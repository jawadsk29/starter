# Flashcard Quizzer

A powerful command-line application for learning with flashcards. Load your study deck from JSON and quiz yourself in three different modes: sequential, random, or adaptive learning.

## Features

### Three Quiz Modes
- **Sequential Mode**: Study cards in the order they appear in your deck
- **Random Mode**: Shuffle cards for variety and prevent memorization by position
- **Adaptive Mode**: First review all cards, then focus on the ones you got wrong

### Smart Answer Matching
The app uses intelligent answer validation with multiple strategies:
- Exact matching (case-insensitive)
- Word-based matching (all your words must be in the correct answer)
- Fuzzy matching (accepts 50%+ similarity for typos)
- Minimum 2-character length requirement prevents single-character false positives

### JSON Format Support
Load flashcards from two flexible JSON formats:

**Array Format** (`glossary.json`):
```json
[
  {"front": "Capital of France?", "back": "Paris"},
  {"front": "2 + 2 = ?", "back": "4"}
]
```

**Object Format** (`python_basics.json`):
```json
{
  "cards": [
    {"front": "What does len() do?", "back": "Returns the length of a sequence"},
    {"front": "What is a dict?", "back": "A collection of key-value pairs"}
  ]
}
```

### Visual Feedback
- Color-coded terminal output (green for correct, red for incorrect)
- Real-time statistics during quiz
- Clear headers and formatting
- Graceful exit handling

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. Clone or download this project
2. Navigate to the project directory:
   ```bash
   cd /voc/work/project/starter
   ```

3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Usage

### Basic Commands

Run the application with a flashcard deck:
```bash
python main.py --file data/glossary.json
```

### Command-Line Options

- `-f, --file` (required): Path to your JSON flashcard file
- `-m, --mode` (optional): Quiz mode - `sequential`, `random`, or `adaptive` (default: sequential)
- `--stats` (optional): Show statistics after each question

### Examples

**Study Python basics in sequential mode:**
```bash
python main.py --file data/python_basics.json --mode sequential
```

**Random quiz with live stats:**
```bash
python main.py -f data/glossary.json -m random --stats
```

**Adaptive learning mode (focus on weak areas):**
```bash
python main.py -f data/python_basics.json -m adaptive
```

**Show help:**
```bash
python main.py --help
```

## Creating Your Own Flashcard Deck

Create a JSON file in the `data/` directory. Use either format:

**Simple array format** (`my_deck.json`):
```json
[
  {"front": "Question 1", "back": "Answer 1"},
  {"front": "Question 2", "back": "Answer 2"}
]
```

Then run:
```bash
python main.py -f data/my_deck.json
```

## Project Structure

```
flashcard-quizzer/
├── main.py                      # CLI entry point
├── utils/
│   ├── flashcard_loader.py     # JSON loading and validation
│   └── quiz_engine.py          # Quiz modes (Strategy + Factory patterns)
├── tests/
│   └── test_flashcard_loader.py # Comprehensive test suite
├── data/
│   ├── glossary.json           # Sample deck (array format)
│   └── python_basics.json      # Sample deck (object format)
├── docs/
│   ├── ai_edit_log.md          # AI collaboration documentation
│   ├── report_template.md      # Final project report template
│   └── design_patterns.md      # Architecture documentation
├── requirements.txt             # Project dependencies
└── README.md                    # This file
```

## Code Quality

This project maintains high code quality standards:

### Run Tests
```bash
python -m pytest tests/ -v
python -m pytest --cov=. --cov-report=html  # With coverage (target: >80%)
```

### Format Code
```bash
python -m black .
python -m isort .
```

### Lint Check
```bash
python -m flake8 .
python -m mypy .
```

### All Quality Checks
```bash
python -m pytest --cov=. && python -m black --check . && python -m flake8 . && python -m mypy .
```

## Technical Design

### Design Patterns Used
- **Strategy Pattern**: Each quiz mode implements a strategy for card ordering
- **Factory Pattern**: `QuizModeFactory` creates the appropriate quiz mode
- **Abstract Base Class**: `QuizMode` defines the interface for all modes

### Error Handling
- Custom `FlashcardLoadError` exception with detailed messages
- Graceful handling of malformed JSON
- Validation at load time with clear error reporting
- User-friendly error messages (no Python tracebacks shown)

### Type Safety
- Full type hints throughout the codebase
- `TypedDict` for flashcard structure definition
- Type checking with mypy

## Test Coverage

The project includes 64 comprehensive tests covering:
- Both JSON formats (array and object)
- Unicode character support
- Error handling and validation
- All three quiz modes
- Answer checking with fuzzy matching
- Statistics tracking
- Edge cases (empty decks, single card, etc.)

**Current coverage: 99%** of core logic

## Tips for Effective Learning

1. **Start with Sequential Mode**: Understand the material in order first
2. **Switch to Random Mode**: Challenge yourself with unpredictable order
3. **Use Adaptive Mode**: Focus study time on weak areas
4. **Enable Stats**: Use `--stats` to track your progress and identify patterns
5. **Custom Decks**: Create focused decks for specific topics

## Troubleshooting

### "File not found" error
- Check the file path is correct (use relative paths from project root)
- Ensure the file is in the `data/` directory or provide the full path

### "Invalid JSON" error
- Validate your JSON syntax (use a JSON validator tool)
- Ensure all strings are properly quoted
- Check for trailing commas in arrays/objects

### "Missing 'front' or 'back' field" error
- Every card must have both "front" and "back" fields
- Both fields must be strings, not numbers or arrays

## Development Notes

This project was developed using AI-assisted development practices. See `ai_edit_log.md` for details on:
- AI prompts used during development
- Design decisions and rationale
- Code review and refinement process
- Lessons learned about AI collaboration

## License

[License](../../LICENSE.txt)
