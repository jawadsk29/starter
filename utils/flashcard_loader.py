"""Load and validate flashcard data from JSON files.

Supports two JSON formats:
- Array format: [{"front": "...", "back": "..."}]
- Object format: {"cards": [{"front": "...", "back": "..."}]}
"""

import json
from pathlib import Path
from typing import Any, TypedDict


class FlashcardDict(TypedDict):
    """Type definition for a flashcard with front and back fields."""

    front: str
    back: str


class FlashcardLoadError(Exception):
    """Raised when flashcard data cannot be loaded or is invalid."""

    pass


def load_flashcards(filepath: str | Path) -> list[FlashcardDict]:
    """Load and validate flashcards from a JSON file.

    Args:
        filepath: Path to the JSON file containing flashcard data.

    Returns:
        A list of validated flashcard dictionaries.

    Raises:
        FlashcardLoadError: If the file cannot be read, JSON is malformed,
                           or required fields are missing.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FlashcardLoadError(f"File not found: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        msg = (
            f"Invalid JSON in {filepath}: {e.msg} at "
            f"line {e.lineno}, column {e.colno}"
        )
        raise FlashcardLoadError(msg) from e
    except (IOError, OSError) as e:
        raise FlashcardLoadError(f"Error reading {filepath}: {e}") from e

    cards = _extract_cards(data)
    _validate_cards(cards, filepath)

    return cards


def _extract_cards(data: Any) -> list[Any]:
    """Extract cards from either array or object format.

    Args:
        data: The parsed JSON data.

    Returns:
        A list of card objects.

    Raises:
        FlashcardLoadError: If the format is invalid or unexpected.
    """
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        if "cards" not in data:
            raise FlashcardLoadError(
                "Object format must have a 'cards' field containing an array"
            )
        cards = data["cards"]
        if not isinstance(cards, list):
            raise FlashcardLoadError("The 'cards' field must contain an array")
        return cards
    else:
        raise FlashcardLoadError(
            "JSON must be an array or an object with a 'cards' field"
        )


def _validate_cards(cards: list[Any], filepath: Path) -> None:
    """Validate that all cards have required fields.

    Args:
        cards: List of card objects to validate.
        filepath: Path to the source file (for error messages).

    Raises:
        FlashcardLoadError: If any card is missing required fields.
    """
    if not isinstance(cards, list):
        raise FlashcardLoadError("Cards must be in an array")

    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            raise FlashcardLoadError(f"Card at index {index} is not an object")

        if "front" not in card:
            raise FlashcardLoadError(f"Card at index {index} is missing 'front' field")

        if "back" not in card:
            raise FlashcardLoadError(f"Card at index {index} is missing 'back' field")

        if not isinstance(card["front"], str):
            raise FlashcardLoadError(
                f"Card at index {index}: 'front' field must be a string"
            )

        if not isinstance(card["back"], str):
            raise FlashcardLoadError(
                f"Card at index {index}: 'back' field must be a string"
            )
