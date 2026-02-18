# Installation

## Prerequisites

- Python 3.13+
- `hyprlang-devel` and `hyprutils-devel` system packages
- A C++23 compiler (GCC 13+, Clang 17+)

### Fedora (with Hyprland COPR)

```sh
sudo dnf install hyprlang-devel hyprutils-devel
```

### Arch

```sh
sudo pacman -S hyprlang
```

## Install with uv

```sh
uv pip install .
```

For development:

```sh
uv pip install -e . --no-build-isolation
```

See [Building from Source](building.md) for the full development setup.
