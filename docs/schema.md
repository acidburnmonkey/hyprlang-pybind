# Schema Reference

Schemas map config key names to default values. The type of each default determines how hyprlang parses the value.

| Python Default       | Hyprlang Type | Parsed As                       | Examples                              |
| -------------------- | ------------- | ------------------------------- | ------------------------------------- |
| `0` (int)            | `INT` (int64) | Integer, hex, boolean, or color | `42`, `0xFF00FF`, `true`, `rgba(...)` |
| `0.0` (float)        | `FLOAT`       | Floating point                  | `3.14`, `0.5`                         |
| `""` (str)           | `STRING`      | String                          | `hello world`, `dwindle`              |
| `(0.0, 0.0)` (tuple) | `VEC2`        | Two space-separated floats      | `1920 1080`                           |
| `SVector2D(0, 0)`    | `VEC2`        | Same as tuple                   | `1920 1080`                           |

Schema is optional for `parse_file()` and `parse_string()`. When omitted, types are auto-inferred from the config contents. See [High-Level API](high-level-api.md#schema-auto-inference) for details on how inference works.

## Nested schemas

Nested dicts are flattened into colon-separated keys:

```python
schema = {
    "general": {
        "border_size": 0,
        "inner": {
            "value": 0,
        },
    },
}

# Is equivalent to:
schema_flat = {
    "general:border_size": 0,
    "general:inner:value": 0,
}
```

Both work with `parse_file()`, `parse_string()`, and the `Config` class.

In your config file, nested keys can be written with either syntax:

```ini
general {
    border_size = 5
    inner {
        value = 10
    }
}

general:border_size = 5
general:inner:value = 10
```
