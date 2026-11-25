"""Entry point for the Flashcard Quizzer CLI application."""

import argparse
import difflib
import sys
from typing import Any, Literal, cast

from utils.flashcard_loader import FlashcardLoadError, load_flashcards
from utils.quiz_engine import QuizModeFactory


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_colored(text: str, color: str) -> None:
    """Print text in a specified color."""
    print(f"{color}{text}{Colors.RESET}")


def print_header(text: str) -> None:
    """Print a colored header."""
    print_colored(f"\n{'=' * 60}", Colors.BLUE)
    print_colored(text, Colors.BOLD + Colors.BLUE)
    print_colored(f"{'=' * 60}\n", Colors.BLUE)


def check_answer(user_answer: str, correct_answer: str) -> bool:
    """Check if user answer matches correct answer (lenient matching).

    Uses multiple strategies:
    1. Exact match (case-insensitive)
    2. Word-based match (all user words in correct answer, min 2 chars)
    3. Fuzzy similarity (50%+ match, min 2 chars)
    """
    import re

    user_clean = user_answer.lower().strip()
    correct_clean = correct_answer.lower().strip()

    if user_clean == correct_clean:
        return True

    min_length = 2
    if len(user_clean) < min_length:
        return False

    def extract_words(text):
        """Extract words, removing punctuation."""
        text = text.replace("'", "").replace('"', "")
        words = re.findall(r"\w+", text)
        return set(words)

    user_words = extract_words(user_clean)
    correct_words = extract_words(correct_clean)
    if user_words and user_words.issubset(correct_words):
        return True

    similarity = difflib.SequenceMatcher(None, user_clean, correct_clean).ratio()
    return similarity >= 0.5


def run_quiz(
    mode_name: Literal["sequential", "random", "adaptive"],
    cards: list[dict[str, Any]],
    show_stats: bool = False,
) -> None:
    """Run the quiz in the specified mode.

    Args:
        mode_name: The quiz mode ('sequential', 'random', or 'adaptive').
        cards: List of flashcard dictionaries.
        show_stats: Whether to show stats after each question.
    """
    quiz = QuizModeFactory.create(mode_name, cards)
    print_header(f"Flashcard Quizzer - {mode_name.capitalize()} Mode")
    print("Type 'exit' or press Ctrl+C to quit.\n")

    question_number = 1
    while True:
        card = quiz.get_next_card()
        if not card:
            break

        print(f"Question {question_number}/{len(quiz.cards)}")
        print(f"Q: {card.front}")

        while True:
            try:
                user_answer = input("Your answer (or 'exit'): ").strip()
            except KeyboardInterrupt:
                print_colored("\n\nQuiz interrupted.", Colors.YELLOW)
                return

            if user_answer.lower() == "exit":
                print_colored("\nQuiz exited.", Colors.YELLOW)
                return

            if not user_answer:
                print("Please enter an answer or type 'exit' to quit.")
                continue

            break

        correct = check_answer(user_answer, card.back)
        quiz.record_answer(correct)

        if correct:
            print_colored("✓ Correct!", Colors.GREEN)
        else:
            answer_text = f"✗ Incorrect. The answer is: {card.back}"
            print_colored(answer_text, Colors.RED)

        if show_stats:
            stats = quiz.get_stats()
            if stats["total"] > 0:
                accuracy = 100 * stats["correct"] // stats["total"]
            else:
                accuracy = 0
            print(
                f"Stats: {stats['correct']}/{stats['total']} correct " f"({accuracy}%)"
            )

        print()
        question_number += 1

    print_header("Quiz Complete!")
    stats = quiz.get_stats()
    if stats["total"] > 0:
        accuracy = 100 * stats["correct"] // stats["total"]
    else:
        accuracy = 0
    print(f"Total Questions: {stats['total']}")
    print_colored(f"Correct: {stats['correct']}", Colors.GREEN)
    print_colored(f"Incorrect: {stats['incorrect']}", Colors.RED)
    print(f"Accuracy: {accuracy}%\n")


def main() -> None:
    """Main entry point for the Flashcard Quizzer CLI."""
    parser = argparse.ArgumentParser(
        description="Flashcard Quizzer - Learn with spaced repetition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -f data/python_basics.json -m sequential
  python main.py -f data/math_facts.json -m adaptive --stats
  python main.py -f data/python_basics.json -m random
        """,
    )

    parser.add_argument(
        "-f",
        "--file",
        required=True,
        type=str,
        help="Path to JSON file containing flashcards",
    )

    parser.add_argument(
        "-m",
        "--mode",
        default="sequential",
        choices=["sequential", "random", "adaptive"],
        help="Quiz mode (default: sequential)",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics after each question",
    )

    args = parser.parse_args()

    try:
        cards = load_flashcards(args.file)
    except FlashcardLoadError as e:
        print_colored(f"Error loading flashcards: {e}", Colors.RED)
        sys.exit(1)

    if not cards:
        print_colored("No flashcards found in the file.", Colors.YELLOW)
        sys.exit(1)

    try:
        mode: Literal["sequential", "random", "adaptive"] = cast(
            Literal["sequential", "random", "adaptive"], args.mode
        )
        run_quiz(mode, cast(list[dict[str, Any]], cards), args.stats)
    except KeyboardInterrupt:
        print_colored("\n\nQuiz interrupted.", Colors.YELLOW)
        sys.exit(0)


if __name__ == "__main__":
    main()
