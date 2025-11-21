from dataclasses import field
from typing import Any, Optional, List


def option(
    default: Any = None,
    *,
    label: Optional[str] = None,
    description: Optional[str] = None,
    editable: bool = True,
    min: Optional[float] = None,
    max: Optional[float] = None,
    step: Optional[float] = None,
    choices: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
):
    """
    Wraps a dataclass field with metadata describing UI, validation and documentation.
    """
    meta = {
        "label": label,
        "description": description,
        "editable": editable,
        "min": min,
        "max": max,
        "step": step,
        "choices": choices,
        "labels": labels,
    }
    return field(default=default, metadata={"option": meta})
