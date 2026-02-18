# Hyprlang Syntax Guide

A brief reference for the config syntax that hyprlang parses.

## Basic values

```ini
my_int = 42
my_float = 3.14
my_string = hello world
my_bool = true
my_hex = 0xDEADBEEF
my_vec = 1920 1080
```

## Comments

```ini
# This is a comment
key = value  # inline comment
key2 = value with ## literal hash  # the ## becomes a literal #
```

## Variables

```ini
$GAP = 10
$BORDER = 3

gaps_in = $GAP
border_size = $BORDER
combined = $GAP$BORDER    # string concatenation: "103"
```

## Expressions

```ini
$BASE = 10
computed = {{BASE + 5}}      # 15
doubled = {{BASE * 2}}       # 20

literal = \{{not an expression}}
```

## Categories (nesting)

```ini
general {
    border_size = 3

    subcategory {
        inner_value = 42
    }
}
```

## Colors

Colors are stored as `INT` (int64) in ARGB format.

```ini
color1 = rgba(255, 128, 0, 0.8)   # RGBA with float alpha (0.0-1.0)
color2 = rgba(FF8000CC)            # RGBA hex (8 digits)
color3 = rgb(255, 128, 0)          # RGB (alpha defaults to 1.0)
color4 = rgb(FF8000)               # RGB hex (6 digits)
```

## Source (includes)

```ini
source = ./colors.conf
source = ~/.config/hypr/extra.conf
```

## Boolean values

All of these are valid boolean representations (stored as INT 0 or 1):

```ini
enabled = true     # 1
enabled = false    # 0
enabled = yes      # 1
enabled = no       # 0
enabled = on       # 1
enabled = off      # 0
```

## Multiline

```ini
long_value = this is \
    a very \
    long value
```
