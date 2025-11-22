from dataclasses import dataclass
from dc_options import Options, option, render_options


@dataclass
class T(Options):
    a: int = option(default=1, label="Alpha", description="First")


def test_dump_contains_metadata():
    t = T()
    s = render_options(t)
    assert "Alpha" in s
    assert "a (Alpha) =" in s
