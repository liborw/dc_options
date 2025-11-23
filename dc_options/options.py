import argparse
import importlib
from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any, Dict, Type, TypeVar


T = TypeVar("T", bound="Options")


@dataclass
class ValidationIssue:
    path: str
    message: str


class ValidationError(Exception):
    def __init__(self, issues: list[ValidationIssue]):
        self.issues = issues
        summary = "\n".join(f"- {issue.path}: {issue.message}" for issue in issues)
        super().__init__(f"{len(issues)} validation error(s) found:\n{summary}")


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
            toml = _require_module("toml", "toml")
            data = toml.loads(path.read_text())

        elif ext in {".yaml", ".yml"}:
            yaml = _require_module("yaml", "yaml")
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
            toml = _require_module("toml", "toml")
            with open(path, "w") as f:
                toml.dump(self.to_dict(), f)

        elif ext in {".yaml", ".yml"}:
            yaml = _require_module("yaml", "yaml")
            with open(path, "w") as f:
                yaml.safe_dump(self.to_dict(), f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for f in fields(self):
            result[f.name] = self._serialize_field(f, getattr(self, f.name))
        return result

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------
    def validate(self):
        issues = self.collect_validation_errors()
        if issues:
            raise ValidationError(issues)

    def collect_validation_errors(self) -> list[ValidationIssue]:
        return self._collect_validation_errors(self.__class__, self)

    @classmethod
    def _collect_validation_errors(cls, datacls, instance, prefix: str = "") -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for f in fields(datacls):
            path = prefix + f.name
            value = getattr(instance, f.name)
            meta = f.metadata.get("option", {})

            if value is None:
                if meta.get("required"):
                    issues.append(ValidationIssue(path, "is required"))
                continue

            if cls._is_options_type(f.type):
                issues.extend(cls._collect_validation_errors(f.type, value, prefix=path + "."))
                continue

            rng = meta.get("range")
            if rng is not None:
                lower, upper = rng
                if lower is not None and value < lower:
                    issues.append(ValidationIssue(path, f"must be >= {lower}"))
                if upper is not None and value > upper:
                    issues.append(ValidationIssue(path, f"must be <= {upper}"))
            else:
                if (m := meta.get("min")) is not None and value < m:
                    issues.append(ValidationIssue(path, f"must be >= {m}"))
                if (m := meta.get("max")) is not None and value > m:
                    issues.append(ValidationIssue(path, f"must be <= {m}"))

            if meta.get("choice_strict", True):
                if (choices := meta.get("choices")) and value not in choices:
                    issues.append(ValidationIssue(path, f"must be one of {choices}"))

        return issues

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


def _require_module(module: str, extra: str):
    try:
        return importlib.import_module(module)
    except ImportError as exc:
        raise RuntimeError(
            f"Module '{module}' is required for this operation. Install the optional dependency via "
            f"`pip install dc-options[{extra}]`."
        ) from exc
