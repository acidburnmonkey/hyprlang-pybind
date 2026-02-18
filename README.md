# hyprlang-pybind

Python bindings for [hyprlang](https://github.com/hyprwm/hyprlang), the configuration language used by Hyprland and other Hypr projects.

Built with pybind11, providing both a high-level Pythonic API and a low-level API that mirrors the C++ interface.

## Quick Start

```python
import hyprlang_pybind as hyprlang

data = hyprlang.parse_string("""
general {
    border_size = 3
    gaps_in = 5.0
    layout = dwindle
}
""")

print(data["general"]["border_size"])  # 3
print(data["general"]["gaps_in"])      # 5.0
print(data["general"]["layout"])       # "dwindle"
```

Schema is optional. When omitted, keys and types are auto-inferred from the config contents. You can also provide an explicit schema for precise type control:

```python
data = hyprlang.parse_file("/path/to/config.conf", schema={
    "general": {
        "border_size": 0,
        "gaps_in": 0.0,
        "layout": "",
    },
})
```

## Documentation

- [Installation](docs/installation.md)
- [High-Level API](docs/high-level-api.md) &mdash; `parse_string`, `parse_file`, `Config` class
- [Low-Level API](docs/low-level-api.md) &mdash; Direct C++ bindings
- [Schema Reference](docs/schema.md) &mdash; Type mapping and nested schemas
- [Hyprlang Syntax Guide](docs/syntax.md) &mdash; Config file format reference
- [Error Handling](docs/error-handling.md)
- [Building from Source](docs/building.md)
