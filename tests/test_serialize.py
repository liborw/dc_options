from dataclasses import dataclass
from pathlib import Path

from dc_options import Options, option


@dataclass
class Paths(Options):
    working_dir: Path = option(
        default_factory=lambda: Path("runs"),
        serialize=lambda p: str(p),
        deserialize=Path,
    )


@dataclass
class Config(Options):
    name: str = option(default="demo")
    paths: Paths = option(default_factory=Paths)


def test_serialize_roundtrip():
    cfg = Config(name="exp", paths=Paths(working_dir=Path("/tmp/work")))
    data = cfg.to_dict()
    assert data["paths"]["working_dir"] == "/tmp/work"

    loaded = Config.from_dict(data)
    assert isinstance(loaded.paths.working_dir, Path)
    assert loaded == cfg
