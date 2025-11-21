from dataclasses import dataclass
from options import Options, option


@dataclass
class Inner(Options):
    x: int = option(default=1, min=0)


@dataclass
class Config(Options):
    a: int = option(default=5, min=1)
    inner: Inner = Inner()


def test_basic_values():
    cfg = Config()
    assert cfg.a == 5
    assert cfg.inner.x == 1
    cfg.validate()

