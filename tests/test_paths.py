from dataclasses import dataclass
from dc_options import Options, option


@dataclass
class A(Options):
    b: int = option(default=10)


@dataclass
class Root(Options):
    a: A = option(default_factory=A)


def test_path_get_set():
    r = Root()
    assert r.get("a.b") == 10
    r.set("a.b", 20)
    assert r.get("a.b") == 20
