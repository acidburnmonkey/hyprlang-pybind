# Building from Source

## Requirements

- Python 3.13+
- `hyprlang` and `hyprutils` development headers (installed via your system package manager)
- A C++23 compiler (GCC 13+, Clang 17+)
- The build uses pkg-config to locate the system hyprlang library

## Setup

```sh
git clone https://github.com/viving-studio/hyprlang-pybind.git
cd hyprlang-pybind

uv venv
uv pip install scikit-build-core pybind11

uv pip install -e . --no-build-isolation
```

## Running tests

```sh
uv run pytest tests/ -v
```
