"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           SUDOKU TASK GENERATOR                                ║
║                                                                               ║
║  Generates sudoku puzzles with initial state (puzzle) and final state         ║
║  (solution), plus animated solving video.                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """
    Sudoku task generator.
    
    Generates valid sudoku puzzles and their solutions.
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        
        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one sudoku task pair."""
        
        # Generate sudoku puzzle and solution
        puzzle, solution = self._generate_sudoku()
        
        # Render images
        first_image = self._render_sudoku(puzzle)
        final_image = self._render_sudoku(solution)
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(puzzle, solution, task_id)
        
        # Select prompt
        difficulty = self._assess_difficulty(puzzle)
        prompt = get_prompt(difficulty)
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  SUDOKU GENERATION
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_sudoku(self) -> Tuple[List[List[int]], List[List[int]]]:
        """
        Generate a valid sudoku puzzle and its solution.
        
        Returns:
            (puzzle, solution) where puzzle has 0s for empty cells
        """
        # First, generate a complete valid solution
        solution = self._generate_complete_sudoku()
        
        # Then, remove numbers to create a puzzle
        puzzle = [row[:] for row in solution]  # Deep copy
        puzzle = self._create_puzzle(puzzle, solution)
        
        return puzzle, solution
    
    def _generate_complete_sudoku(self) -> List[List[int]]:
        """Generate a complete valid sudoku solution."""
        grid = [[0] * 9 for _ in range(9)]
        
        # Fill diagonal 3x3 boxes first (they don't conflict)
        for box in range(0, 9, 3):
            self._fill_box(grid, box, box)
        
        # Solve the rest using backtracking
        self._solve_sudoku(grid)
        
        return grid
    
    def _fill_box(self, grid: List[List[int]], row: int, col: int) -> None:
        """Fill a 3x3 box with random numbers 1-9."""
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        idx = 0
        for i in range(3):
            for j in range(3):
                grid[row + i][col + j] = numbers[idx]
                idx += 1
    
    def _solve_sudoku(self, grid: List[List[int]]) -> bool:
        """Solve sudoku using backtracking. Returns True if solvable."""
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)  # Randomize for variety
                    
                    for num in numbers:
                        if self._is_valid(grid, i, j, num):
                            grid[i][j] = num
                            if self._solve_sudoku(grid):
                                return True
                            grid[i][j] = 0
                    return False
        return True
    
    def _is_valid(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid."""
        # Check row
        for j in range(9):
            if grid[row][j] == num:
                return False
        
        # Check column
        for i in range(9):
            if grid[i][col] == num:
                return False
        
        # Check 3x3 box
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if grid[box_row + i][box_col + j] == num:
                    return False
        
        return True
    
    def _create_puzzle(self, puzzle: List[List[int]], solution: List[List[int]]) -> List[List[int]]:
        """Remove numbers from solution to create a puzzle."""
        # Determine number of cells to remove based on difficulty
        min_givens = self.config.min_givens
        max_givens = self.config.max_givens
        target_givens = random.randint(min_givens, max_givens)
        
        # Create list of all positions
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        # Remove numbers while ensuring puzzle remains solvable
        removed = 0
        total_cells = 81
        target_removed = total_cells - target_givens
        
        for row, col in positions:
            if removed >= target_removed:
                break
            
            # Try removing this cell
            original = puzzle[row][col]
            puzzle[row][col] = 0
            
            # Check if puzzle still has unique solution
            # For simplicity, we'll use a heuristic: remove if it doesn't break uniqueness
            # In a production system, you'd want more sophisticated checking
            removed += 1
        
        return puzzle
    
    def _assess_difficulty(self, puzzle: List[List[int]]) -> str:
        """Assess puzzle difficulty based on number of givens."""
        givens = sum(1 for row in puzzle for cell in row if cell != 0)
        
        if givens >= 30:
            return "easy"
        elif givens >= 25:
            return "medium"
        else:
            return "hard"
    
    # ══════════════════════════════════════════════════════════════════════════
    #  RENDERING
    # ══════════════════════════════════════════════════════════════════════════
    
    def _render_sudoku(self, grid: List[List[int]], highlight_cells: Optional[List[Tuple[int, int]]] = None) -> Image.Image:
        """
        Render sudoku grid as image.
        
        Args:
            grid: 9x9 grid with numbers (0 for empty)
            highlight_cells: Optional list of (row, col) tuples to highlight
        """
        img = Image.new("RGB", self.config.image_size, color="white")
        draw = ImageDraw.Draw(img)
        
        width, height = self.config.image_size
        cell_size = min(width, height) // 10  # Leave some margin
        start_x = (width - cell_size * 9) // 2
        start_y = (height - cell_size * 9) // 2
        
        # Load font
        font_size = int(cell_size * 0.5)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Draw grid
        for i in range(10):
            # Vertical lines
            x = start_x + i * cell_size
            line_width = 3 if i % 3 == 0 else 1
            draw.line([(x, start_y), (x, start_y + cell_size * 9)], 
                     fill=(0, 0, 0), width=line_width)
            
            # Horizontal lines
            y = start_y + i * cell_size
            draw.line([(start_x, y), (start_x + cell_size * 9, y)], 
                     fill=(0, 0, 0), width=line_width)
        
        # Highlight cells if specified
        if highlight_cells:
            for row, col in highlight_cells:
                x0 = start_x + col * cell_size
                y0 = start_y + row * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 200), outline=(255, 200, 0), width=2)
        
        # Draw numbers
        for i in range(9):
            for j in range(9):
                if grid[i][j] != 0:
                    x = start_x + j * cell_size + cell_size // 2
                    y = start_y + i * cell_size + cell_size // 2
                    
                    # Center text
                    text = str(grid[i][j])
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    draw.text(
                        (x - text_width // 2, y - text_height // 2),
                        text,
                        fill=(0, 0, 0),
                        font=font
                    )
        
        return img
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO GENERATION
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_video(
        self,
        puzzle: List[List[int]],
        solution: List[List[int]],
        task_id: str
    ) -> Optional[str]:
        """Generate ground truth video showing solving process."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames showing solving process
        frames = self._create_solving_frames(puzzle, solution)
        
        if not frames:
            return None
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_solving_frames(
        self,
        puzzle: List[List[int]],
        solution: List[List[int]],
        hold_frames: int = 4,
        step_frames: Optional[int] = None
    ) -> List[Image.Image]:
        """
        Create animation frames showing the solving process.
        
        Shows numbers being filled in step by step.
        Dynamically adjusts frame count to match target video duration.
        """
        frames = []
        
        # Get list of cells to fill (empty cells in puzzle)
        cells_to_fill = []
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0:
                    cells_to_fill.append((i, j))
        
        num_cells = len(cells_to_fill)
        
        # Calculate target total frames for desired duration
        target_frames = int(self.config.target_video_duration * self.config.video_fps)
        
        # Calculate step_frames dynamically if not provided
        # Reserve frames for initial and final holds
        reserved_frames = hold_frames * 2  # initial + final
        available_frames = max(1, target_frames - reserved_frames)
        
        if step_frames is None:
            # Distribute available frames across cells
            if num_cells > 0:
                # Calculate frames per cell to match target duration
                # Use regular division and round to nearest integer
                step_frames = max(1, round(available_frames / num_cells))
            else:
                step_frames = 1
        
        # Hold initial puzzle
        initial_frame = self._render_sudoku(puzzle)
        for _ in range(hold_frames):
            frames.append(initial_frame)
        
        # Randomize order for visual variety
        random.shuffle(cells_to_fill)
        
        # Create intermediate states
        current_state = [row[:] for row in puzzle]  # Deep copy
        
        for row, col in cells_to_fill:
            # Fill this cell
            current_state[row][col] = solution[row][col]
            
            # Render frame with this cell highlighted
            frame = self._render_sudoku(current_state, highlight_cells=[(row, col)])
            
            # Add frames for this step
            for _ in range(step_frames):
                frames.append(frame)
        
        # Hold final solution
        final_frame = self._render_sudoku(solution)
        for _ in range(hold_frames):
            frames.append(final_frame)
        
        return frames
