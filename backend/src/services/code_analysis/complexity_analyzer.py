"""
Code Complexity Analyzer - AI Code Learning Platform

This module provides complexity analysis for uploaded code files.
The analyzer evaluates code based on multiple metrics and assigns
a complexity level (beginner, intermediate, advanced) to help
generate appropriate learning materials.

Reference: spec.md - Code analysis requirements
Task: T066 - Implement code complexity analyzer
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class ComplexityLevel(str, Enum):
    """Complexity level classification for code."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class MetricScore:
    """Individual metric score with details."""

    name: str
    """Name of the metric"""

    raw_value: int | float
    """Raw measured value"""

    normalized_score: float
    """Normalized score (0-100)"""

    weight: float
    """Weight in overall calculation (0-1)"""

    description: str
    """Human-readable description of what this metric measures"""


@dataclass
class ComplexityMetrics:
    """Detailed metrics collected during code analysis."""

    # Size metrics
    total_lines: int = 0
    code_lines: int = 0  # Non-empty, non-comment lines
    blank_lines: int = 0
    comment_lines: int = 0

    # Structural metrics
    function_count: int = 0
    class_count: int = 0
    method_count: int = 0  # Methods within classes

    # Complexity indicators
    max_nesting_depth: int = 0
    import_count: int = 0
    unique_imports: int = 0

    # Advanced features
    decorator_count: int = 0
    generator_count: int = 0
    comprehension_count: int = 0
    lambda_count: int = 0
    exception_handler_count: int = 0
    async_count: int = 0

    # Calculated averages
    avg_function_length: float = 0.0
    avg_function_params: float = 0.0


@dataclass
class ComplexityResult:
    """Result of complexity analysis."""

    level: ComplexityLevel
    """Overall complexity level classification"""

    total_score: float
    """Total weighted score (0-100)"""

    metrics: ComplexityMetrics
    """Detailed metrics collected"""

    metric_scores: list[MetricScore] = field(default_factory=list)
    """Individual metric scores with breakdown"""

    language: str = "python"
    """Programming language analyzed"""

    analysis_notes: list[str] = field(default_factory=list)
    """Notes about the analysis"""

    @property
    def level_description(self) -> str:
        """Get description for the complexity level."""
        descriptions = {
            ComplexityLevel.BEGINNER: (
                "Basic code structure suitable for beginners. "
                "Simple logic with few functions and no classes."
            ),
            ComplexityLevel.INTERMEDIATE: (
                "Moderate complexity with object-oriented features. "
                "Multiple functions and some design patterns."
            ),
            ComplexityLevel.ADVANCED: (
                "Complex code with advanced patterns. "
                "Heavy OOP, async programming, or sophisticated logic."
            ),
        }
        return descriptions.get(self.level, "")


class ComplexityAnalyzer:
    """
    Analyzes code complexity using multiple metrics.

    The analyzer uses a weighted scoring system that considers:
    - Size metrics (lines of code, functions, classes)
    - Structural complexity (nesting, dependencies)
    - Advanced language features (decorators, generators, async)

    Thresholds for complexity levels:
    - Beginner: score 0-35
    - Intermediate: score 36-65
    - Advanced: score 66-100
    """

    # Scoring thresholds
    BEGINNER_THRESHOLD = 35
    INTERMEDIATE_THRESHOLD = 60  # Score >= 60 = Advanced

    # Metric weights (must sum to 1.0)
    METRIC_WEIGHTS = {
        "lines_of_code": 0.15,
        "function_count": 0.15,
        "class_count": 0.15,
        "method_count": 0.10,
        "nesting_depth": 0.10,
        "import_count": 0.05,
        "advanced_features": 0.15,
        "avg_function_complexity": 0.15,
    }

    # Scoring curves (value -> normalized score 0-100)
    # Format: [(threshold, score), ...] - linear interpolation between points
    SCORING_CURVES = {
        "lines_of_code": [
            (0, 0),
            (30, 15),
            (100, 35),
            (200, 55),
            (500, 80),
            (1000, 100),
        ],
        "function_count": [
            (0, 0),
            (2, 15),
            (5, 30),
            (10, 50),
            (20, 75),
            (50, 100),
        ],
        "class_count": [
            (0, 0),
            (1, 20),
            (3, 45),
            (5, 65),
            (10, 85),
            (20, 100),
        ],
        "method_count": [
            (0, 0),
            (3, 20),
            (10, 40),
            (20, 60),
            (40, 80),
            (100, 100),
        ],
        "nesting_depth": [
            (0, 0),
            (2, 20),
            (3, 40),
            (4, 60),
            (5, 80),
            (7, 100),
        ],
        "import_count": [
            (0, 0),
            (3, 20),
            (5, 35),
            (10, 55),
            (20, 80),
            (50, 100),
        ],
        "advanced_features": [
            (0, 0),
            (2, 25),
            (5, 50),
            (10, 75),
            (20, 100),
        ],
        "avg_function_complexity": [
            (0, 0),
            (10, 20),
            (20, 40),
            (40, 60),
            (80, 80),
            (150, 100),
        ],
    }

    @classmethod
    def analyze(cls, code: str, _filename: str = "") -> ComplexityResult:
        """
        Analyze code complexity and return detailed results.

        Args:
            code: Source code content to analyze
            filename: Optional filename for context

        Returns:
            ComplexityResult with level, score, and detailed metrics
        """
        if not code or not code.strip():
            return ComplexityResult(
                level=ComplexityLevel.BEGINNER,
                total_score=0.0,
                metrics=ComplexityMetrics(),
                analysis_notes=["Empty or whitespace-only code provided"],
            )

        # Collect metrics
        metrics = cls._collect_metrics(code)

        # Calculate individual metric scores
        metric_scores = cls._calculate_metric_scores(metrics)

        # Calculate weighted total score
        total_score = cls._calculate_total_score(metric_scores)

        # Determine complexity level
        level = cls._determine_level(total_score)

        # Generate analysis notes
        notes = cls._generate_analysis_notes(metrics, level)

        return ComplexityResult(
            level=level,
            total_score=total_score,
            metrics=metrics,
            metric_scores=metric_scores,
            language="python",  # Currently only Python supported
            analysis_notes=notes,
        )

    @classmethod
    def analyze_files(cls, files: Sequence[tuple[str, str]]) -> ComplexityResult:
        """
        Analyze multiple code files and return aggregated results.

        Args:
            files: Sequence of (filename, content) tuples

        Returns:
            ComplexityResult with aggregated metrics and scores
        """
        if not files:
            return ComplexityResult(
                level=ComplexityLevel.BEGINNER,
                total_score=0.0,
                metrics=ComplexityMetrics(),
                analysis_notes=["No files provided for analysis"],
            )

        # Analyze each file and aggregate
        all_metrics: list[ComplexityMetrics] = []
        for filename, content in files:
            result = cls.analyze(content, filename)
            all_metrics.append(result.metrics)

        # Aggregate metrics
        aggregated = cls._aggregate_metrics(all_metrics)

        # Recalculate scores with aggregated metrics
        metric_scores = cls._calculate_metric_scores(aggregated)
        total_score = cls._calculate_total_score(metric_scores)
        level = cls._determine_level(total_score)
        notes = cls._generate_analysis_notes(aggregated, level)
        notes.insert(0, f"Analyzed {len(files)} file(s)")

        return ComplexityResult(
            level=level,
            total_score=total_score,
            metrics=aggregated,
            metric_scores=metric_scores,
            language="python",
            analysis_notes=notes,
        )

    @classmethod
    def _collect_metrics(cls, code: str) -> ComplexityMetrics:
        """
        Collect all complexity metrics from code.

        Args:
            code: Source code to analyze

        Returns:
            ComplexityMetrics with all collected values
        """
        metrics = ComplexityMetrics()

        # Line metrics
        lines = code.split("\n")
        metrics.total_lines = len(lines)

        for line in lines:
            stripped = line.strip()
            if not stripped:
                metrics.blank_lines += 1
            elif stripped.startswith("#"):
                metrics.comment_lines += 1
            else:
                metrics.code_lines += 1

        # Parse AST for structural analysis
        try:
            tree = ast.parse(code)
            cls._analyze_ast(tree, metrics)
        except SyntaxError:
            # Fall back to regex-based analysis for invalid Python
            cls._analyze_regex(code, metrics)

        return metrics

    @classmethod
    def _analyze_ast(cls, tree: ast.AST, metrics: ComplexityMetrics) -> None:
        """
        Analyze AST for structural metrics.

        Args:
            tree: Parsed AST
            metrics: Metrics object to update
        """
        function_lengths: list[int] = []
        function_params: list[int] = []

        for node in ast.walk(tree):
            # Count imports
            if isinstance(node, ast.Import):
                metrics.import_count += len(node.names)
                metrics.unique_imports += len(node.names)
            elif isinstance(node, ast.ImportFrom):
                metrics.import_count += 1
                metrics.unique_imports += 1

            # Count functions (top-level and nested)
            elif isinstance(node, ast.FunctionDef):
                if cls._is_method(node, tree):
                    metrics.method_count += 1
                else:
                    metrics.function_count += 1

                # Track function complexity
                func_lines = (
                    node.end_lineno - node.lineno + 1
                    if hasattr(node, "end_lineno")
                    else 0
                )
                function_lengths.append(func_lines)
                function_params.append(len(node.args.args))

                # Count async functions
                if isinstance(node, ast.AsyncFunctionDef):
                    metrics.async_count += 1

            elif isinstance(node, ast.AsyncFunctionDef):
                if cls._is_method(node, tree):
                    metrics.method_count += 1
                else:
                    metrics.function_count += 1
                metrics.async_count += 1

                func_lines = (
                    node.end_lineno - node.lineno + 1
                    if hasattr(node, "end_lineno")
                    else 0
                )
                function_lengths.append(func_lines)
                function_params.append(len(node.args.args))

            # Count classes
            elif isinstance(node, ast.ClassDef):
                metrics.class_count += 1

            # Count decorators
            elif isinstance(
                node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
            ):
                if hasattr(node, "decorator_list"):
                    metrics.decorator_count += len(node.decorator_list)

            # Count advanced features
            elif isinstance(node, ast.Lambda):
                metrics.lambda_count += 1
            elif isinstance(
                node, ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp
            ):
                metrics.comprehension_count += 1
            elif isinstance(node, ast.Yield | ast.YieldFrom):
                metrics.generator_count += 1
            elif isinstance(node, ast.ExceptHandler):
                metrics.exception_handler_count += 1

        # Calculate nesting depth
        metrics.max_nesting_depth = cls._calculate_max_nesting(tree)

        # Calculate averages
        if function_lengths:
            metrics.avg_function_length = sum(function_lengths) / len(function_lengths)
        if function_params:
            metrics.avg_function_params = sum(function_params) / len(function_params)

    @classmethod
    def _is_method(
        cls, node: ast.FunctionDef | ast.AsyncFunctionDef, tree: ast.AST
    ) -> bool:
        """Check if a function is a method within a class."""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                for child in ast.iter_child_nodes(parent):
                    if child is node:
                        return True
        return False

    @classmethod
    def _calculate_max_nesting(cls, tree: ast.AST) -> int:
        """Calculate maximum nesting depth in the code."""
        max_depth = 0

        def walk_with_depth(node: ast.AST, depth: int) -> None:
            nonlocal max_depth
            max_depth = max(max_depth, depth)

            for child in ast.iter_child_nodes(node):
                # Control flow increases nesting
                if isinstance(
                    child,
                    ast.If
                    | ast.For
                    | ast.While
                    | ast.With
                    | ast.Try
                    | ast.FunctionDef
                    | ast.ClassDef,
                ):
                    walk_with_depth(child, depth + 1)
                else:
                    walk_with_depth(child, depth)

        walk_with_depth(tree, 0)
        return max_depth

    @classmethod
    def _analyze_regex(cls, code: str, metrics: ComplexityMetrics) -> None:
        """
        Fallback regex-based analysis for non-parseable code.

        Args:
            code: Source code to analyze
            metrics: Metrics object to update
        """
        # Function definitions
        metrics.function_count = len(
            re.findall(r"^\s*def\s+\w+\s*\(", code, re.MULTILINE)
        )

        # Class definitions
        metrics.class_count = len(re.findall(r"^\s*class\s+\w+", code, re.MULTILINE))

        # Import statements
        metrics.import_count = len(
            re.findall(r"^\s*(import|from)\s+", code, re.MULTILINE)
        )

        # Decorators
        metrics.decorator_count = len(re.findall(r"^\s*@\w+", code, re.MULTILINE))

        # Estimate nesting by indentation
        max_indent = 0
        for line in code.split("\n"):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent // 4)
        metrics.max_nesting_depth = max_indent

    @classmethod
    def _aggregate_metrics(
        cls, metrics_list: list[ComplexityMetrics]
    ) -> ComplexityMetrics:
        """Aggregate metrics from multiple files."""
        if not metrics_list:
            return ComplexityMetrics()

        aggregated = ComplexityMetrics()
        for m in metrics_list:
            aggregated.total_lines += m.total_lines
            aggregated.code_lines += m.code_lines
            aggregated.blank_lines += m.blank_lines
            aggregated.comment_lines += m.comment_lines
            aggregated.function_count += m.function_count
            aggregated.class_count += m.class_count
            aggregated.method_count += m.method_count
            aggregated.max_nesting_depth = max(
                aggregated.max_nesting_depth, m.max_nesting_depth
            )
            aggregated.import_count += m.import_count
            aggregated.unique_imports += m.unique_imports
            aggregated.decorator_count += m.decorator_count
            aggregated.generator_count += m.generator_count
            aggregated.comprehension_count += m.comprehension_count
            aggregated.lambda_count += m.lambda_count
            aggregated.exception_handler_count += m.exception_handler_count
            aggregated.async_count += m.async_count

        # Average the averages (weighted by function count would be better)
        total_functions = sum(m.function_count for m in metrics_list)
        if total_functions > 0:
            aggregated.avg_function_length = (
                sum(m.avg_function_length * m.function_count for m in metrics_list)
                / total_functions
            )
            aggregated.avg_function_params = (
                sum(m.avg_function_params * m.function_count for m in metrics_list)
                / total_functions
            )

        return aggregated

    @classmethod
    def _calculate_metric_scores(cls, metrics: ComplexityMetrics) -> list[MetricScore]:
        """Calculate normalized scores for each metric."""
        scores = []

        # Lines of code score
        scores.append(
            MetricScore(
                name="Lines of Code",
                raw_value=metrics.code_lines,
                normalized_score=cls._interpolate_score(
                    metrics.code_lines, cls.SCORING_CURVES["lines_of_code"]
                ),
                weight=cls.METRIC_WEIGHTS["lines_of_code"],
                description="Total non-empty, non-comment lines",
            )
        )

        # Function count score
        scores.append(
            MetricScore(
                name="Function Count",
                raw_value=metrics.function_count,
                normalized_score=cls._interpolate_score(
                    metrics.function_count, cls.SCORING_CURVES["function_count"]
                ),
                weight=cls.METRIC_WEIGHTS["function_count"],
                description="Number of standalone functions",
            )
        )

        # Class count score
        scores.append(
            MetricScore(
                name="Class Count",
                raw_value=metrics.class_count,
                normalized_score=cls._interpolate_score(
                    metrics.class_count, cls.SCORING_CURVES["class_count"]
                ),
                weight=cls.METRIC_WEIGHTS["class_count"],
                description="Number of class definitions",
            )
        )

        # Method count score
        scores.append(
            MetricScore(
                name="Method Count",
                raw_value=metrics.method_count,
                normalized_score=cls._interpolate_score(
                    metrics.method_count, cls.SCORING_CURVES["method_count"]
                ),
                weight=cls.METRIC_WEIGHTS["method_count"],
                description="Number of methods within classes",
            )
        )

        # Nesting depth score
        scores.append(
            MetricScore(
                name="Max Nesting Depth",
                raw_value=metrics.max_nesting_depth,
                normalized_score=cls._interpolate_score(
                    metrics.max_nesting_depth, cls.SCORING_CURVES["nesting_depth"]
                ),
                weight=cls.METRIC_WEIGHTS["nesting_depth"],
                description="Maximum control flow nesting level",
            )
        )

        # Import count score
        scores.append(
            MetricScore(
                name="Import Count",
                raw_value=metrics.import_count,
                normalized_score=cls._interpolate_score(
                    metrics.import_count, cls.SCORING_CURVES["import_count"]
                ),
                weight=cls.METRIC_WEIGHTS["import_count"],
                description="Number of import statements",
            )
        )

        # Advanced features score (combined)
        advanced_count = (
            metrics.decorator_count
            + metrics.generator_count
            + metrics.comprehension_count
            + metrics.lambda_count
            + metrics.async_count
        )
        scores.append(
            MetricScore(
                name="Advanced Features",
                raw_value=advanced_count,
                normalized_score=cls._interpolate_score(
                    advanced_count, cls.SCORING_CURVES["advanced_features"]
                ),
                weight=cls.METRIC_WEIGHTS["advanced_features"],
                description="Decorators, generators, comprehensions, lambdas, async",
            )
        )

        # Average function complexity
        avg_complexity = metrics.avg_function_length + (metrics.avg_function_params * 5)
        scores.append(
            MetricScore(
                name="Avg Function Complexity",
                raw_value=round(avg_complexity, 1),
                normalized_score=cls._interpolate_score(
                    avg_complexity, cls.SCORING_CURVES["avg_function_complexity"]
                ),
                weight=cls.METRIC_WEIGHTS["avg_function_complexity"],
                description="Average function length + (params * 5)",
            )
        )

        return scores

    @classmethod
    def _interpolate_score(
        cls, value: float, curve: list[tuple[float, float]]
    ) -> float:
        """
        Interpolate a normalized score from a scoring curve.

        Args:
            value: Raw metric value
            curve: List of (threshold, score) tuples

        Returns:
            Interpolated score (0-100)
        """
        if value <= curve[0][0]:
            return curve[0][1]
        if value >= curve[-1][0]:
            return curve[-1][1]

        # Find surrounding points
        for i in range(len(curve) - 1):
            x1, y1 = curve[i]
            x2, y2 = curve[i + 1]
            if x1 <= value <= x2:
                # Linear interpolation
                ratio = (value - x1) / (x2 - x1)
                return y1 + ratio * (y2 - y1)

        return curve[-1][1]

    @classmethod
    def _calculate_total_score(cls, metric_scores: list[MetricScore]) -> float:
        """Calculate weighted total score."""
        total = sum(score.normalized_score * score.weight for score in metric_scores)
        return round(total, 2)

    @classmethod
    def _determine_level(cls, total_score: float) -> ComplexityLevel:
        """Determine complexity level from total score."""
        if total_score <= cls.BEGINNER_THRESHOLD:
            return ComplexityLevel.BEGINNER
        if total_score <= cls.INTERMEDIATE_THRESHOLD:
            return ComplexityLevel.INTERMEDIATE
        return ComplexityLevel.ADVANCED

    @classmethod
    def _generate_analysis_notes(
        cls, metrics: ComplexityMetrics, level: ComplexityLevel
    ) -> list[str]:
        """Generate human-readable analysis notes."""
        notes = []

        # Add observations based on metrics
        if metrics.class_count > 0:
            notes.append(
                f"Uses object-oriented programming with {metrics.class_count} class(es)"
            )

        if metrics.async_count > 0:
            notes.append(f"Contains {metrics.async_count} async function(s)")

        if metrics.decorator_count > 0:
            notes.append(f"Uses {metrics.decorator_count} decorator(s)")

        if metrics.comprehension_count > 0:
            notes.append(
                f"Contains {metrics.comprehension_count} list/dict/set comprehension(s)"
            )

        if metrics.generator_count > 0:
            notes.append(f"Uses {metrics.generator_count} generator expression(s)")

        if metrics.exception_handler_count > 0:
            notes.append(
                f"Implements {metrics.exception_handler_count} exception handler(s)"
            )

        if metrics.max_nesting_depth >= 4:
            notes.append(f"Deep nesting detected (depth: {metrics.max_nesting_depth})")

        if not notes and level == ComplexityLevel.BEGINNER:
            notes.append("Simple procedural code with basic control flow")

        return notes

    @classmethod
    def get_score_breakdown_table(cls, result: ComplexityResult) -> str:
        """
        Generate a formatted table of score breakdown.

        Args:
            result: ComplexityResult to format

        Returns:
            Formatted table string
        """
        lines = [
            "┌─────────────────────────┬───────────┬────────────┬────────┬───────────────┐",
            "│ Metric                  │ Raw Value │ Score(100) │ Weight │ Weighted      │",
            "├─────────────────────────┼───────────┼────────────┼────────┼───────────────┤",
        ]

        for score in result.metric_scores:
            weighted = score.normalized_score * score.weight
            lines.append(
                f"│ {score.name:<23} │ {str(score.raw_value):>9} │ "
                f"{score.normalized_score:>10.1f} │ {score.weight:>6.2f} │ {weighted:>13.2f} │"
            )

        lines.append(
            "├─────────────────────────┴───────────┴────────────┴────────┼───────────────┤"
        )
        lines.append(
            f"│ TOTAL SCORE                                              │ {result.total_score:>13.2f} │"
        )
        lines.append(
            "└──────────────────────────────────────────────────────────┴───────────────┘"
        )
        lines.append(f"Complexity Level: {result.level.value.upper()}")

        return "\n".join(lines)
