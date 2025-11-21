# Repository Guidelines

## Project Structure & Module Organization
Core source lives in `dc_options/`: `options.py` exposes the `Options` base class, `metadata.py` defines the `option()` helper, and `docs_template.md.j2` renders configuration docs. `examples/minimal.py` demonstrates how downstream apps define concrete option trees. Tests are grouped in `tests/` (`test_dump.py`, `test_paths.py`, etc.) and should mirror the module they verify. Project-level settings such as `pyproject.toml` and `mkdocs.yml` stay at the workspace root, while generated docs belong under `docs/` folders created by contributors.

## Build, Test, and Development Commands
- `uv sync`: install or update dependencies declared in `pyproject.toml`.
- `uv pip install --editable .`: expose the package as `dc_options` inside the virtual environment for ad‑hoc local work.
- `uv run pytest tests -q`: execute the full suite; combine with `-k name` for targeted runs.
- `uv run python examples/minimal.py`: sanity-check the sample configuration and metadata wiring.
- `uv run python - <<'PY' ... PY`: handy for one-off scripts (e.g., calling `Options.export_docs` to refresh rendered documentation).

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indents, expressive type hints, and snake_case identifiers for fields (`time_step`). Configuration dataclasses inherit from `Options` and use PascalCase (`RenderingOptions`). Every tunable value must wrap the field with `option(...)` metadata so validation, CLI flags, and docs remain aligned. Keep helper functions side-effect-free; when mutation is required, encapsulate it inside clearly named instance methods.

## Testing Guidelines
Pytest discovers files named `test_*.py`; keep new tests in the existing suite to ensure coverage stays centralized. Each bug fix should ship with a regression test targeting the affected behavior (validation errors, CLI parsing, dumping order, etc.). Prefer parametrized tests for metadata scenarios (min/max, choices). Run `uv run pytest tests -q` before pushing and capture failures that indicate missing constraints or doc drift.

## Commit & Pull Request Guidelines
Craft imperative, present-tense commit subjects (e.g., `feat: extend path setter errors`) and keep related changes grouped tightly. Reference GitHub/issue IDs in the body when applicable. Pull requests need a problem statement, summary of changes, test evidence (`uv run pytest -q`), and screenshots or snippets if docs or CLI output changed. Ensure CI is green, requested reviews are addressed, and documentation/regression gaps are noted before merging.

### Git Commits
- Commit only complete, tested features or fixes; avoid mixing unrelated refactors with functional changes.
- Prefer small, reviewable commits that explain why the change exists; include context in the body if the diff isn’t obvious.
- Keep the branch history clean by rebasing before opening a PR and resolve conflicts locally to prevent noisy merge commits.

## Documentation & Metadata Tips
Treat metadata as source: double-check `min`, `max`, `choices`, and labels before exporting docs. Regenerate Markdown via a short `uv run python` snippet calling `Options.export_docs`, then preview with `mkdocs serve` if documentation is published. Keep templates generic so downstream consumers can reuse them without editing framework internals, and avoid project-specific jargon inside shared helpers.
