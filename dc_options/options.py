import argparse
from dataclasses import dataclass, fields, is_dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Type, TypeVar

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
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        kwargs = {}
        for f in fields(cls):
            if f.name not in data:
                continue
            kwargs[f.name] = cls._deserialize_field(f, data[f.name])
        return cls(**kwargs)

    @classmethod
    def load(cls: Type[T], path: str | Path ) -> T:
        path = Path(path)
        ext = path.suffix.lower()

        if ext in {".json"}:
            import json
            data = json.loads(path.read_text())

        elif ext in {".toml"}:
            import tomllib
            data = tomllib.loads(path.read_text())

        elif ext in {".yaml", ".yml"}:
            import yaml
            data = yaml.safe_load(path.read_text())

        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        return cls.from_dict(data=data)


    def save(self, path: str | Path):

        path = Path(path)
        ext = path.suffix.lower()

        if ext in {".json"}:
            import json
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)

        elif ext in {".toml"}:
            import toml
            with open(path, "w") as f:
                toml.dump(self.to_dict(), f)

        elif ext in {".yaml", ".yml"}:
            import yaml
            with open(path, "w") as f:
                yaml.dump(self.to_dict(), f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for f in fields(self):
            result[f.name] = self._serialize_field(f, getattr(self, f.name))
        return result

    # -------------------------------------------------------------------------
    # Human-readable dump
    # -------------------------------------------------------------------------
    def dumps(self) -> str:
        return self.render_template()

    def dump(self):
        print(self.dumps())

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------
    def validate(self):
        for f in fields(self):
            value = getattr(self, f.name)
            meta = f.metadata.get("option", {})

            if is_dataclass(value) and isinstance(value, Options):
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
    def render_template(self, template: str | Path | None = None, *, format: str = "plain") -> str:
        tpl_source = self._resolve_template(template, format)
        tpl = Template(tpl_source)
        structure = self._collect_docs(self.__class__, include_values=True, instance=self)
        return tpl.render(options=structure)

    def export(self, output_file: str | Path, template: str | Path | None = None, *, format: str = "plain"):
        Path(output_file).write_text(self.render_template(template, format=format))

    def export_docs(self, output_file: str | Path, template: str | Path | None = None):
        self.export(output_file, template=template, format="markdown")

    def _resolve_template(self, template: str | Path | None, format: str) -> str:
        if template:
            return Path(template).read_text()

        templates = {
            "plain": "templates/plain.txt.j2",
            "markdown": "templates/docs.md.j2",
        }
        rel_path = templates.get(format, templates["plain"])
        return resources.files("dc_options").joinpath(rel_path).read_text()

    @classmethod
    def _collect_docs(cls, datacls, *, include_values=False, instance=None, prefix=""):
        entries = []
        for f in fields(datacls):
            meta = f.metadata.get("option", {})
            label = meta.get("label") or f.name
            description = meta.get("description")
            value = getattr(instance, f.name) if instance is not None else None

            if cls._is_options_type(f.type):
                entries.append({
                    "kind": "section",
                    "name": f.name,
                    "label": label,
                    "description": description,
                    "path": prefix + f.name,
                    "children": cls._collect_docs(f.type, include_values=include_values, instance=value, prefix=prefix + f.name + "."),
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
                    "type": cls._type_name(f.type),
                    "min": meta.get("min"),
                    "max": meta.get("max"),
                    "step": meta.get("step"),
                    "choices": meta.get("choices") or [],
                    "labels": meta.get("labels") or [],
                    "default": meta.get("default"),
                },
            })
        return entries

    # -------------------------------------------------------------------------
    # Serialization helpers
    # -------------------------------------------------------------------------
    @classmethod
    def _serialize_field(cls, f, value):
        if value is None:
            return None

        meta = f.metadata.get("option", {})
        serializer = meta.get("serialize")
        if serializer:
            return serializer(value)

        if isinstance(value, Options):
            return value.to_dict()

        return value

    @classmethod
    def _deserialize_field(cls, f, raw):
        if raw is None:
            return None

        if cls._is_options_type(f.type):
            return f.type.from_dict(raw)

        meta = f.metadata.get("option", {})
        deserializer = meta.get("deserialize")
        if deserializer:
            return deserializer(raw)

        return raw

    @staticmethod
    def _is_options_type(tp):
        try:
            return issubclass(tp, Options)
        except TypeError:
            return False

    @staticmethod
    def _type_name(tp):
        return getattr(tp, "__name__", str(tp))
