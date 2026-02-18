# High-Level API

The high-level API lives directly in the `hyprlang_pybind` module. It wraps the C++ library with Pythonic conventions — nested dicts, exceptions on errors, and automatic type inference.

## parse_string

Parse a raw config string. Returns a nested dict.

```python
hyprlang.parse_string(text: str, schema: dict | None = None, **options) -> dict
```

**Parameters:**

| Parameter          | Type           | Description                                                              |
| ------------------ | -------------- | ------------------------------------------------------------------------ |
| `text`             | `str`          | Raw hyprlang config text                                                 |
| `schema`           | `dict \| None` | Schema defining expected keys and defaults. Auto-inferred when `None`.   |
| `verify_only`      | `bool`         | Don't error on missing values (default `False`)                          |
| `throw_all_errors` | `bool`         | Collect all errors instead of stopping at the first (default `False`)    |

**Examples:**

```python
import hyprlang_pybind as hyprlang

data = hyprlang.parse_string("""
$BORDER = 3
border_size = $BORDER
active_color = rgba(255, 128, 0, 1.0)
enabled = true
""", schema={
    "border_size": 0,
    "active_color": 0,
    "enabled": 0,
})

data["border_size"]   # 3
data["active_color"]  # 4294934528 (ARGB int)
data["enabled"]       # 1
```

Without a schema (types are auto-inferred):

```python
data = hyprlang.parse_string("""
border_size = 3
gaps_in = 5.0
layout = dwindle
""")

data["border_size"]  # 3
data["gaps_in"]      # 5.0
data["layout"]       # "dwindle"
```

## parse_file

Parse a config file from disk. Returns a nested dict.

```python
hyprlang.parse_file(path: str, schema: dict | None = None, **options) -> dict
```

**Parameters:**

| Parameter              | Type           | Description                                                            |
| ---------------------- | -------------- | ---------------------------------------------------------------------- |
| `path`                 | `str`          | Path to the `.conf` file                                               |
| `schema`               | `dict \| None` | Schema defining expected keys and defaults. Auto-inferred when `None`. |
| `verify_only`          | `bool`         | Don't error on missing values (default `False`)                        |
| `throw_all_errors`     | `bool`         | Collect all errors (default `False`)                                   |
| `allow_missing_config` | `bool`         | Don't error if the file doesn't exist (default `False`)                |

**Examples:**

```python
data = hyprlang.parse_file("/home/user/.config/hypr/hyprland.conf", schema={
    "general": {
        "border_size": 1,
        "gaps_in": 5,
        "gaps_out": 20,
        "layout": "dwindle",
    },
    "decoration": {
        "rounding": 0,
        "blur": {
            "enabled": 1,
            "size": 3,
            "passes": 1,
        },
    },
    "input": {
        "kb_layout": "us",
        "follow_mouse": 1,
        "sensitivity": 0.0,
    },
})
```

Without a schema:

```python
data = hyprlang.parse_file("/path/to/config.conf")
```

### Schema auto-inference

When `schema` is `None`, the file or string is pre-scanned to discover keys and infer types from their values:

| Value pattern                         | Inferred type      |
| ------------------------------------- | ------------------ |
| `true`, `false`, `yes`, `no`, `on`, `off` | `int` (0)      |
| Integer literals, hex (`0xFF00FF`)    | `int` (0)          |
| `rgba(...)`, `rgb(...)`               | `int` (0)          |
| Decimal numbers (`3.14`)              | `float` (0.0)      |
| Two space-separated numbers           | `vec2` (0.0, 0.0)  |
| Everything else                       | `str` ("")         |

Variables (`$VAR`) cannot be resolved during pre-scan, so values assigned from variables will be inferred as strings. Use an explicit schema when you need precise type control over variable-assigned values.

## Config class

For more control, use the `Config` class directly. It supports subscript access, dynamic parsing, and checking whether values were explicitly set by the user.

```python
hyprlang.Config(path: str, **options)
```

**Constructor options:**

| Parameter              | Type   | Description                                            |
| ---------------------- | ------ | ------------------------------------------------------ |
| `path`                 | `str`  | File path or raw config text (if `is_stream=True`)     |
| `verify_only`          | `bool` | Don't error on missing values                          |
| `throw_all_errors`     | `bool` | Collect all errors                                     |
| `allow_missing_config` | `bool` | Don't error on missing file                            |
| `is_stream`            | `bool` | Treat `path` as raw config text instead of a file path |

**Methods:**

| Method                    | Description                                                                   |
| ------------------------- | ----------------------------------------------------------------------------- |
| `add(name, default)`      | Register a config value with its default. Must be called before `commence()`. |
| `commence()`              | Lock the schema. No new values can be added after this.                       |
| `parse()`                 | Parse the config. Raises `HyprlangError` on failure.                          |
| `parse_dynamic(line)`     | Parse a single line at runtime. Values set this way are temporary.            |
| `parse_file(path)`        | Parse an additional config file.                                              |
| `get(name, default=None)` | Get a value by name, with optional fallback.                                  |
| `is_set_by_user(name)`    | Check if the user explicitly set this value (vs. using the default).          |
| `to_dict()`               | Return all registered values as a nested dict.                                |

**Subscript access:**

```python
import hyprlang_pybind as hyprlang

config = hyprlang.Config("border_size = 5", is_stream=True)
config.add("border_size", 0)
config.commence()
config.parse()

config["border_size"]          # 5 (KeyError if not found)
config.get("border_size")      # 5
config.get("missing", 42)      # 42
"border_size" in config        # True
```

**Full example:**

```python
config = hyprlang.Config("/path/to/config.conf")

config.add("general:border_size", 1)
config.add("general:gaps_in", 5)
config.add("general:layout", "dwindle")
config.add("decoration:rounding", 0)

config.commence()
config.parse()

print(config["general:border_size"])
print(config.is_set_by_user("decoration:rounding"))

config.parse_dynamic("general:border_size = 10")
print(config["general:border_size"])  # 10

print(config.to_dict())
# {"general": {"border_size": 10, "gaps_in": 5, "layout": "dwindle"}, "decoration": {"rounding": 0}}
```

**Accessing the low-level object:**

```python
raw = config.raw  # returns the _core.Config object
raw.get_value("general:border_size")
```
