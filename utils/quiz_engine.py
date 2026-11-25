"""Quiz engine implementing Strategy and Factory patterns.

Provides three quiz modes:
- SequentialMode: Questions in original order
- RandomMode: Shuffled questions
- AdaptiveMode: Prioritizes incorrect answers
"""

import random
from abc import ABC, abstractmethod
from typing import Literal, Type


class Flashcard:
    """Represents a single flashcard with tracking for adaptive mode."""

    def __init__(self, front: str, back: str):
        self.front = front
        self.back = back
        self.attempts = 0
        self.correct = 0

    def record_answer(self, is_correct: bool) -> None:
        """Record the result of an answer attempt."""
        self.attempts += 1
        if is_correct:
            self.correct += 1

    @property
    def accuracy(self) -> float:
        """Return accuracy as a percentage (0.0 to 1.0)."""
        if self.attempts == 0:
            return 1.0
        return self.correct / self.attempts


class QuizMode(ABC):
    """Abstract base class for quiz modes."""

    def __init__(self, cards: list[dict]):
        """Initialize with flashcard data.

        Args:
            cards: List of flashcard dictionaries with 'front' and 'back'.
        """
        self.cards = [Flashcard(card["front"], card["back"]) for card in cards]
        self.current_index = 0
        self.current_card: Flashcard | None = None
        self.stats = {"correct": 0, "incorrect": 0, "total": 0}

    @abstractmethod
    def get_next_card(self) -> Flashcard | None:
        """Get the next card to quiz the user on.

        Returns:
            The next Flashcard or None if quiz is complete.
        """
        pass

    def record_answer(self, is_correct: bool) -> None:
        """Record the user's answer to the current card."""
        if self.current_card is not None:
            self.current_card.record_answer(is_correct)
            self.stats["total"] += 1
            if is_correct:
                self.stats["correct"] += 1
            else:
                self.stats["incorrect"] += 1

    def reset(self) -> None:
        """Reset the quiz for a new session."""
        self.current_index = 0
        self.current_card = None
        for card in self.cards:
            card.attempts = 0
            card.correct = 0
        self.stats = {"correct": 0, "incorrect": 0, "total": 0}

    def get_stats(self) -> dict:
        """Return quiz statistics."""
        return self.stats.copy()


class SequentialMode(QuizMode):
    """Quiz mode: Questions in sequential order."""

    def get_next_card(self) -> Flashcard | None:
        """Get the next card in sequential order."""
        if self.current_index < len(self.cards):
            self.current_card = self.cards[self.current_index]
            self.current_index += 1
            return self.current_card
        return None


class RandomMode(QuizMode):
    """Quiz mode: Questions in random shuffled order."""

    def __init__(self, cards: list[dict]):
        """Initialize with shuffled card order."""
        super().__init__(cards)
        random.shuffle(self.cards)

    def get_next_card(self) -> Flashcard | None:
        """Get the next card in random order."""
        if self.current_index < len(self.cards):
            self.current_card = self.cards[self.current_index]
            self.current_index += 1
            return self.current_card
        return None


class AdaptiveMode(QuizMode):
    """Quiz mode: Prioritizes cards the user gets wrong."""

    def __init__(self, cards: list[dict]):
        """Initialize with all cards available."""
        super().__init__(cards)
        self.incorrect_cards: list[Flashcard] = []
        self.in_retry_phase = False

    def get_next_card(self) -> Flashcard | None:
        """Get next card, prioritizing incorrect answers.

        Strategy:
        1. First pass: serve all cards in order, track incorrect
        2. After first pass: if some (not all) cards were incorrect, retry them
        3. Stop when all cards shown or all retries exhausted
        """
        if self.in_retry_phase:
            if self.incorrect_cards:
                self.current_card = self.incorrect_cards.pop(0)
                return self.current_card
            return None

        if self.current_index < len(self.cards):
            self.current_card = self.cards[self.current_index]
            self.current_index += 1
            return self.current_card

        self.in_retry_phase = True
        all_incorrect = len(self.incorrect_cards) >= len(self.cards)
        if self.incorrect_cards and not all_incorrect:
            self.current_card = self.incorrect_cards.pop(0)
            return self.current_card

        return None

    def record_answer(self, is_correct: bool) -> None:
        """Record answer and add to retry queue if incorrect."""
        super().record_answer(is_correct)

        if self.current_card and not is_correct and not self.in_retry_phase:
            self.incorrect_cards.append(self.current_card)

    def reset(self) -> None:
        """Reset the quiz for a new session."""
        super().reset()
        self.incorrect_cards = []
        self.in_retry_phase = False


class QuizModeFactory:
    """Factory for creating quiz mode instances."""

    _modes: dict[str, Type[QuizMode]] = {
        "sequential": SequentialMode,
        "random": RandomMode,
        "adaptive": AdaptiveMode,
    }

    @classmethod
    def create(
        cls,
        mode: Literal["sequential", "random", "adaptive"],
        cards: list[dict],
    ) -> QuizMode:
        """Create a quiz mode instance.

        Args:
            mode: The quiz mode name ('sequential', 'random', or 'adaptive').
            cards: List of flashcard dictionaries.

        Returns:
            An instance of the requested QuizMode subclass.

        Raises:
            ValueError: If the mode is not recognized.
        """
        if mode not in cls._modes:
            modes = ", ".join(cls._modes.keys())
            raise ValueError(f"Unknown mode: {mode}. Choose from: {modes}")
        return cls._modes[mode](cards)

    @classmethod
    def available_modes(cls) -> list[str]:
        """Return list of available mode names."""
        return list(cls._modes.keys())
