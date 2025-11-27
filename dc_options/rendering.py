"""Template-based rendering helpers for dc_options.Options."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from importlib import resources
from pathlib import Path
from typing import Any, List, Optional, Union, get_args, get_origin

from jinja2 import Template

from .options import Options, options
from .metadata import OptionMeta, option


# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------

@options
class RenderConfig:
    section_level: int = option(
        default=1,
        description="Level of the configuration section"
    )
    section_title: str = option(
        default="Configuration Options",
        description="Title of the configuration section",
    )

    render_defaults_commented: bool = option(
        default=True,
        description="Render values equal to default as commented-out"
    )

    render_values: bool = option(
        default=True,
        description="Whether actual values are rendered in the config"
    )


# -------------------------------------------------------------------
# Base node
# -------------------------------------------------------------------

@dataclass
class DocNode:
    """Base class for documentation nodes."""
    name: str
    label: str
    description: Optional[str]
    doc: Optional[str]
    path: str


# -------------------------------------------------------------------
# Meta information for rendering
# -------------------------------------------------------------------

@dataclass
class DocMeta(OptionMeta):
    """Extended metadata for documentation rendering."""
    type_name: str = ""
    value: Any = None

    @classmethod
    def from_option_meta(
        cls,
        om: OptionMeta,
        *,
        type_name: str,
        value: Any,
    ) -> "DocMeta":
        """Create DocMeta by copying OptionMeta fields and adding context."""
        return cls(
            label=om.label,
            description=om.description,
            editable=om.editable,
            required=om.required,
            step=om.step,
            choices=om.choices,
            choice_strict=om.choice_strict,
            labels=om.labels,
            serialize=om.serialize,
            deserialize=om.deserialize,
            bounds=om.bounds,
            default=om.default,
            default_factory=om.default_factory,
            doc=om.doc,
            type_name=type_name,
            value=value,
        )


# -------------------------------------------------------------------
# A single field (leaf)
# -------------------------------------------------------------------

@dataclass
class DocField(DocNode):
    meta: DocMeta


# -------------------------------------------------------------------
# A section containing child items
# -------------------------------------------------------------------

@dataclass
class DocSection(DocNode):
    meta: Optional[OptionMeta]
    children: List[DocNode] = field(default_factory=list)


def collect_docs(datacls: type[Options], *, instance: Any = None, prefix: str = "", name: str = "") -> DocSection:
    """
    Build a full documentation tree for an Options class.
    """
    # ----------------------------------------------------------------------
    # 1) Section-level metadata (from @options decorator)
    # ----------------------------------------------------------------------
    cls_meta: OptionMeta | None = getattr(datacls, "__options_meta__", None)

    # These become the top-level section heading, description, doc block
    section_label = cls_meta.label if cls_meta and cls_meta.label else datacls.__name__
    section_description = cls_meta.description if cls_meta else None
    section_doc = cls_meta.doc if cls_meta else None

    # Construct the root section node
    section = DocSection(
        name=name,
        label=section_label,
        description=section_description,
        path=prefix,
        meta=cls_meta,
        doc=section_doc,
        children=[],
    )

    # ----------------------------------------------------------------------
    # 2) Iterate through the dataclass fields of this Options class
    # ----------------------------------------------------------------------
    for f in fields(datacls):

        # Field metadata
        meta: OptionMeta | None = f.metadata.get("option")
        label = meta.label if meta and meta.label else f.name
        description = meta.description if meta else None
        doc = meta.doc if meta else None

        full_path = prefix + "." + f.name if len(prefix) > 0 else f.name
        value = getattr(instance, f.name) if instance is not None else None

        # ------------------------------------------------------------------
        # 3) Nested section?  (i.e. field whose type is another Options class)
        # ------------------------------------------------------------------
        if isinstance(meta, OptionMeta) and _is_options_type(f.type):
            # Build subtree recursively
            subsection = collect_docs(
                f.type,
                instance=value,
                prefix=full_path,
                name=f.name
            )

            # Override section label/description/doc from field metadata if present
            if meta.label:
                subsection.label = meta.label
            if meta.description:
                subsection.description = meta.description
            if meta.doc:
                subsection.doc = meta.doc

            section.children.append(subsection)
            continue

        # ------------------------------------------------------------------
        # 4) Regular field
        # ------------------------------------------------------------------

        docmeta = DocMeta.from_option_meta(
            meta or OptionMeta(),
            type_name=_safe_type_name(f.type),
            value=value,
        )

        field_node = DocField(
            name=f.name,
            label=label,
            description=description,
            doc=doc,
            path=full_path,
            meta=docmeta,
        )

        section.children.append(field_node)

    # sort children so that sections are at the end
    section.children.sort(key= lambda n: isinstance(n, DocSection))

    return section


def _resolve_template(template_path: str | Path) -> str:
    """
    Resolve template from user-provided path or bundled templates.

    Rules:
        1. If `template_path` is an existing filesystem path → load it.
        2. Otherwise, treat the string as a template name located in:
              dc_options/templates/<template_path>
        3. If not found, raise a clear error.
    """

    p = Path(template_path)

    # --------------------------------------------------------
    # Case 1 — User provided a real existing file
    # --------------------------------------------------------
    if p.exists():
        return p.read_text()

    # --------------------------------------------------------
    # Case 2 — Try internal bundled templates
    # --------------------------------------------------------
    try:
        return resources.files("dc_options").joinpath(f"templates/{p.name}").read_text()
    except (FileNotFoundError, OSError):
        pass

    # --------------------------------------------------------
    # Case 3 — Not found anywhere
    # --------------------------------------------------------
    raise FileNotFoundError(
        f"Template '{template_path}' not found as a filesystem path "
        f"and not located in dc_options/templates/"
    )


def render(data: Options, template: str | Path = "plain.txt.j2", config: RenderConfig | None = None) -> str:
    tpl_source = _resolve_template(template)
    tpl = Template(tpl_source)
    structure = collect_docs(data.__class__, instance=data)
    config = config or RenderConfig()
    print(config)
    return tpl.render(options=structure, config=config)


def _is_options_type(tp):
    try:
        return issubclass(tp, Options)
    except TypeError:
        return False


def _safe_type_name(tp):
    """
    Resolve a human-friendly type name for annotations used in dataclasses.
    Handles:
        - regular classes
        - forward references (strings)
        - Optional[T] / Union[T, None]
        - parameterized generics
        - Any / special typing forms
    """
    # Forward reference: "MyType"
    if isinstance(tp, str):
        return tp

    # Normal class
    if isinstance(tp, type):
        return tp.__name__

    # Optional[T] or Union[T, None]
    origin = get_origin(tp)
    if origin is Union:
        args = get_args(tp)
        # filter None out
        names = [_safe_type_name(a) for a in args if a is not type(None)]
        return " | ".join(names)

    # parameterized generic like list[int], dict[str, X]
    if origin:
        origin_name = _safe_type_name(origin)
        args_names = ", ".join(_safe_type_name(a) for a in get_args(tp))
        return f"{origin_name}[{args_names}]"

    # Fallback (typing.Any, etc.)
    return str(tp)


def replace_text(
    instr: str,
    newstr: str,
    sec_start: str,
    sec_end: Optional[str] = None,
) -> str:
    """
    Replace the *first* occurrence of text inside sec_start ... sec_end
    while preserving both markers.

    If sec_end is None, use sec_start as a symmetric marker.
    """
    sec_end = sec_end or sec_start

    # Find the first start marker
    start_idx = instr.find(sec_start)
    if start_idx == -1:
        return instr

    content_start = start_idx + len(sec_start)

    # Find the corresponding end marker
    end_idx = instr.find(sec_end, content_start)
    if end_idx == -1:
        return instr

    # Build new string: before marker + marker + new content + marker + after
    return (
        instr[:content_start] +
        newstr +
        sec_end +
        instr[end_idx + len(sec_end):]
    )
