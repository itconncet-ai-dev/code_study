"""
Code Upload Service - AI Code Learning Platform

This module provides the CodeUploadService for handling code file uploads.
Supports three upload methods: file, folder, and paste.

Features:
- Validate and process uploaded files
- Detect programming language
- Analyze code complexity
- Store files in filesystem
- Create UploadedCode and CodeFile database records

Usage:
    from src.services.code_analysis.code_upload_service import CodeUploadService

    # File upload
    service = CodeUploadService(db)
    uploaded_code = await service.handle_file_upload(
        task_id=task.id,
        user_id=user.id,
        files=[("main.py", b"print('hello')")]
    )

    # Paste upload
    uploaded_code = await service.handle_paste_upload(
        task_id=task.id,
        user_id=user.id,
        code_text="print('hello')",
        language="python"
    )

Reference: spec.md - Code upload requirements
Task: T069 - Implement CodeUploadService
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import ValidationError
from src.models.code_file import CodeFile
from src.models.uploaded_code import UploadedCode
from src.services.code_analysis.complexity_analyzer import ComplexityAnalyzer
from src.services.code_analysis.file_storage import FileStorageService
from src.services.code_analysis.language_detector import LanguageDetector
from src.utils.file_validator import FileValidator

if TYPE_CHECKING:
    pass


class CodeUploadService:
    """
    Service for handling code upload operations.

    Handles three upload methods:
    1. File upload - Single or multiple files
    2. Folder upload - Multiple files with directory structure
    3. Paste upload - Direct code text input

    All uploads are validated, analyzed, and stored with metadata.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize CodeUploadService with database session.

        Args:
            db: SQLAlchemy AsyncSession for database operations
        """
        self.db = db

    async def handle_file_upload(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        files: list[tuple[str, bytes]],
    ) -> UploadedCode:
        """
        Handle file upload method.

        Validates files, detects language, analyzes complexity, and stores files.

        Args:
            task_id: UUID of the parent task
            user_id: UUID of the user
            files: List of (filename, content) tuples

        Returns:
            UploadedCode: Created uploaded code record with files

        Raises:
            ValidationError: If validation fails (size, extension, binary, count)

        Example:
            uploaded_code = await service.handle_file_upload(
                task_id=task.id,
                user_id=user.id,
                files=[("main.py", b"print('hello')"), ("utils.py", b"def helper(): pass")]
            )
        """
        # Validate files
        validation_result = FileValidator.validate_upload(
            [(name, len(content), content) for name, content in files]
        )
        if not validation_result.is_valid:
            raise ValidationError(
                detail=validation_result.error_message or "File validation failed",
                field="files",
            )

        # Calculate total size
        total_size_bytes = sum(len(content) for _, content in files)

        # Detect language from first file
        first_filename, first_content = files[0]
        language_info = LanguageDetector.detect(
            first_filename,
            first_content.decode("utf-8", errors="ignore"),
        )

        # Analyze complexity
        file_contents = [
            (name, content.decode("utf-8", errors="ignore"))
            for name, content in files
        ]
        complexity_result = ComplexityAnalyzer.analyze_files(file_contents)

        # Count total lines
        total_lines = sum(
            len(content.decode("utf-8", errors="ignore").split("\n"))
            for _, content in files
        )

        # Create UploadedCode record
        uploaded_code = UploadedCode(
            task_id=task_id,
            detected_language=language_info.language,
            complexity_level=complexity_result.level.value,
            total_lines=total_lines,
            total_files=len(files),
            upload_size_bytes=total_size_bytes,
        )

        self.db.add(uploaded_code)
        await self.db.flush()  # Get uploaded_code.id

        # Save files and create CodeFile records
        for filename, content in files:
            # Save file to storage
            storage_path = await FileStorageService.save_file(
                content=content,
                user_id=user_id,
                task_id=task_id,
                filename=filename,
            )

            # Get file extension and MIME type
            extension = FileValidator.extract_extension(filename)
            mime_type = FileValidator.get_mime_type(extension) if extension else None

            # Create CodeFile record
            code_file = CodeFile(
                uploaded_code_id=uploaded_code.id,
                file_name=filename,
                file_path=filename,  # For single files, path = name
                file_extension=extension,
                file_size_bytes=len(content),
                storage_path=storage_path,
                mime_type=mime_type,
                content=content.decode("utf-8", errors="replace"),
            )

            self.db.add(code_file)

        await self.db.commit()
        await self.db.refresh(uploaded_code)

        return uploaded_code

    async def handle_folder_upload(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        files: list[tuple[str, bytes]],
    ) -> UploadedCode:
        """
        Handle folder upload method.

        Similar to file upload but preserves directory structure in file_path.

        Args:
            task_id: UUID of the parent task
            user_id: UUID of the user
            files: List of (file_path, content) tuples with relative paths

        Returns:
            UploadedCode: Created uploaded code record with files

        Raises:
            ValidationError: If validation fails

        Example:
            uploaded_code = await service.handle_folder_upload(
                task_id=task.id,
                user_id=user.id,
                files=[
                    ("src/main.py", b"print('hello')"),
                    ("src/utils/helper.py", b"def helper(): pass")
                ]
            )
        """
        # Validate files
        validation_result = FileValidator.validate_upload(
            [(name, len(content), content) for name, content in files]
        )
        if not validation_result.is_valid:
            raise ValidationError(
                detail=validation_result.error_message or "File validation failed",
                field="files",
            )

        # Calculate total size
        total_size_bytes = sum(len(content) for _, content in files)

        # Detect language from first file
        first_file_path, first_content = files[0]
        # Extract just filename for language detection
        first_filename = first_file_path.split("/")[-1]
        language_info = LanguageDetector.detect(
            first_filename,
            first_content.decode("utf-8", errors="ignore"),
        )

        # Analyze complexity
        file_contents = [
            (path, content.decode("utf-8", errors="ignore"))
            for path, content in files
        ]
        complexity_result = ComplexityAnalyzer.analyze_files(file_contents)

        # Count total lines
        total_lines = sum(
            len(content.decode("utf-8", errors="ignore").split("\n"))
            for _, content in files
        )

        # Create UploadedCode record
        uploaded_code = UploadedCode(
            task_id=task_id,
            detected_language=language_info.language,
            complexity_level=complexity_result.level.value,
            total_lines=total_lines,
            total_files=len(files),
            upload_size_bytes=total_size_bytes,
        )

        self.db.add(uploaded_code)
        await self.db.flush()  # Get uploaded_code.id

        # Save files and create CodeFile records
        for file_path, content in files:
            # Extract filename from path
            filename = file_path.split("/")[-1]

            # Save file to storage
            storage_path = await FileStorageService.save_file(
                content=content,
                user_id=user_id,
                task_id=task_id,
                filename=filename,
            )

            # Get file extension and MIME type
            extension = FileValidator.extract_extension(filename)
            mime_type = FileValidator.get_mime_type(extension) if extension else None

            # Create CodeFile record
            code_file = CodeFile(
                uploaded_code_id=uploaded_code.id,
                file_name=filename,
                file_path=file_path,  # Preserve full relative path
                file_extension=extension,
                file_size_bytes=len(content),
                storage_path=storage_path,
                mime_type=mime_type,
                content=content.decode("utf-8", errors="replace"),
            )

            self.db.add(code_file)

        await self.db.commit()
        await self.db.refresh(uploaded_code)

        return uploaded_code

    async def handle_paste_upload(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        code_text: str,
        language: str | None = None,
    ) -> UploadedCode:
        """
        Handle paste upload method.

        Creates a single virtual file from pasted code text.

        Args:
            task_id: UUID of the parent task
            user_id: UUID of the user
            code_text: Pasted code content
            language: Optional language hint (e.g., 'python', 'javascript')

        Returns:
            UploadedCode: Created uploaded code record

        Raises:
            ValidationError: If code_text is empty or too large

        Example:
            uploaded_code = await service.handle_paste_upload(
                task_id=task.id,
                user_id=user.id,
                code_text="print('hello world')",
                language="python"
            )
        """
        # Validate code text
        if not code_text or not code_text.strip():
            raise ValidationError(
                detail="Code text cannot be empty",
                field="code_text",
            )

        # Convert to bytes for size checking
        content_bytes = code_text.encode("utf-8")
        total_size_bytes = len(content_bytes)

        # Validate size
        size_result = FileValidator.validate_total_upload_size(total_size_bytes)
        if not size_result.is_valid:
            raise ValidationError(
                detail=size_result.error_message or "Upload size exceeds limit",
                field="code_text",
            )

        # Detect language
        if language:
            # Use provided language hint
            detected_language = language.capitalize()
        else:
            # Detect from content
            language_info = LanguageDetector.detect_from_content(code_text)
            detected_language = language_info.language

        # Analyze complexity
        complexity_result = ComplexityAnalyzer.analyze(code_text)

        # Count lines
        total_lines = len(code_text.split("\n"))

        # Create UploadedCode record
        uploaded_code = UploadedCode(
            task_id=task_id,
            detected_language=detected_language,
            complexity_level=complexity_result.level.value,
            total_lines=total_lines,
            total_files=1,
            upload_size_bytes=total_size_bytes,
        )

        self.db.add(uploaded_code)
        await self.db.flush()  # Get uploaded_code.id

        # Determine file extension from detected language
        extension_map = {
            "Python": ".py",
            "JavaScript": ".js",
            "TypeScript": ".ts",
            "Java": ".java",
            "C++": ".cpp",
            "C": ".c",
            "HTML": ".html",
            "CSS": ".css",
        }
        extension = extension_map.get(detected_language, ".txt")

        # Create virtual filename
        filename = f"pasted_code{extension}"

        # Save file to storage
        storage_path = await FileStorageService.save_file(
            content=content_bytes,
            user_id=user_id,
            task_id=task_id,
            filename=filename,
        )

        # Get MIME type
        mime_type = FileValidator.get_mime_type(extension)

        # Create CodeFile record
        code_file = CodeFile(
            uploaded_code_id=uploaded_code.id,
            file_name=filename,
            file_path=filename,
            file_extension=extension,
            file_size_bytes=total_size_bytes,
            storage_path=storage_path,
            mime_type=mime_type,
            content=code_text,
        )

        self.db.add(code_file)

        await self.db.commit()
        await self.db.refresh(uploaded_code)

        return uploaded_code


__all__ = ["CodeUploadService"]
