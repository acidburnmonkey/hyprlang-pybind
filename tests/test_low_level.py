"""Tests for the low-level _core bindings."""

import os
import pytest
from hyprlang_pybind._core import Config, ConfigOptions, ParseResult, SVector2D

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
TEST_CONF = os.path.join(FIXTURES, "test.conf")


class TestSVector2D:
    def test_create_default(self):
        v = SVector2D()
        assert v.x == 0.0
        assert v.y == 0.0

    def test_create_with_args(self):
        v = SVector2D(1.5, 2.5)
        assert v.x == 1.5
        assert v.y == 2.5

    def test_equality(self):
        assert SVector2D(1.0, 2.0) == SVector2D(1.0, 2.0)
        assert not (SVector2D(1.0, 2.0) == SVector2D(3.0, 4.0))

    def test_repr(self):
        v = SVector2D(1.0, 2.0)
        assert "1.0" in repr(v)
        assert "2.0" in repr(v)


class TestParseResult:
    def test_default_ok(self):
        r = ParseResult()
        assert not r.error
        assert r.error_message is None
        assert bool(r) is True

    def test_repr(self):
        r = ParseResult()
        assert "ok" in repr(r)


class TestConfigOptions:
    def test_defaults(self):
        opts = ConfigOptions()
        assert opts.verify_only == 0
        assert opts.throw_all_errors == 0
        assert opts.allow_missing_config == 0
        assert opts.path_is_stream == 0


class TestConfigBasic:
    def test_parse_file(self):
        config = Config(TEST_CONF)
        config.add_value("testInt", 0)
        config.add_value("testFloat", 0.0)
        config.add_value("testString", "")
        config.add_value("testVar", 0)
        config.add_value("testColor", 0)
        config.add_value("testCategory:innerInt", 0)
        config.add_value("testCategory:innerString", "")
        config.add_value("testVec", SVector2D(0.0, 0.0))
        config.add_value("testBool", 0)
        config.commence()

        result = config.parse()
        assert not result.error, result.error_message

        assert config.get_value("testInt") == 123
        assert abs(config.get_value("testFloat") - 123.456) < 0.01
        assert config.get_value("testString") == "Hello World"
        assert config.get_value("testVar") == 420
        assert config.get_value("testCategory:innerInt") == 42
        assert config.get_value("testCategory:innerString") == "nested value"
        assert config.get_value("testBool") == 1

    def test_parse_stream(self):
        opts = ConfigOptions()
        opts.path_is_stream = 1
        config = Config("myInt = 42\nmyStr = hello", opts)
        config.add_value("myInt", 0)
        config.add_value("myStr", "")
        config.commence()

        result = config.parse()
        assert not result.error, result.error_message

        assert config.get_value("myInt") == 42
        assert config.get_value("myStr") == "hello"

    def test_parse_dynamic(self):
        opts = ConfigOptions()
        opts.path_is_stream = 1
        config = Config("myVal = 10", opts)
        config.add_value("myVal", 0)
        config.commence()
        config.parse()

        assert config.get_value("myVal") == 10

        result = config.parse_dynamic("myVal = 99")
        assert not result.error
        assert config.get_value("myVal") == 99

    def test_get_value_info(self):
        opts = ConfigOptions()
        opts.path_is_stream = 1
        config = Config("setVal = 5", opts)
        config.add_value("setVal", 0)
        config.add_value("unsetVal", 100)
        config.commence()
        config.parse()

        info_set = config.get_value_info("setVal")
        assert info_set.set_by_user is True
        assert info_set.value == 5

        info_unset = config.get_value_info("unsetVal")
        assert info_unset.set_by_user is False
        assert info_unset.value == 100

    def test_vec2(self):
        opts = ConfigOptions()
        opts.path_is_stream = 1
        config = Config("myVec = 1.5 2.5", opts)
        config.add_value("myVec", SVector2D(0.0, 0.0))
        config.commence()
        config.parse()

        val = config.get_value("myVec")
        assert isinstance(val, tuple)
        assert abs(val[0] - 1.5) < 0.01
        assert abs(val[1] - 2.5) < 0.01

    def test_missing_config_error(self):
        try:
            config = Config("/nonexistent/path/config.conf")
            config.add_value("x", 0)
            config.commence()
            result = config.parse()
            assert result.error
        except RuntimeError:
            pass

    def test_allow_missing_config(self):
        opts = ConfigOptions()
        opts.allow_missing_config = 1
        config = Config("/nonexistent/path/config.conf", opts)
        config.add_value("x", 0)
        config.commence()
        result = config.parse()
        assert not result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
