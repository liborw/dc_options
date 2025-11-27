from dataclasses import dataclass
from dc_options import Options, option


@dataclass
class Inner(Options):
    x: int = option(default=1, bounds=(0, None))


@dataclass
class Config(Options):
    a: int = option(default=5, bounds=(1, None))
    inner: Inner = option(default_factory=Inner)


def test_basic_values():
    cfg = Config()
    assert cfg.a == 5
    assert cfg.inner.x == 1
    cfg.validate()
