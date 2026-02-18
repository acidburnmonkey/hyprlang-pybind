"""
Python bindings for hyprlang configuration parser.

Provides both a low-level API (mirroring the C++ interface) and a high-level
Pythonic API for parsing hyprlang config files.

Low-level (mirrors C++):
    from hyprlang_pybind import Config, ConfigOptions

    config = Config("/path/to/config.conf")
    config.add_value("myCategory:myValue", 0)
    config.commence()
    result = config.parse()
    val = config.get_value("myCategory:myValue")

High-level (Pythonic):
    import hyprlang_pybind as hyprlang

    data = hyprlang.parse_file("config.conf", schema={
        "general": {
            "border_size": 1,
            "gaps_in": 5.0,
        },
    })
    print(data["general"]["border_size"])
"""

from __future__ import annotations

from hyprlang_pybind._core import (
    Config as _Config,
    ConfigOptions,
    ConfigValueProxy,
    HandlerOptions,
    ParseResult,
    SpecialCategoryOptions,
    SVector2D,
)

__all__ = [
    "ConfigOptions",
    "ConfigValueProxy",
    "HandlerOptions",
    "ParseResult",
    "SpecialCategoryOptions",
    "SVector2D",
    "Config",
    "parse_file",
    "parse_string",
    "HyprlangError",
]

type ConfigValue = int | float | str | tuple[float, float]

_BOOL_WORDS = frozenset({"true", "false", "yes", "no", "on", "off"})
_RE_INT = __import__("re").compile(r"^-?\d+$")
_RE_HEX = __import__("re").compile(r"^0x[0-9a-fA-F]+$")
_RE_FLOAT = __import__("re").compile(r"^-?\d*\.\d+$|^-?\d+\.\d*$")
_RE_VEC2 = __import__("re").compile(r"^-?\d+\.?\d*\s+-?\d+\.?\d*$")
_RE_COLOR = __import__("re").compile(r"^rgba?\(")


def _infer_type(value: str) -> ConfigValue:
    """Infer a hyprlang default from a raw value string."""
    v = value.strip()
    if v.lower() in _BOOL_WORDS:
        return 0
    if _RE_HEX.match(v) or _RE_INT.match(v):
        return 0
    if _RE_COLOR.match(v):
        return 0
    if _RE_FLOAT.match(v):
        return 0.0
    if _RE_VEC2.match(v):
        return (0.0, 0.0)
    return ""


def _infer_schema(text: str) -> dict[str, ConfigValue]:
    """Pre-scan hyprlang text and build a flat schema by inferring types."""
    schema: dict[str, ConfigValue] = {}
    category_stack: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.split("#")[0].strip()
        if not line:
            continue

        if line.startswith("$") or line.startswith("source"):
            continue

        if line.endswith("{"):
            cat = line[:-1].strip().split("[")[0].strip()
            if cat:
                category_stack.append(cat)
            continue

        if line == "}":
            if category_stack:
                category_stack.pop()
            continue

        if "=" in line:
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            if not key or not val:
                continue
            full_key = ":".join([*category_stack, key])
            schema[full_key] = _infer_type(val)

    return schema


class HyprlangError(Exception):
    """Raised when hyprlang parsing fails."""


def _flatten_schema(
    schema: dict, prefix: str = ""
) -> list[tuple[str, ConfigValue]]:
    """Flatten a nested schema dict into colon-separated key/default pairs."""
    result: list[tuple[str, ConfigValue]] = []
    for key, value in schema.items():
        full_key = f"{prefix}{key}" if not prefix else f"{prefix}:{key}"
        if isinstance(value, dict):
            result.extend(_flatten_schema(value, full_key))
        else:
            result.append((full_key, value))
    return result


def _unflatten(flat: dict[str, object]) -> dict[str, object]:
    """Convert colon-separated flat keys back into a nested dict."""
    result: dict[str, object] = {}
    for key, value in flat.items():
        parts = key.split(":")
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]  # type: ignore[assignment]
        current[parts[-1]] = value
    return result


class Config:
    """High-level Pythonic wrapper around hyprlang's CConfig."""

    def __init__(
        self,
        path: str,
        *,
        verify_only: bool = False,
        throw_all_errors: bool = False,
        allow_missing_config: bool = False,
        is_stream: bool = False,
    ) -> None:
        opts = ConfigOptions()
        opts.verify_only = int(verify_only)
        opts.throw_all_errors = int(throw_all_errors)
        opts.allow_missing_config = int(allow_missing_config)
        opts.path_is_stream = int(is_stream)
        self._config = _Config(path, opts)
        self._keys: list[str] = []
        self._commenced = False

    def add(
        self,
        name: str,
        default: ConfigValue | SVector2D,
    ) -> None:
        """Register a config value with its default. Must be called before commence()."""
        if self._commenced:
            raise HyprlangError("Cannot add values after commence()")
        self._config.add_value(name, default)
        self._keys.append(name)

    def add_special_category(
        self,
        name: str,
        *,
        key: str | None = None,
        ignore_missing: bool = False,
        anonymous: bool = False,
    ) -> None:
        """Register a special (keyed/anonymous) category."""
        opts = SpecialCategoryOptions()
        if key is not None:
            opts.set_key(key)
        opts.ignore_missing = int(ignore_missing)
        opts.anonymous_key_based = int(anonymous)
        self._config.add_special_category(name, opts)

    def add_special_value(
        self,
        category: str,
        name: str,
        default: ConfigValue | SVector2D,
    ) -> None:
        """Register a config value within a special category."""
        self._config.add_special_value(category, name, default)

    def commence(self) -> None:
        """Lock the schema. No new values can be added after this."""
        self._config.commence()
        self._commenced = True

    def parse(self) -> None:
        """Parse the config file. Raises HyprlangError on failure."""
        result = self._config.parse()
        if result.error:
            raise HyprlangError(result.error_message)

    def parse_dynamic(self, line: str) -> None:
        """Parse a single dynamic line. Raises HyprlangError on failure."""
        result = self._config.parse_dynamic(line)
        if result.error:
            raise HyprlangError(result.error_message)

    def parse_file(self, path: str) -> None:
        """Parse an additional config file. Raises HyprlangError on failure."""
        result = self._config.parse_file(path)
        if result.error:
            raise HyprlangError(result.error_message)

    def get(self, name: str, default: object = None) -> ConfigValue | None:
        """Get a config value by name, returning default if not found."""
        val = self._config.get_value(name)
        if val is None:
            return default
        return val

    def get_special(
        self, category: str, name: str, key: str | None = None
    ) -> ConfigValue | None:
        """Get a special category config value."""
        return self._config.get_special_value(category, name, key)

    def is_set_by_user(self, name: str) -> bool:
        """Check if a config value was explicitly set by the user."""
        info = self._config.get_value_info(name)
        return info.set_by_user

    def special_category_exists(self, category: str, key: str) -> bool:
        """Check if a special category with the given key exists."""
        return self._config.special_category_exists(category, key)

    def list_special_keys(self, category: str) -> list[str]:
        """List all keys for a special category."""
        return self._config.list_keys_for_special_category(category)

    def to_dict(self) -> dict[str, object]:
        """Return all registered config values as a nested dict."""
        flat = {}
        for key in self._keys:
            flat[key] = self._config.get_value(key)
        return _unflatten(flat)

    def __getitem__(self, name: str) -> ConfigValue:
        val = self._config.get_value(name)
        if val is None:
            raise KeyError(name)
        return val

    def __contains__(self, name: str) -> bool:
        return self._config.get_value(name) is not None

    @property
    def raw(self) -> _Config:
        """Access the underlying low-level Config object."""
        return self._config


def parse_file(
    path: str,
    schema: dict | None = None,
    *,
    verify_only: bool = False,
    throw_all_errors: bool = False,
    allow_missing_config: bool = False,
) -> dict[str, object]:
    """Parse a hyprlang config file and return values as a nested dict.

    If schema is None, the file is pre-scanned to infer keys and types.
    """
    if schema is None:
        with open(path) as f:
            flat_pairs = list(_infer_schema(f.read()).items())
    else:
        flat_pairs = _flatten_schema(schema)

    config = Config(
        path,
        verify_only=verify_only,
        throw_all_errors=throw_all_errors,
        allow_missing_config=allow_missing_config,
    )
    for key, default in flat_pairs:
        config.add(key, default)
    config.commence()
    config.parse()
    return config.to_dict()


def parse_string(
    text: str,
    schema: dict | None = None,
    *,
    verify_only: bool = False,
    throw_all_errors: bool = False,
) -> dict[str, object]:
    """Parse a hyprlang config string and return values as a nested dict.

    If schema is None, the text is pre-scanned to infer keys and types.
    """
    if schema is None:
        flat_pairs = list(_infer_schema(text).items())
    else:
        flat_pairs = _flatten_schema(schema)

    config = Config(
        text,
        verify_only=verify_only,
        throw_all_errors=throw_all_errors,
        is_stream=True,
    )
    for key, default in flat_pairs:
        config.add(key, default)
    config.commence()
    config.parse()
    return config.to_dict()
