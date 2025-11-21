from dataclasses import dataclass
from options import Options, option
import pytest


@dataclass
class C(Options):
    v: int = option(default=5, min=3, max=10)


def test_validation_ok():
    C(v=7).validate()


def test_validation_fail():
    with pytest.raises(ValueError):
        C(v=100).validate()

