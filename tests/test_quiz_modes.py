"""Tests for quiz engine modes and factory."""

import pytest

from utils.quiz_engine import (
    AdaptiveMode,
    Flashcard,
    QuizModeFactory,
    RandomMode,
    SequentialMode,
)


@pytest.fixture
def sample_cards():
    """Sample flashcard data for testing."""
    return [
        {"front": "Q1", "back": "A1"},
        {"front": "Q2", "back": "A2"},
        {"front": "Q3", "back": "A3"},
    ]


class TestFlashcard:
    """Test the Flashcard class."""

    def test_flashcard_creation(self):
        """Test creating a flashcard."""
        card = Flashcard("Question", "Answer")
        assert card.front == "Question"
        assert card.back == "Answer"
        assert card.attempts == 0
        assert card.correct == 0

    def test_record_correct_answer(self):
        """Test recording a correct answer."""
        card = Flashcard("Q", "A")
        card.record_answer(True)
        assert card.attempts == 1
        assert card.correct == 1
        assert card.accuracy == 1.0

    def test_record_incorrect_answer(self):
        """Test recording an incorrect answer."""
        card = Flashcard("Q", "A")
        card.record_answer(False)
        assert card.attempts == 1
        assert card.correct == 0
        assert card.accuracy == 0.0

    def test_mixed_answers(self):
        """Test accuracy with mixed correct and incorrect answers."""
        card = Flashcard("Q", "A")
        card.record_answer(True)
        card.record_answer(False)
        card.record_answer(True)
        assert card.attempts == 3
        assert card.correct == 2
        assert card.accuracy == pytest.approx(2 / 3)

    def test_initial_accuracy(self):
        """Test that unattempted cards have 100% accuracy."""
        card = Flashcard("Q", "A")
        assert card.accuracy == 1.0


class TestSequentialMode:
    """Test SequentialMode."""

    def test_sequential_mode_creation(self, sample_cards):
        """Test creating sequential mode."""
        mode = SequentialMode(sample_cards)
        assert len(mode.cards) == 3
        assert mode.current_index == 0

    def test_sequential_mode_order(self, sample_cards):
        """Test that cards are served in order."""
        mode = SequentialMode(sample_cards)

        card1 = mode.get_next_card()
        assert card1 is not None
        assert card1.front == "Q1"

        card2 = mode.get_next_card()
        assert card2 is not None
        assert card2.front == "Q2"

        card3 = mode.get_next_card()
        assert card3 is not None
        assert card3.front == "Q3"

        card4 = mode.get_next_card()
        assert card4 is None

    def test_sequential_mode_reset(self, sample_cards):
        """Test resetting sequential mode."""
        mode = SequentialMode(sample_cards)

        mode.get_next_card()
        mode.get_next_card()
        mode.reset()

        assert mode.current_index == 0
        card = mode.get_next_card()
        assert card.front == "Q1"


class TestRandomMode:
    """Test RandomMode."""

    def test_random_mode_creation(self, sample_cards):
        """Test creating random mode."""
        mode = RandomMode(sample_cards)
        assert len(mode.cards) == 3

    def test_random_mode_shuffled(self, sample_cards):
        """Test that random mode shuffles cards."""
        original_order = [card["front"] for card in sample_cards]

        mode = RandomMode(sample_cards)
        shuffled_order = [card.front for card in mode.cards]

        assert set(shuffled_order) == set(original_order)

    def test_random_mode_completes(self, sample_cards):
        """Test that random mode serves all cards."""
        mode = RandomMode(sample_cards)
        cards_served = []

        while True:
            card = mode.get_next_card()
            if card is None:
                break
            cards_served.append(card.front)

        assert len(cards_served) == 3
        assert set(cards_served) == {"Q1", "Q2", "Q3"}


class TestAdaptiveMode:
    """Test AdaptiveMode."""

    def test_adaptive_mode_creation(self, sample_cards):
        """Test creating adaptive mode."""
        mode = AdaptiveMode(sample_cards)
        assert len(mode.cards) == 3
        assert len(mode.incorrect_cards) == 0

    def test_adaptive_mode_prioritizes_incorrect(self, sample_cards):
        """Test that adaptive mode prioritizes incorrect answers."""
        mode = AdaptiveMode(sample_cards)

        _ = mode.get_next_card()
        mode.record_answer(False)

        _ = mode.get_next_card()
        mode.record_answer(True)

        _ = mode.get_next_card()
        mode.record_answer(False)

        assert len(mode.incorrect_cards) == 2

        next_card = mode.get_next_card()
        assert next_card is not None
        assert next_card.front == "Q1"

    def test_adaptive_mode_correct_answer_stops_retry(self, sample_cards):
        """Test that correct answer removes card from retry queue."""
        mode = AdaptiveMode(sample_cards)

        _ = mode.get_next_card()
        mode.record_answer(False)

        _ = mode.get_next_card()
        mode.record_answer(True)

        _ = mode.get_next_card()
        mode.record_answer(False)

        incorrect_card = mode.get_next_card()
        mode.record_answer(True)

        assert incorrect_card.front == "Q1"
        assert len(mode.incorrect_cards) == 1

    def test_adaptive_mode_full_session(self, sample_cards):
        """Test a full adaptive mode session."""
        mode = AdaptiveMode(sample_cards)
        cards_served = []

        for _ in range(10):
            card = mode.get_next_card()
            if card is None:
                break
            cards_served.append(card.front)
            if card.front == "Q1":
                mode.record_answer(False)
            else:
                mode.record_answer(True)

        assert "Q1" in cards_served
        assert cards_served.count("Q1") >= 2


class TestQuizModeBase:
    """Test QuizMode base class behavior."""

    def test_stats_initialization(self, sample_cards):
        """Test that stats are initialized correctly."""
        mode = SequentialMode(sample_cards)
        stats = mode.get_stats()
        assert stats["correct"] == 0
        assert stats["incorrect"] == 0
        assert stats["total"] == 0

    def test_stats_tracking(self, sample_cards):
        """Test that stats are tracked correctly."""
        mode = SequentialMode(sample_cards)

        mode.get_next_card()
        mode.record_answer(True)

        mode.get_next_card()
        mode.record_answer(False)

        stats = mode.get_stats()
        assert stats["correct"] == 1
        assert stats["incorrect"] == 1
        assert stats["total"] == 2

    def test_reset_stats(self, sample_cards):
        """Test that reset clears stats."""
        mode = SequentialMode(sample_cards)

        mode.get_next_card()
        mode.record_answer(True)

        mode.reset()

        stats = mode.get_stats()
        assert stats["correct"] == 0
        assert stats["incorrect"] == 0
        assert stats["total"] == 0


class TestQuizModeFactory:
    """Test QuizModeFactory."""

    def test_factory_creates_sequential(self, sample_cards):
        """Test factory creates sequential mode."""
        mode = QuizModeFactory.create("sequential", sample_cards)
        assert isinstance(mode, SequentialMode)

    def test_factory_creates_random(self, sample_cards):
        """Test factory creates random mode."""
        mode = QuizModeFactory.create("random", sample_cards)
        assert isinstance(mode, RandomMode)

    def test_factory_creates_adaptive(self, sample_cards):
        """Test factory creates adaptive mode."""
        mode = QuizModeFactory.create("adaptive", sample_cards)
        assert isinstance(mode, AdaptiveMode)

    def test_factory_invalid_mode(self, sample_cards):
        """Test factory raises error for invalid mode."""
        with pytest.raises(ValueError, match="Unknown mode"):
            QuizModeFactory.create("invalid", sample_cards)

    def test_factory_available_modes(self):
        """Test factory returns list of available modes."""
        modes = QuizModeFactory.available_modes()
        assert "sequential" in modes
        assert "random" in modes
        assert "adaptive" in modes
        assert len(modes) == 3

    def test_factory_modes_work(self, sample_cards):
        """Test that factory-created modes work correctly."""
        for mode_name in QuizModeFactory.available_modes():
            mode = QuizModeFactory.create(mode_name, sample_cards)
            card = mode.get_next_card()
            assert card is not None
            assert hasattr(card, "front")
            assert hasattr(card, "back")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_cards_list(self):
        """Test with empty cards list."""
        mode = SequentialMode([])
        assert mode.get_next_card() is None

    def test_single_card(self):
        """Test with single card."""
        cards = [{"front": "Q", "back": "A"}]
        mode = SequentialMode(cards)

        card1 = mode.get_next_card()
        assert card1 is not None
        assert card1.front == "Q"

        card2 = mode.get_next_card()
        assert card2 is None

    def test_duplicate_cards(self):
        """Test with duplicate cards."""
        cards = [
            {"front": "Q", "back": "A"},
            {"front": "Q", "back": "A"},
        ]
        mode = SequentialMode(cards)

        card1 = mode.get_next_card()
        card2 = mode.get_next_card()

        assert card1 is not None
        assert card2 is not None
        assert card1.front == card2.front
