"""
Prompt Templates for AI Content Generation - AI Code Learning Platform

This module provides structured prompt templates for generating educational content
using LLM APIs (Gemini, OpenRouter). All prompts are designed for complete beginners
with zero programming knowledge.

Features:
- 7-chapter learning document generation prompts
- System instructions for educational AI persona
- JSON schema definitions for structured output
- Response validation helpers
- Template composition utilities

Usage:
    from src.services.ai.prompts import (
        DocumentPrompts,
        get_document_generation_prompt,
        get_system_instruction,
        DOCUMENT_RESPONSE_SCHEMA,
    )

    # Generate full document
    system_instruction = get_system_instruction()
    prompt = get_document_generation_prompt(code, language, file_info)

Reference: spec.md FR-026 through FR-039 (Learning Document Generation)
Reference: data-model.md LearningDocument JSONB structure
Task: T092 - Implement prompt templates for 7-chapter document generation
"""

from dataclasses import dataclass
from typing import Any

# ============================================================================
# SYSTEM INSTRUCTIONS
# ============================================================================

EDUCATIONAL_SYSTEM_INSTRUCTION = """You are an expert programming teacher who specializes in explaining code to complete beginners who have ZERO programming experience.

Your teaching philosophy:
1. NEVER assume any prior knowledge - explain everything from scratch
2. Use everyday language - avoid jargon and technical terms unless you explain them first
3. Always provide real-life analogies to make abstract concepts relatable
4. Be patient, encouraging, and thorough in your explanations
5. Make learning fun and accessible

Target audience: People who have never written a single line of code but want to understand AI-generated code.

Critical rules:
- Every technical term must be explained in simple language
- Every abstract concept must have a real-life analogy
- Code examples should be minimal and focused
- Explanations should flow naturally, like a friendly conversation
- Never say "it's easy" or "simply do X" - respect that everything is new to beginners"""


KOREAN_EDUCATIONAL_SYSTEM_INSTRUCTION = """You are an expert programming teacher who specializes in explaining code to complete beginners who have ZERO programming experience.

Your teaching philosophy:
1. NEVER assume any prior knowledge - explain everything from scratch
2. Use everyday Korean language - avoid jargon and technical terms unless you explain them first
3. Always provide real-life analogies to make abstract concepts relatable
4. Be patient, encouraging, and thorough in your explanations
5. Make learning fun and accessible

Target audience: Korean speakers who have never written a single line of code but want to understand AI-generated code.

Critical rules:
- Every technical term must be explained in simple Korean language
- Every abstract concept must have a real-life analogy that Koreans can relate to
- Code examples should be minimal and focused
- Explanations should flow naturally, like a friendly Korean conversation
- Never say "쉬워요" or "그냥 하면 돼요" - respect that everything is new to beginners
- Use polite but friendly Korean (존댓말 but approachable)"""


# ============================================================================
# JSON SCHEMAS FOR STRUCTURED OUTPUT
# ============================================================================

CHAPTER1_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
    },
    "required": ["title", "summary"],
}

CHAPTER2_CONCEPT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "explanation": {"type": "string"},
        "analogy": {"type": "string"},
        "example": {"type": "string"},
        "use_cases": {"type": "string"},
    },
    "required": ["name", "explanation", "analogy", "example", "use_cases"],
}

CHAPTER2_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "concepts": {
            "type": "array",
            "items": CHAPTER2_CONCEPT_SCHEMA,
            "maxItems": 5,
        },
    },
    "required": ["title", "concepts"],
}

CHAPTER3_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "flowchart": {"type": "string"},
        "file_breakdown": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
    },
    "required": ["title", "flowchart", "file_breakdown"],
}

CHAPTER4_LINE_SCHEMA = {
    "type": "object",
    "properties": {
        "line_number": {"type": "integer"},
        "code": {"type": "string"},
        "what_it_does": {"type": "string"},
        "syntax_breakdown": {"type": "string"},
        "analogy": {"type": "string"},
        "alternatives": {"type": "string"},
        "important_notes": {"type": "string"},
    },
    "required": ["line_number", "code", "what_it_does", "syntax_breakdown"],
}

CHAPTER4_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "explanations": {
            "type": "array",
            "items": CHAPTER4_LINE_SCHEMA,
        },
    },
    "required": ["title", "explanations"],
}

CHAPTER5_STEP_SCHEMA = {
    "type": "object",
    "properties": {
        "step_number": {"type": "integer"},
        "action": {"type": "string"},
        "data_state": {"type": "string"},
        "explanation": {"type": "string"},
    },
    "required": ["step_number", "action", "data_state", "explanation"],
}

CHAPTER5_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "steps": {
            "type": "array",
            "items": CHAPTER5_STEP_SCHEMA,
        },
    },
    "required": ["title", "steps"],
}

CHAPTER6_CONCEPT_SCHEMA = {
    "type": "object",
    "properties": {
        "concept_name": {"type": "string"},
        "what_it_is": {"type": "string"},
        "why_used": {"type": "string"},
        "where_applied": {"type": "string"},
    },
    "required": ["concept_name", "what_it_is", "why_used", "where_applied"],
}

CHAPTER6_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "concepts": {
            "type": "array",
            "items": CHAPTER6_CONCEPT_SCHEMA,
        },
    },
    "required": ["title", "concepts"],
}

CHAPTER7_MISTAKE_SCHEMA = {
    "type": "object",
    "properties": {
        "mistake_title": {"type": "string"},
        "wrong_code": {"type": "string"},
        "right_code": {"type": "string"},
        "why_it_matters": {"type": "string"},
        "how_to_fix": {"type": "string"},
    },
    "required": [
        "mistake_title",
        "wrong_code",
        "right_code",
        "why_it_matters",
        "how_to_fix",
    ],
}

CHAPTER7_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "mistakes": {
            "type": "array",
            "items": CHAPTER7_MISTAKE_SCHEMA,
            "minItems": 3,
            "maxItems": 5,
        },
    },
    "required": ["title", "mistakes"],
}

# Full document schema combining all chapters
DOCUMENT_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "chapter1": CHAPTER1_SCHEMA,
        "chapter2": CHAPTER2_SCHEMA,
        "chapter3": CHAPTER3_SCHEMA,
        "chapter4": CHAPTER4_SCHEMA,
        "chapter5": CHAPTER5_SCHEMA,
        "chapter6": CHAPTER6_SCHEMA,
        "chapter7": CHAPTER7_SCHEMA,
    },
    "required": [
        "chapter1",
        "chapter2",
        "chapter3",
        "chapter4",
        "chapter5",
        "chapter6",
        "chapter7",
    ],
}


# ============================================================================
# PROMPT TEMPLATES
# ============================================================================


@dataclass
class FileInfo:
    """Information about an uploaded code file."""

    file_name: str
    file_path: str | None
    content: str
    language: str


class DocumentPrompts:
    """
    Prompt templates for 7-chapter learning document generation.

    Each chapter has a specific purpose aligned with spec.md requirements:
    - Chapter 1: One-sentence summary (FR-027)
    - Chapter 2: Prerequisites with concept cards (FR-028, FR-029)
    - Chapter 3: Code structure overview (FR-030)
    - Chapter 4: Line-by-line explanation (FR-031)
    - Chapter 5: Execution flow simulation (FR-032)
    - Chapter 6: Core concepts summary (FR-033)
    - Chapter 7: Common mistakes (FR-034)
    """

    @staticmethod
    def get_chapter1_prompt(code: str, language: str) -> str:
        """
        Generate prompt for Chapter 1: What This Code Does.

        Produces a one-sentence plain language summary without jargon.

        Args:
            code: The source code to explain
            language: Programming language (e.g., "python", "javascript")

        Returns:
            str: Prompt for generating Chapter 1 content
        """
        return f"""Analyze this {language} code and create Chapter 1: "What This Code Does"

CODE TO ANALYZE:
```{language}
{code}
```

Your task is to write a ONE-SENTENCE summary that explains what this code does in plain, everyday language.

Rules for the summary:
1. NO programming jargon - use everyday words only
2. Explain the PURPOSE, not the technical details
3. A person with zero programming knowledge should understand it
4. Use concrete, relatable terms (like "a recipe", "a to-do list", "a calculator")
5. Maximum 2 sentences if absolutely necessary, but prefer 1

Example of good summaries:
- "This code is like a calculator that adds up a shopping list and tells you the total"
- "This code sorts names alphabetically, like organizing books on a shelf from A to Z"
- "This code checks if a password is strong enough, like a security guard checking IDs"

BAD examples (too technical):
- "This function iterates over an array and applies a callback" (too technical)
- "This implements a sorting algorithm" (jargon)

Return a JSON object with this structure:
{{
    "title": "What This Code Does",
    "summary": "your one-sentence summary here"
}}"""

    @staticmethod
    def get_chapter2_prompt(code: str, language: str) -> str:
        """
        Generate prompt for Chapter 2: Prerequisites Knowledge.

        Identifies up to 5 key concepts needed to understand the code,
        with explanation, analogy, example, and use cases for each.

        Args:
            code: The source code to explain
            language: Programming language

        Returns:
            str: Prompt for generating Chapter 2 content
        """
        return f"""Analyze this {language} code and create Chapter 2: "Prerequisites Knowledge"

CODE TO ANALYZE:
```{language}
{code}
```

Your task is to identify the MOST IMPORTANT programming concepts a beginner needs to understand before reading this code.

For EACH concept (maximum 5 concepts), provide:
1. **name**: The concept name (e.g., "Variables", "Functions", "Loops")
2. **explanation**: A simple explanation using everyday language (2-3 sentences)
3. **analogy**: A real-life analogy that makes the concept relatable
4. **example**: A minimal code example with explanation
5. **use_cases**: Where this concept is commonly used in real life

Rules:
- Maximum 5 concepts - pick only the most essential ones
- Start with the most basic concepts first
- NEVER assume any prior programming knowledge
- Analogies should use everyday objects (boxes, recipes, instruction manuals, etc.)
- Examples should be as SHORT as possible (1-3 lines of code)

Example concept card:
{{
    "name": "Variables",
    "explanation": "A variable is like a labeled box where you store information. You give the box a name so you can find and use what's inside later.",
    "analogy": "Think of a sticky note with a name on it attached to a box. The sticky note says 'age' and inside the box is the number 25. Whenever you need to know the age, you look in that box.",
    "example": "age = 25  # Creates a box named 'age' with the number 25 inside",
    "use_cases": "Variables are used everywhere: storing your name in a contact list, keeping track of a game score, remembering your shopping cart items."
}}

Return a JSON object with this structure:
{{
    "title": "Prerequisites Knowledge",
    "concepts": [
        // array of concept objects (max 5)
    ]
}}"""

    @staticmethod
    def get_chapter3_prompt(
        code: str, language: str, files_info: list[FileInfo] | None = None
    ) -> str:
        """
        Generate prompt for Chapter 3: Code Structure Overview.

        Creates a visual flowchart and file structure breakdown.

        Args:
            code: The source code to explain
            language: Programming language
            files_info: Optional list of file information for multi-file uploads

        Returns:
            str: Prompt for generating Chapter 3 content
        """
        file_section = ""
        if files_info and len(files_info) > 1:
            file_list = "\n".join(
                [f"- {f.file_name}: {f.file_path or 'root'}" for f in files_info]
            )
            file_section = f"""
FILES IN THIS UPLOAD:
{file_list}
"""

        return f"""Analyze this {language} code and create Chapter 3: "Code Structure Overview"

CODE TO ANALYZE:
```{language}
{code}
```
{file_section}

Your task is to help beginners visualize HOW the code is organized and WHAT order things happen.

Create two things:

1. **flowchart**: A simple ASCII diagram showing the main flow of the program
   - Use simple arrows (-->) and boxes made of text
   - Show the main steps, not every detail
   - Include decision points (if/else) as diamonds or branches

   Example flowchart format:
   ```
   [Start]
      |
      v
   [Get user input]
      |
      v
   [Is input valid?]
     / \\
   Yes   No
    |     |
    v     v
   [Process]  [Show error]
      |         |
      v         v
   [Show result] [Ask again]
   ```

2. **file_breakdown**: For each file (or section of code), explain what it does in ONE simple sentence

Rules:
- The flowchart should be readable by someone who has never seen code
- Use everyday terms: "Get user input" not "Read stdin"
- Focus on the WHAT (what happens), not the HOW (technical details)
- If there's only one file, break it down by sections (imports, functions, main logic)

Return a JSON object with this structure:
{{
    "title": "Code Structure Overview",
    "flowchart": "your ASCII flowchart here (use \\n for new lines)",
    "file_breakdown": {{
        "filename_or_section": "what this file/section does in one sentence"
    }}
}}"""

    @staticmethod
    def get_chapter4_prompt(code: str, language: str) -> str:
        """
        Generate prompt for Chapter 4: Line-by-Line Explanation.

        Provides detailed explanation for each significant line of code.

        Args:
            code: The source code to explain
            language: Programming language

        Returns:
            str: Prompt for generating Chapter 4 content
        """
        return f"""Analyze this {language} code and create Chapter 4: "Line-by-Line Explanation"

CODE TO ANALYZE:
```{language}
{code}
```

Your task is to explain EVERY significant line of code in a way a complete beginner can understand.

For EACH line (skip blank lines and simple closing brackets), provide:
1. **line_number**: The line number in the code
2. **code**: The actual code on that line
3. **what_it_does**: Plain language explanation of what this line accomplishes
4. **syntax_breakdown**: Explain each part of the syntax (what does each symbol/word mean)
5. **analogy**: (optional but recommended) A real-life comparison
6. **alternatives**: (optional) Other ways to write the same thing
7. **important_notes**: (optional) Common mistakes or important tips for this line

Rules:
- Explain EVERY symbol: =, (), [], {{}}, :, etc.
- Never skip a concept because it seems "obvious"
- Use analogies frequently - they help concepts stick
- Group related lines if they work together (like a for loop with its body)
- For simple lines (like imports), you can keep explanations brief

Example explanation:
{{
    "line_number": 1,
    "code": "def calculate_total(prices):",
    "what_it_does": "This creates a reusable recipe (function) named 'calculate_total' that expects a list of prices as input.",
    "syntax_breakdown": "'def' = 'define' (we're creating something new). 'calculate_total' = the name we're giving our recipe. '(prices)' = the ingredients we need (a list of prices). ':' = signals that the recipe instructions start on the next line.",
    "analogy": "Like writing a recipe card: 'Recipe Name: Calculate Total, Ingredients: list of prices'. Now anyone can use this recipe whenever they need it.",
    "alternatives": "In some languages, you'd use 'function' instead of 'def'.",
    "important_notes": "The name should describe what the function does. Using 'x' or 'foo' would be confusing!"
}}

Return a JSON object with this structure:
{{
    "title": "Line-by-Line Explanation",
    "explanations": [
        // array of line explanation objects
    ]
}}"""

    @staticmethod
    def get_chapter5_prompt(code: str, language: str) -> str:
        """
        Generate prompt for Chapter 5: Execution Flow Simulation.

        Shows step-by-step how the program executes with data states.

        Args:
            code: The source code to explain
            language: Programming language

        Returns:
            str: Prompt for generating Chapter 5 content
        """
        return f"""Analyze this {language} code and create Chapter 5: "Execution Flow Simulation"

CODE TO ANALYZE:
```{language}
{code}
```

Your task is to WALK THROUGH how this code actually runs, step by step, like watching a movie in slow motion.

For EACH step of execution, provide:
1. **step_number**: The step number (1, 2, 3...)
2. **action**: What happens in this step (plain language)
3. **data_state**: What values are stored in memory right now (show all variables and their current values)
4. **explanation**: Why this matters or what the computer is "thinking"

Rules:
- Start from the very first line the computer reads
- Show the state of ALL variables at each step
- Use a concrete example (make up realistic input values if needed)
- Explain WHY the computer goes to the next step it does
- For loops, show at least 2-3 iterations so the pattern is clear
- For conditionals (if/else), explain which path is taken and why

Example steps:
{{
    "step_number": 1,
    "action": "Computer reads line 1: prices = [10, 20, 30]",
    "data_state": "prices = [10, 20, 30]",
    "explanation": "The computer creates a list (like a shopping cart) with three prices inside: $10, $20, and $30. It stores this list in a box labeled 'prices'."
}}

{{
    "step_number": 2,
    "action": "Computer reads line 2: total = 0",
    "data_state": "prices = [10, 20, 30], total = 0",
    "explanation": "The computer creates another box labeled 'total' and puts 0 inside. This will be our running sum, starting from zero like a fresh calculator."
}}

{{
    "step_number": 3,
    "action": "Computer enters the for loop, takes first price (10)",
    "data_state": "prices = [10, 20, 30], total = 0, price = 10",
    "explanation": "The computer picks up the first item from our shopping cart ($10) and holds it in a temporary box called 'price'. Now it's ready to work with this price."
}}

Return a JSON object with this structure:
{{
    "title": "Execution Flow Simulation",
    "steps": [
        // array of step objects
    ]
}}"""

    @staticmethod
    def get_chapter6_prompt(code: str, language: str) -> str:
        """
        Generate prompt for Chapter 6: Core Concepts Summary.

        Summarizes the key programming concepts learned from this code.

        Args:
            code: The source code to explain
            language: Programming language

        Returns:
            str: Prompt for generating Chapter 6 content
        """
        return f"""Analyze this {language} code and create Chapter 6: "Core Concepts Summary"

CODE TO ANALYZE:
```{language}
{code}
```

Your task is to summarize the KEY PROGRAMMING CONCEPTS that a beginner has learned by studying this code.

For EACH core concept used in the code, provide:
1. **concept_name**: The name of the concept (e.g., "Loops", "Functions", "Lists")
2. **what_it_is**: A concise definition in beginner-friendly language
3. **why_used**: Why programmers use this concept (what problem does it solve?)
4. **where_applied**: Real-world applications where this concept is used

Rules:
- Focus on the concepts ACTUALLY USED in the code
- Keep explanations concise but complete
- Connect each concept to real-world uses
- Order from most fundamental to most advanced

Example concept summary:
{{
    "concept_name": "For Loops",
    "what_it_is": "A for loop is a way to repeat the same action multiple times, automatically. Instead of writing the same code 100 times, you write it once and tell the computer to repeat it.",
    "why_used": "Loops save time and reduce errors. Imagine having to manually add 1000 numbers - a loop does this in seconds without mistakes.",
    "where_applied": "Playing each song in a playlist, sending the same email to multiple recipients, calculating the total of all items in a shopping cart."
}}

Return a JSON object with this structure:
{{
    "title": "Core Concepts Summary",
    "concepts": [
        // array of concept summary objects
    ]
}}"""

    @staticmethod
    def get_chapter7_prompt(code: str, language: str) -> str:
        """
        Generate prompt for Chapter 7: Common Mistakes.

        Lists 3-5 common mistakes beginners make with this type of code.

        Args:
            code: The source code to explain
            language: Programming language

        Returns:
            str: Prompt for generating Chapter 7 content
        """
        return f"""Analyze this {language} code and create Chapter 7: "Common Mistakes"

CODE TO ANALYZE:
```{language}
{code}
```

Your task is to identify 3-5 COMMON MISTAKES that beginners make when working with code like this.

For EACH mistake, provide:
1. **mistake_title**: A short title for the mistake
2. **wrong_code**: An example of the WRONG way to write it (realistic mistake)
3. **right_code**: The CORRECT way to write it
4. **why_it_matters**: Why this mistake causes problems (what breaks?)
5. **how_to_fix**: Step-by-step guidance to fix and avoid this mistake

Rules:
- Focus on mistakes BEGINNERS actually make (not obscure edge cases)
- Make the wrong_code look realistic (like a beginner would write it)
- Explain the consequences in plain language (what error would they see?)
- Give actionable advice for how to remember the correct way
- Minimum 3, maximum 5 mistakes

Example mistake:
{{
    "mistake_title": "Forgetting the colon after 'if'",
    "wrong_code": "if age > 18\\n    print('Adult')",
    "right_code": "if age > 18:\\n    print('Adult')",
    "why_it_matters": "Python uses the colon (:) to know where the condition ends and the action begins. Without it, Python gets confused and shows an error: 'SyntaxError: expected ':'",
    "how_to_fix": "Every time you write 'if', 'for', 'while', or 'def', remember to end the line with a colon. Think of it like a colon before a list: 'My shopping list: apples, oranges, bananas'."
}}

Return a JSON object with this structure:
{{
    "title": "Common Mistakes",
    "mistakes": [
        // array of 3-5 mistake objects
    ]
}}"""

    @staticmethod
    def get_full_document_prompt(
        code: str,
        language: str,
        files_info: list[FileInfo] | None = None,
    ) -> str:
        """
        Generate a combined prompt for all 7 chapters at once.

        Use this for generating the complete document in a single API call.
        For very long code, consider generating chapters separately.

        Args:
            code: The source code to explain
            language: Programming language
            files_info: Optional list of file information for multi-file uploads

        Returns:
            str: Complete prompt for generating all 7 chapters
        """
        file_section = ""
        if files_info and len(files_info) > 1:
            file_list = "\n".join(
                [f"- {f.file_name} ({f.file_path or 'root'})" for f in files_info]
            )
            file_section = f"""
FILES IN THIS UPLOAD:
{file_list}
"""

        return f"""You are creating a comprehensive 7-chapter learning document for a COMPLETE BEGINNER with ZERO programming experience.

CODE TO ANALYZE ({language}):
```{language}
{code}
```
{file_section}

Generate ALL 7 chapters as a single JSON document. Follow the structure and rules below EXACTLY.

=== CHAPTER 1: What This Code Does ===
- One-sentence summary in PLAIN language (no jargon)
- Use concrete, relatable comparisons

=== CHAPTER 2: Prerequisites Knowledge ===
- Maximum 5 concept cards
- Each concept needs: name, explanation, analogy, example, use_cases
- Start with most basic concepts first

=== CHAPTER 3: Code Structure Overview ===
- ASCII flowchart showing program flow
- File/section breakdown with one-sentence descriptions

=== CHAPTER 4: Line-by-Line Explanation ===
- Every significant line explained
- Include: what_it_does, syntax_breakdown
- Optional: analogy, alternatives, important_notes

=== CHAPTER 5: Execution Flow Simulation ===
- Step-by-step walkthrough with concrete values
- Show data_state (all variable values) at each step
- Explain the "why" behind each step

=== CHAPTER 6: Core Concepts Summary ===
- Key concepts from this code
- For each: what_it_is, why_used, where_applied

=== CHAPTER 7: Common Mistakes ===
- 3-5 beginner mistakes related to this code
- Each with: wrong_code, right_code, why_it_matters, how_to_fix

=== CRITICAL RULES ===
1. NEVER use programming jargon without explaining it
2. ALWAYS include real-life analogies
3. Write for someone with ZERO programming knowledge
4. Be encouraging and patient in tone
5. Use concrete examples, not abstract descriptions

Return a JSON object with this EXACT structure:
{{
    "chapter1": {{
        "title": "What This Code Does",
        "summary": "..."
    }},
    "chapter2": {{
        "title": "Prerequisites Knowledge",
        "concepts": [...]
    }},
    "chapter3": {{
        "title": "Code Structure Overview",
        "flowchart": "...",
        "file_breakdown": {{...}}
    }},
    "chapter4": {{
        "title": "Line-by-Line Explanation",
        "explanations": [...]
    }},
    "chapter5": {{
        "title": "Execution Flow Simulation",
        "steps": [...]
    }},
    "chapter6": {{
        "title": "Core Concepts Summary",
        "concepts": [...]
    }},
    "chapter7": {{
        "title": "Common Mistakes",
        "mistakes": [...]
    }}
}}"""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_system_instruction(use_korean: bool = False) -> str:
    """
    Get the system instruction for the AI model.

    Args:
        use_korean: If True, use Korean language system instruction

    Returns:
        str: System instruction text
    """
    if use_korean:
        return KOREAN_EDUCATIONAL_SYSTEM_INSTRUCTION
    return EDUCATIONAL_SYSTEM_INSTRUCTION


def get_document_generation_prompt(
    code: str,
    language: str,
    files_info: list[FileInfo] | None = None,
    chapter: int | None = None,
) -> str:
    """
    Get the appropriate prompt for document generation.

    Args:
        code: The source code to explain
        language: Programming language
        files_info: Optional list of file information
        chapter: Specific chapter number (1-7) or None for full document

    Returns:
        str: Prompt for document generation

    Raises:
        ValueError: If chapter number is invalid
    """
    if chapter is None:
        return DocumentPrompts.get_full_document_prompt(code, language, files_info)

    chapter_prompts = {
        1: DocumentPrompts.get_chapter1_prompt,
        2: DocumentPrompts.get_chapter2_prompt,
        3: lambda c, lang: DocumentPrompts.get_chapter3_prompt(c, lang, files_info),
        4: DocumentPrompts.get_chapter4_prompt,
        5: DocumentPrompts.get_chapter5_prompt,
        6: DocumentPrompts.get_chapter6_prompt,
        7: DocumentPrompts.get_chapter7_prompt,
    }

    if chapter not in chapter_prompts:
        raise ValueError(f"Invalid chapter number: {chapter}. Must be 1-7.")

    prompt_fn = chapter_prompts[chapter]
    return prompt_fn(code, language)


def get_document_response_schema() -> dict[str, Any]:
    """
    Get the JSON schema for validating document responses.

    Returns:
        dict: JSON schema for full document response
    """
    return DOCUMENT_RESPONSE_SCHEMA


def get_chapter_schema(chapter: int) -> dict[str, Any]:
    """
    Get the JSON schema for a specific chapter.

    Args:
        chapter: Chapter number (1-7)

    Returns:
        dict: JSON schema for the specified chapter

    Raises:
        ValueError: If chapter number is invalid
    """
    schemas = {
        1: CHAPTER1_SCHEMA,
        2: CHAPTER2_SCHEMA,
        3: CHAPTER3_SCHEMA,
        4: CHAPTER4_SCHEMA,
        5: CHAPTER5_SCHEMA,
        6: CHAPTER6_SCHEMA,
        7: CHAPTER7_SCHEMA,
    }

    if chapter not in schemas:
        raise ValueError(f"Invalid chapter number: {chapter}. Must be 1-7.")

    return schemas[chapter]


def validate_document_structure(document: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate that a generated document has the correct structure.

    Args:
        document: The generated document dictionary

    Returns:
        tuple: (is_valid, list of error messages)
    """
    errors = []
    required_chapters = [f"chapter{i}" for i in range(1, 8)]

    for chapter_key in required_chapters:
        if chapter_key not in document:
            errors.append(f"Missing {chapter_key}")
            continue

        chapter = document[chapter_key]

        if not isinstance(chapter, dict):
            errors.append(f"{chapter_key} is not a dictionary")
            continue

        if "title" not in chapter:
            errors.append(f"{chapter_key} missing 'title' field")

    # Chapter-specific validations
    if "chapter2" in document and isinstance(document["chapter2"], dict):
        concepts = document["chapter2"].get("concepts", [])
        if len(concepts) > 5:
            errors.append("chapter2 has more than 5 concepts (max is 5)")

    if "chapter7" in document and isinstance(document["chapter7"], dict):
        mistakes = document["chapter7"].get("mistakes", [])
        if len(mistakes) < 3:
            errors.append("chapter7 has fewer than 3 mistakes (min is 3)")
        if len(mistakes) > 5:
            errors.append("chapter7 has more than 5 mistakes (max is 5)")

    return len(errors) == 0, errors


def estimate_token_count(text: str) -> int:
    """
    Estimate the token count for a piece of text.

    This is a rough estimate (4 characters per token on average).
    For accurate counts, use the tiktoken library.

    Args:
        text: Text to estimate tokens for

    Returns:
        int: Estimated token count
    """
    return len(text) // 4
