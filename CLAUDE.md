# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

threaded-context — a thread-safe context manager library for Python (>=3.9) with nested context inheritance and conflict resolution strategies. Single-module library, zero runtime dependencies, managed with Poetry.

## Commands

```bash
make test          # run tests (poetry run pytest)
make lint          # pycodestyle, black, flake8, pylint, mypy
make build         # clean + lint + test + poetry build
make clean         # rm build artifacts and caches

# run a single test
poetry run pytest tests.py::ThreadedContextTestCase::test_base

# release (bumps version, commits, tags — does NOT push)
make release-patch
make release-minor
make release-major

# publish to PyPI (runs build first)
make publish
```

## Architecture

Single file library (`threaded_context.py`) using `threading.local()` for thread-safe storage. Contexts form a parent chain — each `ThreadedContext` stores a reference to its parent and `get_current_context()` walks the chain upward to merge values.

**Context classes and value precedence:**
- `ThreadedContext` — strong: this level's values win over children's
- `WeakThreadedContext` — weak: children can override this level's values
- `BrutalThreadedContext` — strong + forcefully overrides parent values
- `WeakBrutalThreadedContext` — weak + forcefully overrides parent values

All context classes work as both context managers and decorators (via `ContextDecorator`).

**Public API:** `get_current_context()`, `reset_context()`, `update_current_context()`.

## Build Configuration

- `Makefile` is generic (designed to be reused across Poetry projects)
- `.vars.mk` holds project-specific config (`CODE`, `TEST_CMD`, linter flags)
- Some dev tools (black, pylint, pytest) have `python >= 3.10` markers in pyproject.toml; minimum supported runtime is 3.9

## Commit Style

Use conventional commits: `<type>(<scope>): <subject>`. No co-author lines.
