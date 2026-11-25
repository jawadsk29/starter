"""Integration tests for the full quiz workflow."""

import json
import tempfile
from pathlib import Path

import pytest

from utils.flashcard_loader import load_flashcards
from utils.quiz_engine import QuizModeFactory


@pytest.fixture
def sample_json_file():
    """Create a temporary JSON file with sample flashcards."""
    cards = [
        {"front": "What is 2+2?", "back": "4"},
        {"front": "What is the capital of France?", "back": "Paris"},
        {"front": "What is 10/2?", "back": "5"},
    ]

    tmp = Path(tempfile.gettempdir())
    filepath = tmp / "test_cards.json"
    filepath.write_text(json.dumps(cards))

    yield filepath
    filepath.unlink()


class TestFullSession:
    """Test full quiz sessions with different modes."""

    def test_full_session_sequential(self, sample_json_file):
        """Test a complete sequential mode session."""
        cards = load_flashcards(sample_json_file)
        quiz = QuizModeFactory.create("sequential", cards)

        answers = [
            (True, "4"),
            (False, "London"),
            (True, "5"),
        ]

        for expected_correct, answer in answers:
            card = quiz.get_next_card()
            assert card is not None
            is_correct = answer.lower() == card.back.lower()
            quiz.record_answer(is_correct)

        stats = quiz.get_stats()
        assert stats["total"] == 3
        assert stats["correct"] == 2
        assert stats["incorrect"] == 1

    def test_full_session_random(self, sample_json_file):
        """Test a complete random mode session."""
        cards = load_flashcards(sample_json_file)
        quiz = QuizModeFactory.create("random", cards)

        cards_served = []
        for _ in range(3):
            card = quiz.get_next_card()
            assert card is not None
            cards_served.append(card.front)
            quiz.record_answer(True)

        assert len(cards_served) == 3

        no_more_cards = quiz.get_next_card()
        assert no_more_cards is None

    def test_full_session_adaptive_with_retries(self, sample_json_file):
        """Test adaptive mode with incorrect answers triggering retries."""
        cards = load_flashcards(sample_json_file)
        quiz = QuizModeFactory.create("adaptive", cards)

        sequence = [
            (True, "4"),
            (False, "London"),
            (True, "5"),
            (True, "Paris"),
        ]

        cards_shown = []
        for expected_correct, answer in sequence:
            card = quiz.get_next_card()
            assert card is not None
            cards_shown.append(card.front)
            is_correct = answer.lower() == card.back.lower()
            quiz.record_answer(is_correct)

        assert len(cards_shown) >= 4
        assert cards_shown.count("What is the capital of France?") >= 2

    def test_stats_calculation_accuracy(self, sample_json_file):
        """Test that accuracy is calculated correctly."""
        cards = load_flashcards(sample_json_file)
        quiz = QuizModeFactory.create("sequential", cards)

        quiz.get_next_card()
        quiz.record_answer(True)

        quiz.get_next_card()
        quiz.record_answer(True)

        quiz.get_next_card()
        quiz.record_answer(False)

        stats = quiz.get_stats()
        assert stats["total"] == 3
        assert stats["correct"] == 2
        assert stats["incorrect"] == 1

    def test_multiple_reset_cycles(self, sample_json_file):
        """Test that quiz can be reset and run multiple times."""
        cards = load_flashcards(sample_json_file)
        quiz = QuizModeFactory.create("sequential", cards)

        for cycle in range(2):
            quiz.reset()
            quiz.get_next_card()
            quiz.record_answer(True)

            stats = quiz.get_stats()
            assert stats["total"] == 1
            assert stats["correct"] == 1


class TestDataIntegration:
    """Test integration between data loader and quiz engine."""

    def test_load_and_quiz_array_format(self, sample_json_file):
        """Test loading array format and running quiz."""
        cards = load_flashcards(sample_json_file)

        for mode_name in QuizModeFactory.available_modes():
            quiz = QuizModeFactory.create(mode_name, cards)

            card = quiz.get_next_card()
            assert card is not None
            assert hasattr(card, "front")
            assert hasattr(card, "back")

    def test_load_and_quiz_object_format(self):
        """Test loading object format and running quiz."""
        cards_data = {
            "title": "Test Deck",
            "cards": [
                {"front": "Q1", "back": "A1"},
                {"front": "Q2", "back": "A2"},
            ],
        }

        tmp = Path(tempfile.gettempdir())
        filepath = tmp / "test_object.json"
        filepath.write_text(json.dumps(cards_data))

        try:
            cards = load_flashcards(filepath)
            quiz = QuizModeFactory.create("sequential", cards)

            card = quiz.get_next_card()
            assert card is not None
            assert card.front == "Q1"
        finally:
            filepath.unlink()


class TestQuizWorkflow:
    """Test realistic quiz workflows."""

    def test_user_gets_all_correct(self, sample_json_file):
        """Test session where user gets all questions correct."""
        cards = load_flashcards(sample_json_file)
        quiz = QuizModeFactory.create("sequential", cards)

        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            quiz.record_answer(True)

        stats = quiz.get_stats()
        assert stats["correct"] == stats["total"]
        assert stats["incorrect"] == 0

    def test_user_gets_all_incorrect(self, sample_json_file):
        """Test session where user gets all questions incorrect."""
        cards = load_flashcards(sample_json_file)
        quiz = QuizModeFactory.create("sequential", cards)

        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            quiz.record_answer(False)

        stats = quiz.get_stats()
        assert stats["correct"] == 0
        assert stats["incorrect"] == stats["total"]

    def test_mixed_performance(self, sample_json_file):
        """Test session with mixed performance."""
        cards = load_flashcards(sample_json_file)
        quiz = QuizModeFactory.create("random", cards)

        results = [True, False, True]
        for expected_correct in results:
            card = quiz.get_next_card()
            if card:
                quiz.record_answer(expected_correct)

        stats = quiz.get_stats()
        assert stats["total"] == 3
        assert stats["correct"] == 2
        assert stats["incorrect"] == 1


class TestAdaptiveModeBehavior:
    """Test specific adaptive mode behaviors."""

    def test_adaptive_mode_repeats_incorrect_questions(self):
        """Test that adaptive mode actually repeats incorrect questions."""
        cards = [
            {"front": "Q1", "back": "A1"},
            {"front": "Q2", "back": "A2"},
            {"front": "Q3", "back": "A3"},
        ]

        quiz = QuizModeFactory.create("adaptive", cards)

        sequences = []
        for _ in range(10):
            card = quiz.get_next_card()
            if card is None:
                break
            sequences.append(card.front)
            if card.front == "Q1":
                quiz.record_answer(False)
            else:
                quiz.record_answer(True)

        q1_count = sequences.count("Q1")
        assert q1_count >= 2

    def test_adaptive_mode_does_not_repeat_correct_questions(self):
        """Test that adaptive mode doesn't retry correct answers."""
        cards = [
            {"front": "Q1", "back": "A1"},
            {"front": "Q2", "back": "A2"},
        ]

        quiz = QuizModeFactory.create("adaptive", cards)

        sequences = []
        for _ in range(5):
            card = quiz.get_next_card()
            if card is None:
                break
            sequences.append(card.front)
            quiz.record_answer(True)

        q1_count = sequences.count("Q1")
        q2_count = sequences.count("Q2")

        assert q1_count == 1
        assert q2_count == 1

    def test_adaptive_mode_prioritizes_recent_mistakes(self):
        """Test that adaptive mode prioritizes recently missed cards."""
        cards = [
            {"front": "Q1", "back": "A1"},
            {"front": "Q2", "back": "A2"},
            {"front": "Q3", "back": "A3"},
        ]

        quiz = QuizModeFactory.create("adaptive", cards)

        _ = quiz.get_next_card()
        quiz.record_answer(False)

        _ = quiz.get_next_card()
        quiz.record_answer(True)

        _ = quiz.get_next_card()
        quiz.record_answer(False)

        next_card = quiz.get_next_card()
        assert next_card is not None
        assert next_card.front == "Q1"


class TestEdgeConditions:
    """Test edge conditions in integration."""

    def test_empty_deck(self):
        """Test with empty deck."""
        cards = []
        quiz = QuizModeFactory.create("sequential", cards)

        card = quiz.get_next_card()
        assert card is None

    def test_very_large_deck(self):
        """Test with large number of cards."""
        cards = [{"front": f"Q{i}", "back": f"A{i}"} for i in range(1000)]
        quiz = QuizModeFactory.create("sequential", cards)

        count = 0
        while quiz.get_next_card():
            count += 1

        assert count == 1000

    def test_special_characters_in_cards(self):
        """Test cards with special characters."""
        cards = [
            {"front": "What is 2 × 3?", "back": "6"},
            {"front": "What is π?", "back": "3.14159..."},
            {"front": "Who said 'Hello'?", "back": "Someone"},
        ]

        quiz = QuizModeFactory.create("sequential", cards)

        for _ in range(3):
            card = quiz.get_next_card()
            assert card is not None
            quiz.record_answer(True)

        stats = quiz.get_stats()
        assert stats["total"] == 3
