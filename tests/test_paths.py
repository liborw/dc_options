from dataclasses import dataclass
from options import Options, option


@dataclass
class A(Options):
    b: int = option(default=10)


@dataclass
class Root(Options):
    a: A = A()


def test_path_get_set():
    r = Root()
    assert r.get("a.b") == 10
    r.set("a.b", 20)
    assert r.get("a.b") == 20

