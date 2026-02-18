# Error Handling

## High-level API

The high-level API raises `hyprlang_pybind.HyprlangError` on parse failures:

```python
import hyprlang_pybind as hyprlang

try:
    data = hyprlang.parse_string("unclosed {", schema={"x": 0})
except hyprlang.HyprlangError as e:
    print(f"Parse error: {e}")
```

## Low-level API

The low-level API returns `ParseResult` objects instead of raising:

```python
from hyprlang_pybind._core import Config, ConfigOptions

opts = ConfigOptions()
opts.path_is_stream = 1
config = Config("x = abc", opts)
config.add_value("x", 0)
config.commence()

result = config.parse()
if result.error:
    print(result.error_message)
```

## Collecting all errors

By default, parsing stops at the first error. To collect all errors:

```python
data = hyprlang.parse_string(text, schema=schema, throw_all_errors=True)

config = hyprlang.Config(path, throw_all_errors=True)
```
