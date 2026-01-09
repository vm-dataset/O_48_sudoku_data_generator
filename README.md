# Sudoku Task Data Generator 🎲

A data generator for creating synthetic sudoku solving tasks. Generates sudoku puzzles with initial states, solutions, and animated solving videos.

Repository: [O_48_sudoku_data_generator](https://github.com/vm-dataset/O_48_sudoku_data_generator)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vm-dataset/O_48_sudoku_data_generator.git
cd O_48_sudoku_data_generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python examples/generate.py --num-samples 50
```

---

## 📁 Structure

```
sudoku-task-data-generator/
├── core/                    # ✅ KEEP: Standard utilities
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image helpers
│   ├── video_utils.py      # Video generation
│   └── output_writer.py    # File output
├── src/                     # ⚠️ SUDOKU TASK: Task logic
│   ├── generator.py        # Sudoku generator
│   ├── prompts.py          # Sudoku prompt templates
│   └── config.py           # Sudoku configuration
├── examples/
│   └── generate.py         # Entry point
└── data/questions/         # Generated output
```

---

## 📦 Output Format

Every generator produces:

```
data/questions/sudoku_task/{task_id}/
├── first_frame.png          # Initial puzzle (REQUIRED)
├── final_frame.png          # Complete solution (REQUIRED)
├── prompt.txt               # Instructions (REQUIRED)
└── ground_truth.mp4         # Solving video (OPTIONAL)
```

---

## 🎯 Features

- **Valid Sudoku Generation**: Generates valid 9x9 sudoku puzzles with unique solutions
- **Difficulty Levels**: Automatically assesses difficulty (easy/medium/hard) based on number of givens
- **Visual Rendering**: Clean 9x9 grid with proper 3x3 box boundaries
- **Animated Solutions**: Step-by-step solving videos showing numbers being filled
- **Configurable**: Adjustable puzzle parameters (min/max givens, grid size, etc.)

---

## 🎨 Configuration

### Task-Specific Settings (`src/config.py`)

```python
class TaskConfig(GenerationConfig):
    domain: str = Field(default="sudoku")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    # Sudoku-specific settings
    min_givens: int = Field(default=17)      # Minimum clues for valid puzzle
    max_givens: int = Field(default=35)      # Maximum clues
    grid_size: int = Field(default=9)        # Standard 9x9 grid
    difficulty_levels: list[str] = Field(default=["easy", "medium", "hard"])
```

### Usage Examples

```bash
# Generate 10 puzzles without videos
python examples/generate.py --num-samples 10 --no-videos

# Generate 100 puzzles with videos
python examples/generate.py --num-samples 100

# Custom output directory and seed
python examples/generate.py --num-samples 50 --output data/my_sudoku --seed 42
```

---

## 🔧 Implementation Details

### Sudoku Generation Algorithm

1. **Complete Solution**: Generates a valid complete 9x9 sudoku grid using backtracking
2. **Puzzle Creation**: Removes numbers from solution while maintaining uniqueness
3. **Validation**: Ensures puzzle follows standard sudoku rules (no duplicates in rows, columns, or 3x3 boxes)

### Video Generation

- Shows step-by-step solving process
- Highlights each cell as it's filled
- Smooth animation with configurable frame rate

---

## 📋 Requirements

- Python >= 3.8
- numpy
- Pillow
- pydantic
- opencv-python (for video generation)

---

## 📝 License

See LICENSE file for details.
