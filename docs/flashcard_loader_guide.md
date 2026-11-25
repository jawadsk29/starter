# Flashcard Loader Guide

The flashcard loader (`utils/flashcard_loader.py`) handles loading and validating flashcard data from JSON files with comprehensive error handling.

## Supported Formats

### Array Format
Simple array of flashcard objects:

```json
[
  {"front": "Question 1", "back": "Answer 1"},
  {"front": "Question 2", "back": "Answer 2"}
]
```

### Object Format
Wrapper object with `cards` array (supports metadata):

```json
{
  "title": "My Deck",
  "description": "Optional description",
  "cards": [
    {"front": "Question 1", "back": "Answer 1"},
    {"front": "Question 2", "back": "Answer 2"}
  ]
}
```

## Usage

```python
from utils.flashcard_loader import load_flashcards, FlashcardLoadError

try:
    cards = load_flashcards("data/my_cards.json")
    for card in cards:
        print(f"Q: {card['front']}")
        print(f"A: {card['back']}")
except FlashcardLoadError as e:
    print(f"Error loading flashcards: {e}")
```

## Error Handling

The loader provides friendly error messages without Python tracebacks:

- **File not found**: "File not found: path/to/file.json"
- **Malformed JSON**: "Invalid JSON in path/to/file.json: error details"
- **Missing fields**: "Card at index 2 is missing 'back' field"
- **Wrong types**: "Card at index 1: 'front' field must be a string"
- **Format errors**: "JSON must be an array or an object with a 'cards' field"

## Validation

The loader validates:
✓ JSON is valid and parseable
✓ Top-level structure is array or object with `cards` field
✓ All cards are objects
✓ Each card has `front` and `back` fields
✓ Both fields are strings (not numbers, arrays, or objects)
✓ Card index reported in error messages for debugging

## Running Tests

```bash
# Run flashcard loader tests
python -m pytest tests/test_flashcard_loader.py -v

# Run with coverage
python -m pytest tests/test_flashcard_loader.py --cov=utils.flashcard_loader
```

## Test Coverage

The test suite includes 21 tests covering:
- Valid array and object formats
- Empty datasets
- Unicode characters
- Malformed JSON
- Missing required fields
- Type validation
- Clear error messages without tracebacks
