from dataclasses import dataclass
from dc_options import Options, option, ValidationError
import pytest


@dataclass
class C(Options):
    v: int = option(default=5, range=(3, 10))


def test_validation_ok():
    C(v=7).validate()


def test_validation_fail():
    with pytest.raises(ValidationError) as exc:
        C(v=100).validate()
    assert exc.value.issues[0].path == "v"
    assert "<=" in exc.value.issues[0].message


@dataclass
class Multi(Options):
    a: int = option(range=(1, 5))
    b: int = option(range=(10, None))


def test_validation_collects_multiple_errors():
    cfg = Multi(a=0, b=5)
    with pytest.raises(ValidationError) as exc:
        cfg.validate()
    assert len(exc.value.issues) == 2
