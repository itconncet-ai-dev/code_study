"""
Token Service - AI Code Learning Platform

This module provides the TokenService for JWT token management,
including access token creation, refresh token management with
database storage, token verification, and token rotation.

Features:
- Access token creation (short-lived, 15 minutes)
- Refresh token creation with SHA-256 hash storage in database
- Token verification with database validation
- Token rotation (issue new, revoke old)
- Token revocation for logout support
- Bulk revocation for all user tokens

Usage:
    from src.services.auth.token_service import TokenService

    # In FastAPI endpoint with dependency injection
    async def login(
        request: LoginRequest,
        db: AsyncSession = Depends(get_db)
    ):
        # After validating credentials...
        token_service = TokenService(db)
        access_token, refresh_token = await token_service.create_token_pair(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token}

Reference: data-model.md §RefreshToken entity
Task: T026 - Implement TokenService (create access/refresh tokens, verify, rotate)
"""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import TokenExpiredError, TokenInvalidError
from src.models.refresh_token import RefreshToken
from src.utils.jwt import (
    TokenPayload,
    TokenType,
    create_access_token as jwt_create_access_token,
    create_refresh_token as jwt_create_refresh_token,
    decode_token,
    get_jwt_settings,
    verify_token,
)
from src.utils.jwt import (
    TokenExpiredError as JWTTokenExpiredError,
    TokenInvalidError as JWTTokenInvalidError,
)


class TokenService:
    """
    Service class for JWT token management.

    Handles access token creation, refresh token lifecycle management,
    token verification, and token rotation with database persistence.

    Attributes:
        db: AsyncSession for database operations
        settings: JWT settings for token configuration

    Example:
        service = TokenService(db_session)
        access, refresh = await service.create_token_pair(user_id)
        new_access, new_refresh = await service.rotate_tokens(refresh)
        await service.revoke_refresh_token(refresh)

    Security Notes:
        - Refresh tokens are stored as SHA-256 hashes (never plaintext)
        - Tokens are rotated on use (old revoked, new issued)
        - All user tokens can be revoked on logout or security events
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize TokenService with database session.

        Args:
            db: SQLAlchemy AsyncSession for database operations
        """
        self.db = db
        self.settings = get_jwt_settings()

    def create_access_token(
        self,
        user_id: UUID | str,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a short-lived access token for API authentication.

        Access tokens are used for authenticating API requests.
        They are not stored in the database (stateless).

        Args:
            user_id: The user's unique identifier (UUID or string)
            extra_claims: Optional additional claims to include

        Returns:
            str: Encoded JWT access token

        Example:
            token = service.create_access_token(user_id)
        """
        return jwt_create_access_token(
            user_id=str(user_id),
            extra_claims=extra_claims,
            settings=self.settings,
        )

    def verify_access_token(self, token: str) -> TokenPayload:
        """
        Verify an access token and return its payload.

        Validates the token signature, expiration, and type.

        Args:
            token: The JWT access token to verify

        Returns:
            TokenPayload: The decoded and validated token payload

        Raises:
            TokenExpiredError: If the token has expired
            TokenInvalidError: If the token is invalid or wrong type

        Example:
            payload = service.verify_access_token(token)
            user_id = payload.sub
        """
        try:
            return verify_token(
                token,
                expected_type=TokenType.ACCESS,
                settings=self.settings,
            )
        except JWTTokenExpiredError as e:
            raise TokenExpiredError(detail="Access token has expired") from e
        except JWTTokenInvalidError as e:
            raise TokenInvalidError(detail=str(e)) from e

    async def create_refresh_token(self, user_id: UUID | str) -> str:
        """
        Create a long-lived refresh token and store its hash in database.

        Refresh tokens are used to obtain new access tokens without
        re-authentication. The SHA-256 hash is stored in the database
        for revocation support.

        Args:
            user_id: The user's unique identifier

        Returns:
            str: Encoded JWT refresh token

        Example:
            refresh_token = await service.create_refresh_token(user_id)

        Database Storage:
            - token_hash: SHA-256 hash of the token
            - user_id: Owner of the token
            - expires_at: Token expiration timestamp
            - revoked: False (not revoked initially)
        """
        # Generate unique token ID for tracking
        jti = str(uuid.uuid4())

        # Create the JWT refresh token
        token = jwt_create_refresh_token(
            user_id=str(user_id),
            jti=jti,
            settings=self.settings,
        )

        # Compute SHA-256 hash of the token (never store plaintext)
        token_hash = self._hash_token(token)

        # Calculate expiration timestamp
        expires_at = datetime.now(timezone.utc) + self.settings.refresh_token_lifetime

        # Create database record
        refresh_token_record = RefreshToken(
            user_id=UUID(str(user_id)) if isinstance(user_id, str) else user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False,
        )

        # Persist to database
        self.db.add(refresh_token_record)
        await self.db.commit()

        return token

    async def verify_refresh_token(self, token: str) -> TokenPayload:
        """
        Verify a refresh token and check database validity.

        Validates the JWT signature, expiration, type, and checks
        that the token exists in the database and is not revoked.

        Args:
            token: The JWT refresh token to verify

        Returns:
            TokenPayload: The decoded and validated token payload

        Raises:
            TokenExpiredError: If the token has expired
            TokenInvalidError: If the token is invalid, revoked, or not found

        Example:
            payload = await service.verify_refresh_token(token)
            user_id = payload.sub
        """
        # First, verify JWT signature and type
        try:
            payload = verify_token(
                token,
                expected_type=TokenType.REFRESH,
                settings=self.settings,
            )
        except JWTTokenExpiredError as e:
            raise TokenExpiredError(detail="Refresh token has expired") from e
        except JWTTokenInvalidError as e:
            raise TokenInvalidError(detail=str(e)) from e

        # Look up token in database by hash
        token_hash = self._hash_token(token)
        stored_token = await self._get_token_by_hash(token_hash)

        if stored_token is None:
            raise TokenInvalidError(detail="Refresh token not found")

        if stored_token.revoked:
            raise TokenInvalidError(detail="Refresh token has been revoked")

        if stored_token.is_expired():
            raise TokenExpiredError(detail="Refresh token has expired")

        return payload

    async def rotate_tokens(
        self,
        refresh_token: str,
    ) -> tuple[str, str]:
        """
        Rotate tokens: verify old refresh token, revoke it, issue new pair.

        This implements the recommended security practice of token rotation.
        Each refresh token can only be used once.

        Args:
            refresh_token: The current refresh token to rotate

        Returns:
            tuple[str, str]: New (access_token, refresh_token) pair

        Raises:
            TokenExpiredError: If the refresh token has expired
            TokenInvalidError: If the refresh token is invalid or revoked

        Example:
            new_access, new_refresh = await service.rotate_tokens(old_refresh)
        """
        # Verify the old refresh token
        payload = await self.verify_refresh_token(refresh_token)
        user_id = UUID(payload.sub)

        # Get the stored token record
        token_hash = self._hash_token(refresh_token)
        stored_token = await self._get_token_by_hash(token_hash)

        if stored_token is None:
            raise TokenInvalidError(detail="Refresh token not found")

        # Revoke the old token
        stored_token.revoked = True
        stored_token.revoked_at = datetime.now(timezone.utc)

        # Create new token pair
        new_access_token = self.create_access_token(user_id)
        new_refresh_token = await self.create_refresh_token(user_id)

        await self.db.commit()

        return new_access_token, new_refresh_token

    async def revoke_refresh_token(self, token: str) -> bool:
        """
        Revoke a refresh token (used for logout).

        Marks the token as revoked in the database so it can no longer
        be used to obtain new access tokens.

        Args:
            token: The refresh token to revoke

        Returns:
            bool: True if token was found and revoked, False if not found

        Example:
            success = await service.revoke_refresh_token(refresh_token)
        """
        try:
            # Decode token to validate format (don't need full verification)
            decode_token(token, verify_signature=True, settings=self.settings)
        except (JWTTokenExpiredError, JWTTokenInvalidError):
            # Even if JWT is invalid/expired, we should still try to revoke
            # in case it's somehow in the database
            pass

        # Look up token in database
        token_hash = self._hash_token(token)
        stored_token = await self._get_token_by_hash(token_hash)

        if stored_token is None:
            return False

        # Mark as revoked
        stored_token.revoked = True
        stored_token.revoked_at = datetime.now(timezone.utc)
        await self.db.commit()

        return True

    async def revoke_all_user_tokens(self, user_id: UUID | str) -> int:
        """
        Revoke all refresh tokens for a user.

        Used for security events like password change or account compromise.
        Marks all non-revoked tokens as revoked.

        Args:
            user_id: The user's unique identifier

        Returns:
            int: Number of tokens revoked

        Example:
            count = await service.revoke_all_user_tokens(user_id)
        """
        user_uuid = UUID(str(user_id)) if isinstance(user_id, str) else user_id
        now = datetime.now(timezone.utc)

        # Update all non-revoked tokens for the user
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_uuid)
            .where(RefreshToken.revoked == False)  # noqa: E712
            .values(revoked=True, revoked_at=now)
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount  # type: ignore

    async def create_token_pair(
        self,
        user_id: UUID | str,
        extra_claims: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        """
        Create both access and refresh tokens for a user.

        Convenience method for creating the token pair needed after
        successful authentication (login or registration).

        Args:
            user_id: The user's unique identifier
            extra_claims: Optional additional claims for access token

        Returns:
            tuple[str, str]: (access_token, refresh_token) pair

        Example:
            access, refresh = await service.create_token_pair(user_id)
        """
        access_token = self.create_access_token(user_id, extra_claims)
        refresh_token = await self.create_refresh_token(user_id)
        return access_token, refresh_token

    def _hash_token(self, token: str) -> str:
        """
        Compute SHA-256 hash of a token.

        Used for securely storing refresh tokens in the database.
        SHA-256 is used instead of bcrypt for tokens because:
        1. Tokens are already high-entropy random values
        2. SHA-256 is faster (tokens checked frequently)
        3. bcrypt is overkill for random tokens (bcrypt protects against
           dictionary attacks, which don't apply to random tokens)

        Args:
            token: The token string to hash

        Returns:
            str: Hexadecimal SHA-256 hash
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def _get_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        """
        Look up a refresh token by its hash.

        Args:
            token_hash: SHA-256 hash of the token

        Returns:
            RefreshToken | None: The token record if found, None otherwise
        """
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
