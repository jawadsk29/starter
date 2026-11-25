# AI-Assisted Development Project Report

**Student Name:** Jawad Kabir  
**Project Title:** Flashcard Quizzer - AI-Assisted CLI Application  
**Date:** November 24, 2026

---

## Executive Summary

This project demonstrates effective collaboration with AI to build a fully-functional Flashcard Quizzer—a command-line application that loads JSON flashcard decks and provides three distinct quiz modes (sequential, random, and adaptive). Using AI assistance strategically for architecture and implementation, combined with rigorous testing and human judgment for edge cases, produced clean, maintainable code meeting all requirements. The application achieved 100% test coverage, passes all code quality checks (black, flake8, mypy), and demonstrates how AI is most effective as a tool for thinking through design rather than blindly generating code.

## Project Overview

### Problem Statement

Traditional flashcard apps use the same card order repeatedly, enabling memorization by position rather than learning content. Users need flexibility—some prefer sequential study, others want randomization, and many benefit from adaptive learning that focuses on weak areas.

### Solution Approach

I built a modular Python CLI using three key patterns:

1. **Strategy Pattern**: Each quiz mode is a separate strategy implementing the same interface
2. **Factory Pattern**: `QuizModeFactory` creates appropriate mode instances, decoupling the CLI from implementations
3. **Separation of Concerns**: Three independent modules (loader, engine, CLI) handle distinct responsibilities

### Implemented Features

- Load flashcards from JSON in two formats (array and object)
- Three quiz modes: Sequential, Random, and Adaptive
- Lenient answer validation (substring, word-based, fuzzy matching)
- Color-coded terminal output with real-time statistics
- Comprehensive error handling with helpful messages
- Full type hints and 64 passing unit tests with 100% coverage

## AI Collaboration Experience

### Workflow

My most effective approach was:
1. Ask AI for high-level architectural guidance before coding
2. Have AI generate implementation code
3. Review all code, run tests, identify edge cases
4. Iterate on AI suggestions rather than accepting verbatim
5. Document decisions and rationale in the AI edit log

### Most Valuable AI Interactions

**Architecture Design**: Initial prompt asked AI to recommend patterns for multiple quiz modes and two JSON formats. AI suggested Strategy + Factory patterns, which proved excellent. This upfront design saved significant refactoring.

**Answer Checking**: User answers need flexibility (typos, partial answers should be accepted). AI suggested multi-strategy approach: exact → substring → word-based → fuzzy matching. Implementation was straightforward and users found it intuitive.

**Adaptive Mode Logic**: This mode must show all cards once, track incorrect ones, then retry them—but only if not all were wrong. AI provided the basic algorithm; I added an override to `record_answer()` to prevent double-queueing during retry phase. This edge case surfaced during testing.

**JSON Format Handling**: Supporting two formats required extracting from both arrays and nested objects. AI suggested helper functions `_extract_cards()` and `_validate_cards()`, which I implemented with enhanced error messages including JSON line/column info.

**CLI Interface**: AI suggested `argparse`, helper functions for colored output, and a wrapper function for the quiz loop. I added the `--stats` flag and improved visual hierarchy with bold headers.

### Key Learnings

- **Architecture first**: Spending time on design patterns upfront meant implementation was straightforward
- **Testing catches edge cases**: AI suggestions were generally sound but missed some edge cases only tests revealed
- **Iteration matters**: Treating AI suggestions as starting points rather than final answers improved quality significantly
- **Type hints are documentation**: Coupling them with validation makes intent clear to future readers

## Software Engineering Practices

### Code Quality

All code meets professional standards:
- **Black formatting**: ✓ All files formatted
- **flake8 linting**: ✓ 0 violations
- **mypy type checking**: ✓ 0 errors (with proper type hints throughout)
- **pytest**: ✓ 64 tests passing with 100% coverage

### Testing Strategy

Comprehensive test suite covering:
- Both JSON formats (array and object)
- Error handling (malformed JSON, missing fields, type errors)
- All three quiz modes and their state transitions
- Edge cases (empty decks, all correct/incorrect scenarios)
- Unicode character support

### Design Patterns

**Strategy Pattern**: `QuizMode` abstract base class with three concrete implementations (`SequentialMode`, `RandomMode`, `AdaptiveMode`). Each strategy determines card ordering independently.

**Factory Pattern**: `QuizModeFactory.create()` instantiates the appropriate mode without coupling the CLI to mode implementations. Easy to add new modes.

## Technical Challenges

### Challenge 1: Type System Complexity

The codebase had a naming conflict: `flashcard_loader.py` defined `Flashcard` as a TypedDict, while `quiz_engine.py` defined it as a class. This confused mypy's type checker.

**Solution**: Renamed the TypedDict to `FlashcardDict`, keeping the class name for the actual objects. Added proper type annotations throughout.

### Challenge 2: Adaptive Mode Retry Logic

Initial implementation queued cards for retry every time they were answered incorrectly, causing some cards to appear multiple times.

**Solution**: Override `record_answer()` to only queue cards during the first pass, not during retry phase. Tests verified the fix.

### Challenge 3: Answer Validation Balance

Too-strict matching rejected valid answers ("Paris" vs. "Capital of France is Paris"); too-lenient matched nonsense.

**Solution**: Multi-strategy approach with progressive looseness: exact → substring → word-based → fuzzy (50%+ similarity). Testing confirmed it handles edge cases gracefully.

## Code Quality Metrics

| Metric | Result |
|--------|--------|
| Lines of Production Code | 530 |
| Test Code Lines | 300 |
| Test Count | 64 |
| Test Coverage | 100% |
| Black | ✓ Passes |
| flake8 | ✓ 0 violations |
| mypy | ✓ 0 errors |

## Learning Outcomes

### Technical Skills

- Deepened understanding of Python type system and TypedDict
- Practical experience implementing Strategy and Factory patterns
- Learned to test file I/O with temporary files and fixtures
- Built user-friendly CLI with ANSI color codes

### AI Collaboration Skills

- Effective prompting requires specific context, not vague requests
- Code review discipline is essential—test before accepting AI suggestions
- AI excels at architecture and boilerplate; human judgment needed for edge cases
- Iteration improves outcomes significantly

### Software Engineering Insights

- Design patterns communicate intent to future maintainers
- Tests document expected behavior as well as provide regression protection
- Error messages matter—users see them more than code
- Separation of concerns makes code testable and maintainable

## Reflection

### What Worked Well

Starting with architecture before coding proved invaluable. Comprehensive testing from the beginning caught edge cases that manual code review would miss. Clear prompts with specific context generated better AI suggestions than vague requests.

### Areas for Improvement

Could have discussed testing strategy with AI more systematically before implementation. Would have benefited from stronger emphasis on edge cases in AI prompts. More explicit code reviews using AI feedback would have improved iterative refinement.

### Future Enhancements

Would add: persistence for tracking progress across sessions, spaced repetition algorithm, performance metrics per card, and deck management tools. Possible to implement Quizlet/AnkiWeb integration for fetching decks online.

## Conclusion

This project demonstrates that AI-assisted development is most effective when combining AI's strengths (architecture, boilerplate, suggestions) with human judgment (testing, edge cases, iteration, design decisions). The Flashcard Quizzer is production-ready code built with clean architecture, comprehensive testing, and thoughtful human oversight.

My understanding of AI-assisted development evolved from "write code faster" to "think at a higher level while AI handles implementation details." The best use case is architecture + design, then human review and iteration. AI amplifies thoughtful engineering; it's not a replacement for critical thinking.

---

## Appendices

**Appendix A: AI Interaction Log**  
See `ai_edit_log.md` for complete documentation of 5+ AI interactions with prompts, responses, and decision-making rationale.

**Appendix B: Test Results**
- 64 tests passed
- 100% code coverage
- All quality checks passing

---

**Word Count:** 1,350 words
