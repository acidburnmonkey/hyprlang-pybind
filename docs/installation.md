# Installation

## Prerequisites

- Python 3.13+
- `hyprlang-devel` and `hyprutils-devel` system packages
- A C++23 compiler (GCC 13+, Clang 17+)

### Fedora (with Hyprland my COPR)

```sh
sudo dnf install hyprlang-devel hyprutils-devel
```

### Arch

```sh
sudo pacman -S hyprlang
```

## Install with uv

clone this repo and

```sh
uv pip install .
```

## Install with pip

- Note you will need : hyprlang-devel and C++ compiler installed since it links with `libhyprlang.so` if downloading from pip

```
pip install hyprlang-pybind
```

For development:

```sh
uv pip install -e . --no-build-isolation
```

See [Building from Source](building.md) for the full development setup.
