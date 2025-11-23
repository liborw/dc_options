# dc_options

Dataclass-first configuration helpers with validation, metadata, argparse wiring, and documentation export. `dc_options` lets you describe nested option trees using familiar dataclasses while automatically generating CLIs, enforcing constraints, and producing Markdown/reference docs.

## Features
- Declarative configuration via dataclasses and an `option()` helper carrying labels, ranges, choices, and UI hints.
- Built-in JSON load/save with optional per-field serialize/deserialize hooks.
- Path-based getters/setters (`cfg.get("training.lr")`) for ergonomic CLI or scripting overrides.
- Argparse integration that maps metadata to command-line flags.
- Documentation export using Jinja2 templates so UI teams and docs stay synced with code.
- Whole-structure validation that reports every issue in a single `ValidationError` report.

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
- Custom validation is possible by overriding `collect_validation_errors`. For example:
  ```python
  @dataclass
  class Flags(Options):
      enable_a: bool = option(default=False)
      enable_b: bool = option(default=False)

      def collect_validation_errors(self):
          issues = super().collect_validation_errors()
          if self.enable_a and self.enable_b:
              issues.append(ValidationIssue("enable_b", "cannot be true when enable_a is true"))
          return issues
  ```
  Calling `Flags(enable_a=True, enable_b=True).validate()` now raises a `ValidationError` listing both built-in and custom issues so users can fix everything in one pass.

## Documentation
- Update option metadata before exporting; the built-in templates live under `dc_options/templates/`.
- Use `dc_options.rendering.render_options` / `export_options` to produce plain text or markdown views; pass custom template paths when needed.
- Preview site content through MkDocs (`mkdocs serve`) if documentation is published.

## Metadata Reference
- `label` / `description` – available for every field; provide human-readable names and context.
- `editable` – all field types; mark values that should be read-only in generated UIs.
- `required` – mark fields that must not be `None`.
- `range`, `step` – numeric fields (`int`/`float`); `range=(min, max)` constrains bounds while `step` guides UI controls.
- `choices`, `labels` – enumerations (`str`, `int`, etc.); specify allowed values and friendly labels. Set `choice_strict=False` to permit values outside the provided list.
- `default`, `default_factory` – all fields; stored in metadata for resets or documentation.
- `serialize`, `deserialize` – scalar fields; callables that map custom objects (e.g., `Path`) to/from JSON-safe data.

## Contributing
Follow `AGENTS.md` for project structure tips, coding style, testing expectations, and git hygiene. Every feature or fix should ship with regression tests and refreshed docs whenever CLI behavior or configuration metadata changes.
