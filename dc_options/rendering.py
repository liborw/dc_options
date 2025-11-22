"""Template-based rendering helpers for dc_options.Options."""

from __future__ import annotations

from dataclasses import fields
from importlib import resources
from pathlib import Path
from typing import Any

from jinja2 import Template

from .options import Options


def render_options(options: Options, template: str | Path | None = None, *, format: str = "plain") -> str:
    tpl_source = _resolve_template(template, format)
    tpl = Template(tpl_source)
    structure = _collect_docs(options.__class__, include_values=True, instance=options)
    return tpl.render(options=structure)


def export_options(options: Options, output: str | Path, template: str | Path | None = None, *, format: str = "plain") -> None:
    Path(output).write_text(render_options(options, template=template, format=format))


def _resolve_template(template: str | Path | None, format: str) -> str:
    if template:
        return Path(template).read_text()

    templates = {
        "plain": "templates/plain.txt.j2",
        "markdown": "templates/docs.md.j2",
    }
    rel_path = templates.get(format, templates["plain"])
    return resources.files("dc_options").joinpath(rel_path).read_text()


def _collect_docs(datacls, *, include_values: bool, instance: Any | None, prefix: str = ""):
    entries = []
    for f in fields(datacls):
        meta = f.metadata.get("option", {})
        label = meta.get("label") or f.name
        description = meta.get("description")
        value = getattr(instance, f.name) if instance is not None else None

        if _is_options_type(f.type):
            entries.append({
                "kind": "section",
                "name": f.name,
                "label": label,
                "description": description,
                "path": prefix + f.name,
                "children": _collect_docs(f.type, include_values=include_values, instance=value, prefix=prefix + f.name + "."),
            })
            continue

        entries.append({
            "kind": "field",
            "name": f.name,
            "label": label,
            "description": description,
            "path": prefix + f.name,
            "value": value,
            "meta": {
                "type": _type_name(f.type),
                "min": meta.get("min"),
                "max": meta.get("max"),
                "step": meta.get("step"),
                "choices": meta.get("choices") or [],
                "labels": meta.get("labels") or [],
                "default": meta.get("default"),
            },
        })
    return entries


def _is_options_type(tp):
    try:
        return issubclass(tp, Options)
    except TypeError:
        return False


def _type_name(tp):
    return getattr(tp, "__name__", str(tp))
