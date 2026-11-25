"""Tests for the flashcard loader module."""

import json
import pytest

from utils.flashcard_loader import (
    FlashcardLoadError,
    load_flashcards,
)


class TestLoadFlashcardsArrayFormat:
    """Test loading flashcards in array format."""

    def test_load_valid_array_format(self, tmp_path):
        """Test loading valid array format JSON."""
        filepath = tmp_path / "cards.json"
        cards_data = [
            {"front": "What is 2+2?", "back": "4"},
            {"front": "Capital of France?", "back": "Paris"},
        ]
        filepath.write_text(json.dumps(cards_data))

        result = load_flashcards(filepath)

        assert len(result) == 2
        assert result[0]["front"] == "What is 2+2?"
        assert result[0]["back"] == "4"
        assert result[1]["front"] == "Capital of France?"
        assert result[1]["back"] == "Paris"

    def test_load_empty_array(self, tmp_path):
        """Test loading empty array."""
        filepath = tmp_path / "empty.json"
        filepath.write_text(json.dumps([]))

        result = load_flashcards(filepath)

        assert result == []

    def test_load_array_with_unicode(self, tmp_path):
        """Test loading array with unicode characters."""
        filepath = tmp_path / "unicode.json"
        cards_data = [
            {"front": "¿Hola?", "back": "Hello"},
            {"front": "日本語", "back": "Japanese"},
        ]
        filepath.write_text(
            json.dumps(cards_data, ensure_ascii=False), encoding="utf-8"
        )

        result = load_flashcards(filepath)

        assert len(result) == 2
        assert result[0]["front"] == "¿Hola?"
        assert result[1]["back"] == "Japanese"


class TestLoadFlashcardsObjectFormat:
    """Test loading flashcards in object format."""

    def test_load_valid_object_format(self, tmp_path):
        """Test loading valid object format JSON."""
        filepath = tmp_path / "cards.json"
        cards_data = {
            "cards": [
                {"front": "Q1", "back": "A1"},
                {"front": "Q2", "back": "A2"},
            ]
        }
        filepath.write_text(json.dumps(cards_data))

        result = load_flashcards(filepath)

        assert len(result) == 2
        assert result[0]["front"] == "Q1"
        assert result[1]["back"] == "A2"

    def test_load_object_with_extra_fields(self, tmp_path):
        """Test that extra fields in object wrapper are ignored."""
        filepath = tmp_path / "cards.json"
        cards_data = {
            "title": "My Deck",
            "description": "A test deck",
            "cards": [
                {"front": "Q", "back": "A"},
            ],
        }
        filepath.write_text(json.dumps(cards_data))

        result = load_flashcards(filepath)

        assert len(result) == 1
        assert result[0]["front"] == "Q"

    def test_load_object_with_empty_cards_array(self, tmp_path):
        """Test loading object format with empty cards array."""
        filepath = tmp_path / "empty.json"
        cards_data = {"cards": []}
        filepath.write_text(json.dumps(cards_data))

        result = load_flashcards(filepath)

        assert result == []


class TestErrorHandling:
    """Test error handling and validation."""

    def test_file_not_found(self):
        """Test error when file does not exist."""
        with pytest.raises(FlashcardLoadError, match="File not found"):
            load_flashcards("/nonexistent/path/cards.json")

    def test_malformed_json(self, tmp_path):
        """Test error on malformed JSON."""
        filepath = tmp_path / "bad.json"
        filepath.write_text("{invalid json")

        with pytest.raises(FlashcardLoadError, match="Invalid JSON"):
            load_flashcards(filepath)

    def test_json_is_string(self, tmp_path):
        """Test error when JSON is a string instead of array/object."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(json.dumps("not a valid format"))

        with pytest.raises(FlashcardLoadError, match="must be an array"):
            load_flashcards(filepath)

    def test_json_is_number(self, tmp_path):
        """Test error when JSON is a number."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(json.dumps(42))

        with pytest.raises(FlashcardLoadError, match="must be an array"):
            load_flashcards(filepath)

    def test_object_missing_cards_field(self, tmp_path):
        """Test error when object format doesn't have 'cards' field."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(json.dumps({"data": []}))

        with pytest.raises(FlashcardLoadError, match="'cards' field"):
            load_flashcards(filepath)

    def test_object_cards_not_array(self, tmp_path):
        """Test error when 'cards' field is not an array."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(json.dumps({"cards": "not an array"}))

        with pytest.raises(
            FlashcardLoadError, match="'cards' field must contain an array"
        ):
            load_flashcards(filepath)

    def test_card_is_not_dict(self, tmp_path):
        """Test error when a card is not an object."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(
            json.dumps(
                [
                    {"front": "Q", "back": "A"},
                    "invalid card",
                ]
            )
        )

        with pytest.raises(FlashcardLoadError, match="not an object"):
            load_flashcards(filepath)

    def test_card_missing_front_field(self, tmp_path):
        """Test error when card is missing 'front' field."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(
            json.dumps(
                [
                    {"back": "A"},
                ]
            )
        )

        with pytest.raises(FlashcardLoadError, match="'front' field"):
            load_flashcards(filepath)

    def test_card_missing_back_field(self, tmp_path):
        """Test error when card is missing 'back' field."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(
            json.dumps(
                [
                    {"front": "Q"},
                ]
            )
        )

        with pytest.raises(FlashcardLoadError, match="'back' field"):
            load_flashcards(filepath)

    def test_card_front_not_string(self, tmp_path):
        """Test error when 'front' field is not a string."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(
            json.dumps(
                [
                    {"front": 123, "back": "A"},
                ]
            )
        )

        with pytest.raises(FlashcardLoadError, match="'front' field must be a string"):
            load_flashcards(filepath)

    def test_card_back_not_string(self, tmp_path):
        """Test error when 'back' field is not a string."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(
            json.dumps(
                [
                    {"front": "Q", "back": ["A", "B"]},
                ]
            )
        )

        with pytest.raises(FlashcardLoadError, match="'back' field must be a string"):
            load_flashcards(filepath)

    def test_multiple_validation_errors_reports_first(self, tmp_path):
        """Test that validation reports the first error found."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(
            json.dumps(
                [
                    {"front": "Q1", "back": "A1"},
                    {"back": "A2"},  # Missing 'front'
                    {"front": "Q3"},  # Missing 'back'
                ]
            )
        )

        with pytest.raises(FlashcardLoadError, match="index 1"):
            load_flashcards(filepath)

    def test_error_message_includes_index(self, tmp_path):
        """Test that error message includes the card index."""
        filepath = tmp_path / "bad.json"
        filepath.write_text(
            json.dumps(
                [
                    {"front": "Q1", "back": "A1"},
                    {"front": "Q2", "back": "A2"},
                    {"front": "Q3"},  # Missing 'back' at index 2
                ]
            )
        )

        with pytest.raises(FlashcardLoadError, match="index 2"):
            load_flashcards(filepath)

    def test_readable_error_no_traceback(self, tmp_path, capsys):
        """Test that errors are caught and printed without Python traceback."""
        filepath = tmp_path / "bad.json"
        filepath.write_text("{invalid")

        try:
            load_flashcards(filepath)
        except FlashcardLoadError as e:
            print(f"Error loading flashcards: {e}")

        captured = capsys.readouterr()
        assert "Error loading flashcards:" in captured.out
        assert "Traceback" not in captured.out


class TestCardWithExtraFields:
    """Test handling of cards with extra fields."""

    def test_card_with_extra_fields_allowed(self, tmp_path):
        """Test that cards with extra fields load (extra fields ignored)."""
        filepath = tmp_path / "cards.json"
        cards_data = [
            {"front": "Q", "back": "A", "difficulty": "hard", "topic": "Math"},
        ]
        filepath.write_text(json.dumps(cards_data))

        result = load_flashcards(filepath)

        assert len(result) == 1
        assert result[0]["front"] == "Q"
        assert result[0]["back"] == "A"
