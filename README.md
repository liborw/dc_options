# dc_options

Dataclass-first configuration helpers with validation, metadata, argparse wiring, and documentation export. `dc_options` lets you describe nested option trees using familiar dataclasses while automatically generating CLIs, enforcing constraints, and producing Markdown/reference docs.

## Features
- Declarative configuration via dataclasses and an `option()` helper carrying labels, ranges, choices, and UI hints.
- Strict loading/saving from JSON using `dacite` with metadata validation baked in.
- Path-based getters/setters (`cfg.get("training.lr")`) for ergonomic CLI or scripting overrides.
- Argparse integration that maps metadata to command-line flags.
- Documentation export using Jinja2 templates so UI teams and docs stay synced with code.

## Project Layout
```
dc_options/         Core package (Options base class, metadata helper, docs template)
examples/           Minimal usage sample for experimentation
tests/              Pytest suites covering dump, path helpers, validation, etc.
pyproject.toml      uv/PEP 621 project definition
AGENTS.md           Contributor guide and workflow expectations
```

## Getting Started
```bash
uv sync                             # install deps in .venv
uv run python examples/minimal.py   # inspect nested configs & path helpers
uv run python examples/argparse_example.py --serve.port 9090 --workers 4
uv run pytest tests -q              # run the test suite
```

To pull configuration from JSON or args:
```python
from dc_options import Options, option

@dataclass
class Train(Options):
    epochs: int = option(default=10, min=1, label="Epochs")

cfg = Train.load("train.json")
cfg.validate()
parser = Train.build_argparser()
cfg.apply_cli_overrides(parser.parse_args())
```

## Examples
- `examples/minimal.py` shows nested option classes, validation, and `get`/`set` helpers that operate on dot paths.
- `examples/argparse_example.py` demonstrates combining JSON loading with CLI overrides using `build_argparser`.

## Documentation
- Update option metadata before exporting docs; the default template lives in `dc_options/docs_template.md.j2`.
- Generate fresh docs with `uv run python - <<'PY' ... Options.export_docs(...)`.
- Preview site content through MkDocs (`mkdocs serve`) if documentation is published.

## Contributing
Follow `AGENTS.md` for project structure tips, coding style, testing expectations, and git hygiene. Every feature or fix should ship with regression tests and refreshed docs whenever CLI behavior or configuration metadata changes.
