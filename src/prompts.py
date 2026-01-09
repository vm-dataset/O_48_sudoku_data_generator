"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           SUDOKU TASK PROMPTS                                  ║
║                                                                               ║
║  Prompts/instructions for sudoku solving tasks.                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        "Solve this sudoku puzzle by filling in all empty cells. Each row, column, and 3x3 box must contain the digits 1-9 exactly once. Show the complete solution step by step.",
        "Complete this sudoku puzzle. Fill in the missing numbers so that every row, column, and 3x3 square contains all digits from 1 to 9 without repetition. Animate the solving process.",
        "Solve the sudoku puzzle. Place numbers in the empty cells following sudoku rules: each number 1-9 must appear exactly once in each row, column, and 3x3 box. Show how you fill each cell.",
    ],
    
    "easy": [
        "Solve this easy sudoku puzzle. Fill in the empty cells with numbers 1-9, ensuring no duplicates in any row, column, or 3x3 box. Show the solution being filled in.",
        "Complete this beginner sudoku. Each empty cell should be filled with a number from 1 to 9, following standard sudoku rules. Animate the numbers being placed.",
        "Solve this straightforward sudoku puzzle. Fill all empty squares so that each row, column, and 3x3 region contains digits 1-9 exactly once. Show the solving process.",
    ],
    
    "medium": [
        "Solve this medium difficulty sudoku puzzle. Use logical deduction to fill in the missing numbers, ensuring each row, column, and 3x3 box has all digits 1-9. Show your reasoning step by step.",
        "Complete this intermediate sudoku. Fill in the empty cells by applying sudoku rules: no number can repeat in any row, column, or 3x3 square. Animate the solution process.",
        "Solve this sudoku puzzle of medium complexity. Place numbers in empty cells following the rules, and show how each number is determined and placed.",
    ],
    
    "hard": [
        "Solve this challenging sudoku puzzle. Use advanced techniques to deduce the correct numbers for each empty cell. Show the complete solving process with all numbers being filled in.",
        "Complete this difficult sudoku. Apply advanced sudoku solving strategies to fill in all empty cells. Each row, column, and 3x3 box must contain 1-9 exactly once. Animate the solution.",
        "Solve this hard sudoku puzzle. Fill in all missing numbers using logical reasoning and sudoku techniques. Show step by step how each cell is solved and filled.",
    ],
}


def get_prompt(task_type: str = "default") -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict) - "easy", "medium", "hard", or "default"
        
    Returns:
        Random prompt string from the specified type
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])
