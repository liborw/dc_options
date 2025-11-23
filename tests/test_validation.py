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
    mode: str = option(choices=["fast", "safe"], default="fast")
    label: str = option(choices=["red"], choice_strict=False, default="blue")
    title: str = option(required=True, default="demo")


def test_validation_collects_multiple_errors():
    cfg = Multi(a=0, b=5, mode="unknown", title=None)
    with pytest.raises(ValidationError) as exc:
        cfg.validate()
    assert len(exc.value.issues) == 4
    paths = {issue.path for issue in exc.value.issues}
    assert paths == {"a", "b", "mode", "title"}


def test_choice_non_strict_allows_extra_values():
    cfg = Multi(a=3, b=20, mode="fast", label="custom", title="demo")
    cfg.validate()
