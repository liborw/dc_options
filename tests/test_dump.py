from dataclasses import dataclass
from options import Options, option


@dataclass
class T(Options):
    a: int = option(default=1, label="Alpha", description="First")


def test_dump_contains_metadata():
    t = T()
    s = t.dumps()
    assert "Alpha" in s
    assert "a =" in s
