"""
Language Detection Service - AI Code Learning Platform

This module provides language detection for code files using:
1. Extension-based detection (primary, fast)
2. Pygments content analysis (fallback for extensionless files)

Reference: spec.md - Code upload requirements
Task: T065 - Implement language detection service using Pygments
"""

from __future__ import annotations

from dataclasses import dataclass

from pygments.lexers import (
    ClassNotFound,
    get_lexer_for_filename,
    guess_lexer,
)
from pygments.util import ClassNotFound as PygmentsClassNotFound


@dataclass
class LanguageInfo:
    """Information about a detected programming language."""

    language: str
    """Normalized language name (e.g., 'Python', 'JavaScript')"""

    confidence: float
    """Detection confidence: 1.0 for extension-based, 0.5-0.9 for content analysis"""

    lexer_name: str
    """Pygments lexer name for syntax highlighting"""

    detection_method: str
    """Method used: 'extension' or 'content_analysis'"""

    @classmethod
    def unknown(cls) -> LanguageInfo:
        """Create an unknown language result."""
        return cls(
            language="Unknown",
            confidence=0.0,
            lexer_name="text",
            detection_method="none",
        )


class LanguageDetector:
    """
    Language detection service using Pygments.

    Supports two detection methods:
    1. Extension-based: Fast, reliable for files with extensions
    2. Content analysis: Uses Pygments heuristics for extensionless files
    """

    # Extension to language mapping with normalized names
    EXTENSION_LANGUAGE_MAP: dict[str, tuple[str, str]] = {
        # Python
        ".py": ("Python", "python"),
        ".pyw": ("Python", "python"),
        ".pyi": ("Python", "python"),
        # JavaScript
        ".js": ("JavaScript", "javascript"),
        ".mjs": ("JavaScript", "javascript"),
        ".cjs": ("JavaScript", "javascript"),
        # TypeScript
        ".ts": ("TypeScript", "typescript"),
        # React JSX/TSX
        ".jsx": ("JavaScript", "jsx"),
        ".tsx": ("TypeScript", "tsx"),
        # Web
        ".html": ("HTML", "html"),
        ".htm": ("HTML", "html"),
        ".css": ("CSS", "css"),
        ".scss": ("SCSS", "scss"),
        ".sass": ("Sass", "sass"),
        ".less": ("Less", "less"),
        # Java
        ".java": ("Java", "java"),
        # C/C++
        ".c": ("C", "c"),
        ".h": ("C", "c"),
        ".cpp": ("C++", "cpp"),
        ".cxx": ("C++", "cpp"),
        ".cc": ("C++", "cpp"),
        ".hpp": ("C++", "cpp"),
        ".hxx": ("C++", "cpp"),
        # C#
        ".cs": ("C#", "csharp"),
        # Go
        ".go": ("Go", "go"),
        # Rust
        ".rs": ("Rust", "rust"),
        # Ruby
        ".rb": ("Ruby", "ruby"),
        # PHP
        ".php": ("PHP", "php"),
        # Swift
        ".swift": ("Swift", "swift"),
        # Kotlin
        ".kt": ("Kotlin", "kotlin"),
        ".kts": ("Kotlin", "kotlin"),
        # Scala
        ".scala": ("Scala", "scala"),
        # Shell
        ".sh": ("Shell", "bash"),
        ".bash": ("Shell", "bash"),
        ".zsh": ("Shell", "zsh"),
        # SQL
        ".sql": ("SQL", "sql"),
        # Config/Data
        ".json": ("JSON", "json"),
        ".yaml": ("YAML", "yaml"),
        ".yml": ("YAML", "yaml"),
        ".xml": ("XML", "xml"),
        ".toml": ("TOML", "toml"),
        # Markdown/Text
        ".md": ("Markdown", "markdown"),
        ".markdown": ("Markdown", "markdown"),
        ".txt": ("Text", "text"),
        ".rst": ("reStructuredText", "rst"),
        # R
        ".r": ("R", "r"),
        ".R": ("R", "r"),
    }

    # Minimum confidence threshold for content-based detection
    MIN_CONTENT_CONFIDENCE: float = 0.3

    @classmethod
    def detect_from_extension(cls, filename: str) -> LanguageInfo | None:
        """
        Detect language from file extension.

        Args:
            filename: The filename to analyze

        Returns:
            LanguageInfo if extension is recognized, None otherwise
        """
        extension = cls._extract_extension(filename)
        if extension is None:
            return None

        ext_lower = extension.lower()
        if ext_lower in cls.EXTENSION_LANGUAGE_MAP:
            language, lexer_name = cls.EXTENSION_LANGUAGE_MAP[ext_lower]
            return LanguageInfo(
                language=language,
                confidence=1.0,
                lexer_name=lexer_name,
                detection_method="extension",
            )

        # Try Pygments for unrecognized extensions
        try:
            lexer = get_lexer_for_filename(filename)
            return LanguageInfo(
                language=cls._normalize_language_name(lexer.name),
                confidence=0.9,
                lexer_name=lexer.aliases[0] if lexer.aliases else lexer.name.lower(),
                detection_method="extension",
            )
        except ClassNotFound:
            return None

    @classmethod
    def detect_from_content(cls, content: str, filename: str = "") -> LanguageInfo:
        """
        Detect language from file content using Pygments heuristics.

        Uses Pygments' guess_lexer which analyzes:
        - Shebang lines (#!/usr/bin/python)
        - Keywords and syntax patterns
        - Common constructs

        Args:
            content: The file content to analyze
            filename: Optional filename for additional hints

        Returns:
            LanguageInfo with detected language and confidence
        """
        if not content or not content.strip():
            return LanguageInfo.unknown()

        try:
            # Try filename hint first if provided
            if filename:
                try:
                    lexer = get_lexer_for_filename(filename, content)
                    return LanguageInfo(
                        language=cls._normalize_language_name(lexer.name),
                        confidence=0.9,
                        lexer_name=(
                            lexer.aliases[0] if lexer.aliases else lexer.name.lower()
                        ),
                        detection_method="content_analysis",
                    )
                except ClassNotFound:
                    pass

            # Try heuristics-based detection first for common languages
            heuristic_result = cls._detect_by_heuristics(content)
            if heuristic_result is not None:
                return heuristic_result

            # Fall back to pure content analysis
            lexer = guess_lexer(content)

            # Calculate confidence based on analysis results
            confidence = cls._calculate_content_confidence(content, lexer)

            if confidence < cls.MIN_CONTENT_CONFIDENCE:
                return LanguageInfo.unknown()

            return LanguageInfo(
                language=cls._normalize_language_name(lexer.name),
                confidence=confidence,
                lexer_name=lexer.aliases[0] if lexer.aliases else lexer.name.lower(),
                detection_method="content_analysis",
            )
        except (ClassNotFound, PygmentsClassNotFound):
            return LanguageInfo.unknown()

    @classmethod
    def detect(cls, filename: str, content: str | None = None) -> LanguageInfo:
        """
        Detect language using best available method.

        Priority:
        1. Extension-based detection (fast, reliable)
        2. Content analysis if extension detection fails and content provided

        Args:
            filename: The filename to analyze
            content: Optional file content for content-based analysis

        Returns:
            LanguageInfo with detected language
        """
        # Try extension-based detection first
        result = cls.detect_from_extension(filename)
        if result is not None:
            return result

        # Fall back to content analysis if available
        if content is not None:
            return cls.detect_from_content(content, filename)

        return LanguageInfo.unknown()

    @classmethod
    def _extract_extension(cls, filename: str) -> str | None:
        """
        Extract file extension from filename.

        Args:
            filename: The filename to extract extension from

        Returns:
            The extension including the dot (e.g., '.py'), or None if no extension
        """
        if "." not in filename:
            return None

        # Handle files like .gitignore (no extension, just dot prefix)
        if filename.startswith(".") and filename.count(".") == 1:
            return None

        return "." + filename.rsplit(".", 1)[-1]

    @classmethod
    def _normalize_language_name(cls, name: str) -> str:
        """
        Normalize Pygments lexer name to standard language name.

        Args:
            name: Pygments lexer name

        Returns:
            Normalized language name
        """
        normalization_map = {
            "Python 3": "Python",
            "Python": "Python",
            "JavaScript": "JavaScript",
            "TypeScript": "TypeScript",
            "HTML": "HTML",
            "CSS": "CSS",
            "Java": "Java",
            "C": "C",
            "C++": "C++",
            "C#": "C#",
            "Go": "Go",
            "Rust": "Rust",
            "Ruby": "Ruby",
            "PHP": "PHP",
            "Swift": "Swift",
            "Kotlin": "Kotlin",
            "Scala": "Scala",
            "Bash": "Shell",
            "Shell": "Shell",
            "SQL": "SQL",
            "JSON": "JSON",
            "YAML": "YAML",
            "XML": "XML",
            "Markdown": "Markdown",
            "Text only": "Text",
        }
        return normalization_map.get(name, name)

    @classmethod
    def _detect_by_heuristics(cls, content: str) -> LanguageInfo | None:
        """
        Detect language using pattern-based heuristics for common languages.

        This method checks for distinctive patterns that uniquely identify
        languages before falling back to Pygments' guess_lexer.

        Args:
            content: The file content to analyze

        Returns:
            LanguageInfo if a language is confidently detected, None otherwise
        """
        import re

        lines = content.split("\n")
        content.lower()

        # Check shebang first
        if lines and lines[0].startswith("#!"):
            shebang = lines[0].lower()
            if "python" in shebang:
                return LanguageInfo(
                    language="Python",
                    confidence=0.95,
                    lexer_name="python",
                    detection_method="content_analysis",
                )
            if "node" in shebang:
                return LanguageInfo(
                    language="JavaScript",
                    confidence=0.95,
                    lexer_name="javascript",
                    detection_method="content_analysis",
                )
            if any(sh in shebang for sh in ["/bash", "/sh", "/zsh"]):
                return LanguageInfo(
                    language="Shell",
                    confidence=0.95,
                    lexer_name="bash",
                    detection_method="content_analysis",
                )

        # Python-specific patterns
        python_patterns = [
            r"\bdef\s+\w+\s*\([^)]*\)\s*(?:->|:)",  # def func(...) -> or :
            r"\bclass\s+\w+\s*(?:\([^)]*\))?\s*:",  # class Name(...)
            r"^\s*import\s+\w+",  # import statement
            r"^\s*from\s+\w+\s+import",  # from x import
            r'if\s+__name__\s*==\s*["\']__main__["\']',  # main guard
            r"self\.\w+",  # self.attribute
            r'""".*?"""',  # docstrings
        ]

        # JavaScript-specific patterns
        js_patterns = [
            r"\bconst\s+\w+\s*=",  # const declaration
            r"\blet\s+\w+\s*=",  # let declaration
            r"\bvar\s+\w+\s*=",  # var declaration
            r"=>\s*[{\(]",  # arrow functions
            r"function\s+\w*\s*\([^)]*\)\s*{",  # function declaration
            r"\bconsole\.(log|error|warn)",  # console methods
            r"\.forEach\s*\(",  # Array methods
            r"\.map\s*\([^)]*=>",  # Array map with arrow
            r"\.reduce\s*\(",  # Array reduce
            r"\.filter\s*\(",  # Array filter
            r'require\s*\(["\']',  # require()
            r"module\.exports",  # CommonJS exports
            r"export\s+(default|const|function|class)",  # ES6 exports
            r'import\s+.*\s+from\s+["\']',  # ES6 imports
        ]

        # TypeScript-specific patterns
        ts_patterns = [
            r":\s*(string|number|boolean|void|any|unknown|never)\b",
            r"interface\s+\w+\s*{",
            r"type\s+\w+\s*=",
            r"<\w+(\s*,\s*\w+)*>",  # Generics
            r"as\s+(string|number|boolean|any)",  # Type assertions
        ]

        # Java-specific patterns
        java_patterns = [
            r"public\s+class\s+\w+",
            r"public\s+static\s+void\s+main",
            r"System\.out\.print",
            r"private\s+(static\s+)?(final\s+)?\w+\s+\w+",
            r"@Override",
            r"package\s+[\w.]+;",
        ]

        # C-specific patterns
        c_patterns = [
            r"#include\s*<\w+\.h>",
            r"int\s+main\s*\([^)]*\)",
            r"printf\s*\(",
            r"malloc\s*\(",
            r"sizeof\s*\(",
        ]

        # C++-specific patterns
        cpp_patterns = [
            r"#include\s*<iostream>",
            r"std::cout",
            r"std::cin",
            r"std::string",
            r"namespace\s+\w+",
            r"template\s*<",
        ]

        # Count pattern matches for each language
        def count_patterns(patterns: list[str]) -> int:
            return sum(1 for p in patterns if re.search(p, content, re.MULTILINE))

        scores = {
            "Python": count_patterns(python_patterns),
            "JavaScript": count_patterns(js_patterns),
            "TypeScript": count_patterns(ts_patterns),
            "Java": count_patterns(java_patterns),
            "C": count_patterns(c_patterns),
            "C++": count_patterns(cpp_patterns),
        }

        # TypeScript score includes JavaScript (superset)
        if scores["TypeScript"] > 0:
            scores["TypeScript"] += scores["JavaScript"]

        # C++ score includes C (superset)
        if scores["C++"] > 0:
            scores["C++"] += scores["C"]

        # Find best match
        best_lang = max(scores, key=scores.get)
        best_score = scores[best_lang]

        # Require minimum matches for confidence
        if best_score >= 3:
            confidence = min(0.5 + (best_score * 0.1), 0.90)

            lexer_map = {
                "Python": "python",
                "JavaScript": "javascript",
                "TypeScript": "typescript",
                "Java": "java",
                "C": "c",
                "C++": "cpp",
            }

            return LanguageInfo(
                language=best_lang,
                confidence=confidence,
                lexer_name=lexer_map.get(best_lang, best_lang.lower()),
                detection_method="content_analysis",
            )

        return None

    @classmethod
    def _calculate_content_confidence(cls, content: str, _lexer) -> float:
        """
        Calculate confidence score for content-based detection.

        Factors considered:
        - Presence of shebang line
        - Number of recognized keywords/patterns
        - File length (longer files = more reliable detection)

        Args:
            content: The analyzed content
            lexer: The detected Pygments lexer

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence for Pygments detection

        lines = content.split("\n")

        # Boost for shebang line
        if lines and lines[0].startswith("#!"):
            shebang = lines[0].lower()
            if (
                "python" in shebang
                or "node" in shebang
                or "javascript" in shebang
                or any(shell in shebang for shell in ["bash", "sh", "zsh"])
            ):
                confidence += 0.3
            else:
                confidence += 0.1

        # Boost for longer files (more content to analyze)
        line_count = len(lines)
        if line_count >= 50:
            confidence += 0.2
        elif line_count >= 20:
            confidence += 0.1
        elif line_count >= 10:
            confidence += 0.05

        # Cap at 0.95 (never fully confident with content analysis)
        return min(confidence, 0.95)

    @classmethod
    def get_supported_languages(cls) -> list[str]:
        """
        Get list of all supported languages.

        Returns:
            Sorted list of supported language names
        """
        languages = {lang for lang, _ in cls.EXTENSION_LANGUAGE_MAP.values()}
        return sorted(languages)

    @classmethod
    def get_extensions_for_language(cls, language: str) -> list[str]:
        """
        Get file extensions associated with a language.

        Args:
            language: Language name (e.g., 'Python')

        Returns:
            List of file extensions for the language
        """
        return [
            ext
            for ext, (lang, _) in cls.EXTENSION_LANGUAGE_MAP.items()
            if lang.lower() == language.lower()
        ]
