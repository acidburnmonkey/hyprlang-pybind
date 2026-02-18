"""Tests for the high-level Pythonic API."""

import os
import pytest
import hyprlang_pybind as hyprlang

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
TEST_CONF = os.path.join(FIXTURES, "test.conf")


class TestParseString:
    def test_basic_types(self):
        data = hyprlang.parse_string(
            "myInt = 42\nmyFloat = 3.14\nmyStr = hello world",
            schema={
                "myInt": 0,
                "myFloat": 0.0,
                "myStr": "",
            },
        )
        assert data["myInt"] == 42
        assert abs(data["myFloat"] - 3.14) < 0.01
        assert data["myStr"] == "hello world"

    def test_nested_schema(self):
        data = hyprlang.parse_string(
            "general:border = 5\ngeneral:gap = 10.0",
            schema={
                "general": {
                    "border": 0,
                    "gap": 0.0,
                },
            },
        )
        assert data["general"]["border"] == 5
        assert abs(data["general"]["gap"] - 10.0) < 0.01

    def test_category_syntax(self):
        data = hyprlang.parse_string(
            "mycat {\n  val = 99\n}\n",
            schema={
                "mycat": {
                    "val": 0,
                },
            },
        )
        assert data["mycat"]["val"] == 99

    def test_variables(self):
        data = hyprlang.parse_string(
            "$X = 100\nmyVal = $X",
            schema={"myVal": 0},
        )
        assert data["myVal"] == 100

    def test_boolean_values(self):
        data = hyprlang.parse_string(
            "a = true\nb = false\nc = yes\nd = no",
            schema={"a": 0, "b": 0, "c": 0, "d": 0},
        )
        assert data["a"] == 1
        assert data["b"] == 0
        assert data["c"] == 1
        assert data["d"] == 0

    def test_hex_int(self):
        data = hyprlang.parse_string(
            "color = 0xFF0000",
            schema={"color": 0},
        )
        assert data["color"] == 0xFF0000


class TestParseFile:
    def test_basic(self):
        data = hyprlang.parse_file(
            TEST_CONF,
            schema={
                "testInt": 0,
                "testFloat": 0.0,
                "testString": "",
                "testCategory": {
                    "innerInt": 0,
                    "innerString": "",
                },
            },
        )
        assert data["testInt"] == 123
        assert abs(data["testFloat"] - 123.456) < 0.01
        assert data["testString"] == "Hello World"
        assert data["testCategory"]["innerInt"] == 42
        assert data["testCategory"]["innerString"] == "nested value"


class TestConfigClass:
    def test_basic_usage(self):
        config = hyprlang.Config(
            "val = 7\nname = test",
            is_stream=True,
        )
        config.add("val", 0)
        config.add("name", "")
        config.commence()
        config.parse()

        assert config["val"] == 7
        assert config["name"] == "test"
        assert config.get("val") == 7
        assert config.get("missing", "default") == "default"

    def test_to_dict(self):
        config = hyprlang.Config("x = 1\ny = 2", is_stream=True)
        config.add("x", 0)
        config.add("y", 0)
        config.commence()
        config.parse()

        d = config.to_dict()
        assert d == {"x": 1, "y": 2}

    def test_to_dict_nested(self):
        config = hyprlang.Config(
            "cat {\n  a = 10\n  b = 20\n}\n",
            is_stream=True,
        )
        config.add("cat:a", 0)
        config.add("cat:b", 0)
        config.commence()
        config.parse()

        d = config.to_dict()
        assert d == {"cat": {"a": 10, "b": 20}}

    def test_is_set_by_user(self):
        config = hyprlang.Config("a = 1", is_stream=True)
        config.add("a", 0)
        config.add("b", 99)
        config.commence()
        config.parse()

        assert config.is_set_by_user("a") is True
        assert config.is_set_by_user("b") is False

    def test_parse_dynamic(self):
        config = hyprlang.Config("x = 1", is_stream=True)
        config.add("x", 0)
        config.commence()
        config.parse()

        assert config["x"] == 1
        config.parse_dynamic("x = 42")
        assert config["x"] == 42

    def test_error_raises(self):
        with pytest.raises((hyprlang.HyprlangError, RuntimeError)):
            config = hyprlang.Config("/nonexistent/file.conf")
            config.add("x", 0)
            config.commence()
            config.parse()

    def test_contains(self):
        config = hyprlang.Config("x = 1", is_stream=True)
        config.add("x", 0)
        config.commence()
        config.parse()
        assert "x" in config

    def test_add_after_commence_raises(self):
        config = hyprlang.Config("x = 1", is_stream=True)
        config.add("x", 0)
        config.commence()
        with pytest.raises(hyprlang.HyprlangError):
            config.add("y", 0)

    def test_raw_access(self):
        config = hyprlang.Config("x = 1", is_stream=True)
        config.add("x", 0)
        config.commence()
        config.parse()
        assert config.raw.get_value("x") == 1


class TestParseStringErrors:
    """Test that genuinely invalid syntax raises an error."""

    def test_invalid_syntax(self):
        with pytest.raises(hyprlang.HyprlangError):
            hyprlang.parse_string(
                "mycat {\n  val = 1\n",
                schema={"mycat": {"val": 0}},
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
