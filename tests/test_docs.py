from dataclasses import dataclass
from pathlib import Path

from dc_options import Options, option, export_options


@dataclass
class Train(Options):
    epochs: int = option(default=10, range=(1, None))
    lr: float = option(default=0.01)


@dataclass
class Config(Options):
    train: Train = option(default_factory=Train, label="Training")
    name: str = option(default="demo", description="Experiment identifier")


def test_export_docs_default_template(tmp_path):
    cfg = Config()
    output = tmp_path / "options.md"
    export_options(cfg, output, format="markdown")
    content = output.read_text()
    assert "Training" in content
    assert "epochs" in content
    assert "##" in content
