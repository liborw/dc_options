import warnings
from dataclasses import MISSING, field
from typing import Any, Optional, List, Callable, Tuple


def option(
    default: Any = MISSING,
    *,
    default_factory = MISSING,
    label: Optional[str] = None,
    description: Optional[str] = None,
    editable: bool = True,
    required: bool = False,
    min: Optional[float] = None,
    max: Optional[float] = None,
    step: Optional[float] = None,
    choices: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
    serialize: Optional[Callable[[Any], Any]] = None,
    deserialize: Optional[Callable[[Any], Any]] = None,
    range: Optional[Tuple[Optional[float], Optional[float]]] = None,
    **field_kwargs,
):
    """
    Wraps a dataclass field with metadata describing UI, validation and documentation.
    """
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError("option() cannot accept both default and default_factory.")

    if "default" in field_kwargs or "default_factory" in field_kwargs:
        raise ValueError("Use option() parameters for default/default_factory.")

    range_min = None
    range_max = None
    if range is not None:
        if len(range) != 2:
            raise ValueError("range must be a 2-tuple (min, max).")
        range_min, range_max = range

    if min is not None or max is not None:
        warnings.warn(
            "option(): 'min'/'max' parameters are deprecated; use 'range' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if min is not None:
            range_min = min if range_min is None else min
        if max is not None:
            range_max = max if range_max is None else max

    meta = {
        "label": label,
        "description": description,
        "editable": editable,
        "required": required,
        "min": range_min,
        "max": range_max,
        "step": step,
        "choices": choices,
        "labels": labels,
        "serialize": serialize,
        "deserialize": deserialize,
    }
    if range_min is not None or range_max is not None:
        meta["range"] = (range_min, range_max)

    meta = {k: v for k, v in meta.items() if v is not None}
    if default is not MISSING:
        meta["default"] = default
    if default_factory is not MISSING:
        meta["default_factory"] = default_factory
    metadata = dict(field_kwargs.pop("metadata", {}) or {})
    metadata["option"] = meta

    params = {"metadata": metadata, **field_kwargs}
    if default is not MISSING:
        params["default"] = default
    if default_factory is not MISSING:
        params["default_factory"] = default_factory

    return field(**params)
