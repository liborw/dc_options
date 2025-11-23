from dataclasses import dataclass
from pathlib import Path

import pytest

from dc_options import Options, option

try:
    import toml  # noqa: F401
except Exception:  # pragma: no cover
    HAS_TOML = False
else:
    HAS_TOML = True

try:
    import yaml  # noqa: F401
except Exception:  # pragma: no cover
    HAS_YAML = False
else:
    HAS_YAML = True


@dataclass
class Demo(Options):
    value: int = option(default=5)
    name: str = option(default="demo")


def test_json_roundtrip(tmp_path):
    cfg = Demo(value=9, name="abc")
    path = tmp_path / "cfg.json"
    cfg.save(path)
    loaded = Demo.load(path)
    assert loaded == cfg


@pytest.mark.skipif(not HAS_TOML, reason="toml package not available")
def test_toml_roundtrip(tmp_path):
    cfg = Demo(value=2, name="toml")
    path = tmp_path / "cfg.toml"
    cfg.save(path)
    loaded = Demo.load(path)
    assert loaded == cfg


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
def test_yaml_roundtrip(tmp_path):
    cfg = Demo(value=7, name="yaml")
    path = tmp_path / "cfg.yaml"
    cfg.save(path)
    loaded = Demo.load(path)
    assert loaded == cfg
