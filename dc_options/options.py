import json
import argparse
from dataclasses import dataclass, fields, is_dataclass, asdict
from typing import Type, TypeVar

from dacite import from_dict, Config as DaciteConfig
from jinja2 import Template

T = TypeVar("T", bound="Options")


@dataclass
class Options:
    """
    Base class for rich dataclass-based configuration.

    Features:
        - Nested dataclasses
        - Metadata validation
        - Argparse integration
        - Human-readable dumps
        - Path-based get/set ("a.b.c")
        - Documentation generator (Jinja2)
    """

    # -------------------------------------------------------------------------
    # Load / Save
    # -------------------------------------------------------------------------
    @classmethod
    def load(cls: Type[T], filename: str) -> T:
        with open(filename, "r") as f:
            data = json.load(f)
        return from_dict(data_class=cls, data=data, config=DaciteConfig(strict=True))

    def save(self, filename: str):
        with open(filename, "w") as f:
            json.dump(asdict(self), f, indent=2)

    # -------------------------------------------------------------------------
    # Human-readable dump
    # -------------------------------------------------------------------------
    def dumps(self) -> str:
        lines = []
        self._dump_collect(self.__class__, self, lines, prefix="")
        return "\n".join(lines)

    def dump(self):
        print(self.dumps())

    @classmethod
    def _dump_collect(cls, datacls, instance, out, prefix):
        for f in fields(datacls):
            name = prefix + f.name
            value = getattr(instance, f.name)
            meta = f.metadata.get("option", {})

            if is_dataclass(value):
                cls._dump_collect(f.type, value, out, prefix=f"{name}.")
                continue

            out.append(f"{name} = {repr(value)}")

            for k, v in meta.items():
                if v is not None:
                    out.append(f"    {k}: {v}")

            out.append("")

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------
    def validate(self):
        for f in fields(self):
            value = getattr(self, f.name)
            meta = f.metadata.get("option", {})

            if is_dataclass(value):
                value.validate()
                continue

            if (m := meta.get("min")) is not None and value < m:
                raise ValueError(f"'{f.name}' must be >= {m}")

            if (m := meta.get("max")) is not None and value > m:
                raise ValueError(f"'{f.name}' must be <= {m}")

            if (choices := meta.get("choices")):
                if value not in choices:
                    raise ValueError(f"'{f.name}' must be one of {choices}")

    # -------------------------------------------------------------------------
    # Path-based get / set
    # -------------------------------------------------------------------------
    def get(self, path: str):
        obj = self
        for part in path.split("."):
            if not hasattr(obj, part):
                raise KeyError(f"Invalid path '{path}'. Missing '{part}'.")
            obj = getattr(obj, part)
        return obj

    def set(self, path: str, value):
        parts = path.split(".")
        obj = self

        for part in parts[:-1]:
            if not hasattr(obj, part):
                raise KeyError(f"Invalid path '{path}'. Missing '{part}'.")
            obj = getattr(obj, part)

        if not hasattr(obj, parts[-1]):
            raise KeyError(f"Invalid path '{path}'. Missing final '{parts[-1]}'.")

        setattr(obj, parts[-1], value)

    # -------------------------------------------------------------------------
    # Argparse integration
    # -------------------------------------------------------------------------
    @classmethod
    def build_argparser(cls, *, add_help=True):
        parser = argparse.ArgumentParser(add_help=add_help)
        cls._add_fields(parser, cls)
        return parser

    @classmethod
    def _add_fields(cls, parser, datacls, prefix=""):
        for f in fields(datacls):
            name = prefix + f.name
            meta = f.metadata.get("option", {})

            if is_dataclass(f.type):
                cls._add_fields(parser, f.type, prefix=name + ".")
                continue

            arg = "--" + name.replace("_", "-")
            kwargs = {"help": meta.get("description", "")}

            if f.type in (int, float, str):
                kwargs["type"] = f.type

            if meta.get("choices"):
                kwargs["choices"] = meta["choices"]

            parser.add_argument(arg, **kwargs)

    def apply_cli_overrides(self, args):
        for k, v in vars(args).items():
            if v is None:
                continue
            self.set(k, v)

    # -------------------------------------------------------------------------
    # Documentation
    # -------------------------------------------------------------------------
    def export_docs(self, template_file: str, output_file: str):
        with open(template_file) as f:
            tpl = Template(f.read())

        items = []
        self._collect_docs(items, self.__class__)

        with open(output_file, "w") as f:
            f.write(tpl.render(options=items))

    @classmethod
    def _collect_docs(cls, out, datacls, prefix=""):
        for f in fields(datacls):
            meta = f.metadata.get("option", {})

            if is_dataclass(f.type):
                cls._collect_docs(out, f.type, prefix + f.name + ".")
                continue

            out.append({
                "name": prefix + f.name,
                "type": f.type.__name__,
                "label": meta.get("label") or f.name,
                "description": meta.get("description") or "",
                "min": meta.get("min"),
                "max": meta.get("max"),
                "step": meta.get("step"),
                "choices": meta.get("choices"),
            })

