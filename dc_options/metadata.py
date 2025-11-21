from dataclasses import MISSING, field
from typing import Any, Optional, List, Callable


def option(
    default: Any = MISSING,
    *,
    default_factory = MISSING,
    label: Optional[str] = None,
    description: Optional[str] = None,
    editable: bool = True,
    min: Optional[float] = None,
    max: Optional[float] = None,
    step: Optional[float] = None,
    choices: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
    serialize: Optional[Callable[[Any], Any]] = None,
    deserialize: Optional[Callable[[Any], Any]] = None,
    **field_kwargs,
):
    """
    Wraps a dataclass field with metadata describing UI, validation and documentation.
    """
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError("option() cannot accept both default and default_factory.")

    if "default" in field_kwargs or "default_factory" in field_kwargs:
        raise ValueError("Use option() parameters for default/default_factory.")

    meta = {
        "label": label,
        "description": description,
        "editable": editable,
        "min": min,
        "max": max,
        "step": step,
        "choices": choices,
        "labels": labels,
        "serialize": serialize,
        "deserialize": deserialize,
    }
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
