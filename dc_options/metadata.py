from dataclasses import MISSING, dataclass, field
from typing import Any, Optional, List, Callable, Tuple


@dataclass
class OptionMeta:
    label: Optional[str] = None
    description: Optional[str] = None
    editable: bool = True
    required: bool = False
    step: Optional[float] = None
    choices: Optional[List[Any]] = None
    choice_strict: bool = True
    labels: Optional[List[str]] = None
    serialize: Optional[Callable[[Any], Any]] = None
    deserialize: Optional[Callable[[Any], Any]] = None
    bounds: Optional[Tuple[Optional[float], Optional[float]]] = None
    default: Any = None
    default_factory: Any = None
    doc: Optional[str] = None

    def cleaned(self) -> dict:
        """Convert to plain dict but without None values, matching current semantics."""
        d = {
            "label": self.label,
            "description": self.description,
            "editable": self.editable,
            "required": self.required,
            "step": self.step,
            "choices": self.choices,
            "choice_strict": self.choice_strict,
            "labels": self.labels,
            "serialize": self.serialize,
            "deserialize": self.deserialize,
            "bunds": self.bounds,
            "doc": self.doc,
            "default": self.default,
            "default_factory": self.default_factory,
        }
        return {k: v for k, v in d.items() if v is not None}


def option(
    default: Any = MISSING,
    *,
    default_factory = MISSING,
    label: Optional[str] = None,
    description: Optional[str] = None,
    editable: bool = True,
    required: bool = False,
    step: Optional[float] = None,
    choices: Optional[List[Any]] = None,
    choice_strict: bool = True,
    labels: Optional[List[str]] = None,
    serialize: Optional[Callable[[Any], Any]] = None,
    deserialize: Optional[Callable[[Any], Any]] = None,
    bounds: Optional[Tuple[Optional[float], Optional[float]]] = None,
    doc: Optional[str] = None,
    **field_kwargs,
):
    """
    Wraps a dataclass field with metadata describing UI, validation and documentation.
    """
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError("option() cannot accept both default and default_factory.")

    if "default" in field_kwargs or "default_factory" in field_kwargs:
        raise ValueError("Use option() parameters for default/default_factory.")

    meta = OptionMeta(
        label=label,
        description=description,
        editable=editable,
        required=required,
        step=step,
        choices=choices,
        choice_strict=choice_strict,
        labels=labels,
        serialize=serialize,
        deserialize=deserialize,
        bounds=bounds,
        default=default if default is not MISSING else None,
        default_factory=default_factory if default_factory is not MISSING else None,
        doc=doc,
    )

    metadata = dict(field_kwargs.pop("metadata", {}) or {})
    metadata["option"] = meta

    params = {"metadata": metadata, **field_kwargs}
    if default is not MISSING:
        params["default"] = default
    if default_factory is not MISSING:
        params["default_factory"] = default_factory

    return field(**params)
