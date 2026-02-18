# Low-Level API

The low-level API is in `hyprlang_pybind._core` and mirrors the C++ `Hyprlang::CConfig` interface directly. All types are also re-exported from `hyprlang_pybind` for convenience.

## Config

Wraps `Hyprlang::CConfig`.

```python
from hyprlang_pybind._core import Config, ConfigOptions

opts = ConfigOptions()
opts.path_is_stream = 1

config = Config("myval = 42", opts)
config.add_value("myval", 0)
config.commence()
result = config.parse()

if not result.error:
    print(config.get_value("myval"))  # 42
```

**Methods:**

| Method                           | Signature                                   | Description                                                      |
| -------------------------------- | ------------------------------------------- | ---------------------------------------------------------------- |
| `add_value`                      | `(name: str, default)`                      | Register a config value (int, float, str, SVector2D, or 2-tuple) |
| `commence`                       | `()`                                        | Lock schema                                                      |
| `parse`                          | `() -> ParseResult`                         | Parse config                                                     |
| `parse_file`                     | `(path: str) -> ParseResult`                | Parse additional file                                            |
| `parse_dynamic`                  | `(line: str) -> ParseResult`                | Parse a single line dynamically                                  |
| `parse_dynamic_kv`               | `(command: str, value: str) -> ParseResult` | Parse a command/value pair                                       |
| `get_value`                      | `(name: str) -> int\|float\|str\|tuple`     | Get a parsed value                                               |
| `get_value_info`                 | `(name: str) -> ConfigValueProxy`           | Get value + `set_by_user` flag                                   |
| `add_special_category`           | `(name, options)`                           | Register a special category                                      |
| `add_special_value`              | `(cat, name, default)`                      | Add a value to a special category                                |
| `get_special_value`              | `(cat, name, key=None)`                     | Get a special category value                                     |
| `list_keys_for_special_category` | `(cat) -> list[str]`                        | List all keys in a special category                              |
| `special_category_exists`        | `(cat, key) -> bool`                        | Check if a keyed category exists                                 |
| `change_root_path`               | `(path: str)`                               | Change root for relative `source` directives                     |

## ParseResult

Returned by `parse()`, `parse_dynamic()`, and `parse_file()`.

```python
result = config.parse()

result.error          # bool — True if parsing failed
result.error_message  # str | None — error details
bool(result)          # True if OK (no error)
```

## ConfigOptions

Options for the parser.

```python
opts = ConfigOptions()
opts.verify_only = 1
opts.throw_all_errors = 1
opts.allow_missing_config = 1
opts.path_is_stream = 1
```

## SVector2D

2D vector type. Used for config values like monitor positions or sizes.

```python
from hyprlang_pybind import SVector2D

v = SVector2D(1920.0, 1080.0)
v.x  # 1920.0
v.y  # 1080.0

config.add_value("monitor_pos", SVector2D(0.0, 0.0))
config.add_value("monitor_pos", (0.0, 0.0))  # equivalent

val = config.get_value("monitor_pos")  # (1920.0, 1080.0)
```

## Special Categories

Special categories are hyprlang's mechanism for repeated/keyed config blocks (like monitor or window rules).

```python
from hyprlang_pybind._core import Config, ConfigOptions, SpecialCategoryOptions

opts = ConfigOptions()
opts.path_is_stream = 1

config = Config("""
device[my-mouse] {
    sensitivity = 0.5
}

device[my-keyboard] {
    kb_layout = us
}
""", opts)

config.add_value("placeholder", 0)

cat_opts = SpecialCategoryOptions()
cat_opts.set_key("key")
config.add_special_category("device", cat_opts)
config.add_special_value("device", "sensitivity", 0.0)
config.add_special_value("device", "kb_layout", "")

config.commence()
config.parse()

config.get_special_value("device", "sensitivity", "my-mouse")    # 0.5
config.get_special_value("device", "kb_layout", "my-keyboard")   # "us"

config.list_keys_for_special_category("device")  # ["my-mouse", "my-keyboard"]

config.special_category_exists("device", "my-mouse")  # True
```

The high-level `Config` class also exposes these:

```python
import hyprlang_pybind as hyprlang

config = hyprlang.Config(text, is_stream=True)
config.add("placeholder", 0)
config.add_special_category("device", key="key")
config.add_special_value("device", "sensitivity", 0.0)
config.commence()
config.parse()
config.get_special("device", "sensitivity", "my-mouse")
config.list_special_keys("device")
```
