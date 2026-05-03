import os
import unittest
from types import SimpleNamespace

import config


class TestConfig(unittest.TestCase):

    def setUp(self):
        config._config = {}
        for key in ["TEST_PARAM", "JSON_PARAM", "plain_arg", "list_arg"]:
            os.environ.pop(key, None)

    def tearDown(self):
        config._config = None
        for key in ["TEST_PARAM", "JSON_PARAM", "plain_arg", "list_arg"]:
            os.environ.pop(key, None)

    def test_convert_to_typed_value_json_number(self):
        result = config.convert_to_typed_value("123")
        self.assertEqual(result, 123)

    def test_convert_to_typed_value_json_list(self):
        result = config.convert_to_typed_value("[1, 2, 3]")
        self.assertEqual(result, [1, 2, 3])

    def test_convert_to_typed_value_plain_string(self):
        result = config.convert_to_typed_value("not json")
        self.assertEqual(result, "not json")

    def test_convert_to_typed_value_none(self):
        result = config.convert_to_typed_value(None)
        self.assertIsNone(result)

    def test_get_parameter_from_config(self):
        config._config = {"TEST_PARAM": "from_config"}

        result = config.get_parameter("TEST_PARAM")

        self.assertEqual(result, "from_config")

    def test_get_parameter_from_environment_overrides_config(self):
        config._config = {"TEST_PARAM": "from_config"}
        os.environ["TEST_PARAM"] = "from_env"

        result = config.get_parameter("TEST_PARAM")

        self.assertEqual(result, "from_env")

    def test_get_parameter_json_environment_value(self):
        config._config = {}
        os.environ["JSON_PARAM"] = "json:[1, 2]"

        result = config.get_parameter("JSON_PARAM")

        self.assertEqual(result, [1, 2])

    def test_get_parameter_default(self):
        config._config = {}

        result = config.get_parameter("MISSING_PARAM", "default_value")

        self.assertEqual(result, "default_value")

    def test_get_parameter_missing_returns_none(self):
        config._config = {}

        result = config.get_parameter("MISSING_PARAM")

        self.assertIsNone(result)

    def test_set_parameter_string(self):
        config._config = {}

        config.set_parameter("TEST_PARAM", "hello")

        self.assertEqual(os.environ["TEST_PARAM"], "hello")

    def test_set_parameter_list(self):
        config._config = {}

        config.set_parameter("JSON_PARAM", [1, 2, 3])

        self.assertEqual(os.environ["JSON_PARAM"], "json:[1, 2, 3]")

    def test_overwrite_from_args(self):
        config._config = {}
        args = SimpleNamespace(plain_arg="hello", list_arg=[1, 2], empty_arg=None)

        config.overwrite_from_args(args)

        self.assertEqual(os.environ["plain_arg"], "hello")
        self.assertEqual(os.environ["list_arg"], "json:[1, 2]")
        self.assertNotIn("empty_arg", os.environ)


if __name__ == "__main__":
    unittest.main()
