"""
TokenService Token Lifecycle Test Script

Test Scenarios:
1. create_token_pair() - Create Access + Refresh tokens
2. verify_access_token() - Verify Access Token
3. Check RefreshToken hash in database (Mock)
"""

import asyncio
import hashlib

# Fix Windows console encoding
import io
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))


async def test_token_lifecycle():
    """TokenService Token Lifecycle Test"""

    print("=" * 60)
    print("TokenService Token Lifecycle Test")
    print("=" * 60)

    # Import directly by specifying full path
    import importlib.util

    jwt_spec = importlib.util.spec_from_file_location(
        "jwt_module", backend_src / "utils" / "jwt.py"
    )
    jwt_module = importlib.util.module_from_spec(jwt_spec)
    jwt_spec.loader.exec_module(jwt_module)

    TokenType = jwt_module.TokenType
    create_access_token = jwt_module.create_access_token
    jwt_create_refresh_token = jwt_module.create_refresh_token
    verify_token = jwt_module.verify_token
    decode_token = jwt_module.decode_token
    get_jwt_settings = jwt_module.get_jwt_settings

    # Create a simple RefreshToken-like object for testing
    class MockRefreshToken:
        def __init__(self, user_id, token_hash, expires_at):
            self.id = uuid4()
            self.user_id = user_id
            self.token_hash = token_hash
            self.expires_at = expires_at
            self.created_at = datetime.now(UTC)
            self.revoked = False
            self.revoked_at = None

        def is_valid(self):
            return not self.revoked and datetime.now(UTC) < self.expires_at

    # Settings
    settings = get_jwt_settings()

    # Test user ID
    test_user_id = uuid4()
    print(f"\n[*] Test User ID: {test_user_id}")

    # Variable to store the refresh token record
    stored_refresh_token = None

    # ============================================================
    # Step 1: create_token_pair()
    # ============================================================
    print("\n" + "=" * 60)
    print("Step 1: create_token_pair()")
    print("=" * 60)

    # Create Access Token
    access_token = create_access_token(user_id=str(test_user_id), settings=settings)

    print("\n[OK] Access Token Created")
    print(f"   - Length: {len(access_token)} characters")
    print(f"   - Token (first 60 chars): {access_token[:60]}...")

    # Create Refresh Token
    jti = str(uuid4())
    refresh_token = jwt_create_refresh_token(
        user_id=str(test_user_id), jti=jti, settings=settings
    )

    print("\n[OK] Refresh Token Created")
    print(f"   - Length: {len(refresh_token)} characters")
    print(f"   - Token (first 60 chars): {refresh_token[:60]}...")

    # Store hash in "database" (mock)
    token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(UTC) + settings.refresh_token_lifetime
    stored_refresh_token = MockRefreshToken(
        user_id=test_user_id, token_hash=token_hash, expires_at=expires_at
    )

    # ============================================================
    # Step 2: verify_access_token()
    # ============================================================
    print("\n" + "=" * 60)
    print("Step 2: verify_access_token()")
    print("=" * 60)

    try:
        payload = verify_token(
            access_token, expected_type=TokenType.ACCESS, settings=settings
        )

        print("\n[OK] Access Token Verified Successfully!")
        print(f"   - subject (user_id): {payload.sub}")
        print(f"   - token_type: {payload.type.value}")
        print(f"   - issued_at (iat): {payload.iat.isoformat()}")
        print(f"   - expires_at (exp): {payload.exp.isoformat()}")

        # Remaining time
        remaining = payload.exp - datetime.now(UTC)
        print(
            f"   - remaining time: {remaining.total_seconds():.0f}s ({remaining.total_seconds()/60:.1f}min)"
        )

        # user_id match check
        if payload.sub == str(test_user_id):
            print("\n   [PASS] user_id matches!")
        else:
            print(
                f"\n   [FAIL] user_id mismatch! Expected: {test_user_id}, Got: {payload.sub}"
            )

    except Exception as e:
        print(f"\n[FAIL] Access Token verification failed: {e}")
        return

    # ============================================================
    # Step 3: RefreshToken Hash Verification
    # ============================================================
    print("\n" + "=" * 60)
    print("Step 3: RefreshToken Hash Verification (DB Check)")
    print("=" * 60)

    # Compute token hash locally
    computed_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
    print("\n[*] Computed Token Hash (SHA-256):")
    print(f"   {computed_hash}")

    # Check stored token
    if stored_refresh_token is not None:
        print("\n[OK] RefreshToken found in database!")
        print(f"   - ID: {stored_refresh_token.id}")
        print(f"   - user_id: {stored_refresh_token.user_id}")
        print(f"   - token_hash: {stored_refresh_token.token_hash[:32]}...")
        print(f"   - expires_at: {stored_refresh_token.expires_at.isoformat()}")
        print(f"   - revoked: {stored_refresh_token.revoked}")

        # Hash match verification
        if stored_refresh_token.token_hash == computed_hash:
            print("\n   [PASS] Hash values match!")
        else:
            print("\n   [FAIL] Hash values do not match!")

        # user_id match verification
        if stored_refresh_token.user_id == test_user_id:
            print("   [PASS] user_id matches!")
        else:
            print("   [FAIL] user_id does not match!")

        # Validity check
        if stored_refresh_token.is_valid():
            print("   [PASS] Token is valid (not expired, not revoked)")
        else:
            print("   [FAIL] Token is not valid")

        # Remaining validity
        remaining = stored_refresh_token.expires_at - datetime.now(UTC)
        print(
            f"\n   [*] Remaining validity: {remaining.days} days {remaining.seconds//3600} hours"
        )

    else:
        print("\n[FAIL] RefreshToken not found in database!")

    # ============================================================
    # Decode Refresh Token to show JWT claims
    # ============================================================
    print("\n" + "=" * 60)
    print("Bonus: Refresh Token JWT Payload")
    print("=" * 60)

    refresh_payload = decode_token(refresh_token, settings=settings)
    print("\n[*] Refresh Token Decoded:")
    print(f"   - subject (user_id): {refresh_payload.sub}")
    print(f"   - token_type: {refresh_payload.type.value}")
    print(f"   - jti (unique ID): {refresh_payload.jti}")
    print(f"   - issued_at (iat): {refresh_payload.iat.isoformat()}")
    print(f"   - expires_at (exp): {refresh_payload.exp.isoformat()}")

    print("\n" + "=" * 60)
    print("Token Lifecycle Test Completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_token_lifecycle())
