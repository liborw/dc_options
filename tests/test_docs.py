from dataclasses import dataclass
from pathlib import Path

from dc_options import Options, option


@dataclass
class Train(Options):
    epochs: int = option(default=10, min=1)
    lr: float = option(default=0.01)


@dataclass
class Config(Options):
    train: Train = option(default_factory=Train, label="Training")
    name: str = option(default="demo", description="Experiment identifier")


def test_export_docs_default_template(tmp_path):
    cfg = Config()
    output = tmp_path / "options.md"
    cfg.export_docs(output)
    content = output.read_text()
    assert "Training" in content
    assert "epochs" in content
    assert "##" in content
