import pytest
from pathlib import Path
from config_loader import ConfigLoader
from config_loader.config_loader import DuplicateConfigKeyError

from tests.conftest import config_file_mapping


def test_file_loading(config_file):
    config = config_file.load()
    assert config["name"] == "Example"
    assert config["version"] == 1.0
    assert config["settings"]["debug"] is True
    assert config["settings"]["max_connections"] == 10
    assert config["settings"]["threshold"] == 0.85
    assert config["settings"]["timeout"] == 30.5
    assert config["settings"]["nested_dict"]["inner_key"] == "inner_value"
    assert config["settings"]["nested_dict"]["inner_list"] == [1, 2, 3]
    assert config["settings"]["complex_list"][0]["key1"] == "value1"
    assert config["settings"]["complex_list"][2]["key3"] == [10, 20, 30]


def test_duplicate_loading(multiple_configs_duplicate):
    with pytest.raises(DuplicateConfigKeyError):
        multiple_configs_duplicate.load()


def test_multiple_loading(multiple_configs):
    configs = multiple_configs.load()
    for config in configs:
        assert configs[config]["name"] == "Example"
        assert configs[config]["version"] == 1.0
        assert configs[config]["settings"]["debug"] is True
        assert configs[config]["settings"]["max_connections"] == 10
        assert configs[config]["settings"]["threshold"] == 0.85
        assert configs[config]["settings"]["timeout"] == 30.5


def test_merge_configs_function():
    default_config = {
        "name": "Default",
        "settings": {
            "debug": False,
            "max_connections": 5,
            "threshold": 0.75,
            "timeout": 15.5,
            "clarity": 0.9,
            "nested_dict": {
                "inner_key": "default_value",
                "inner_list": [4, 5, 6],
                "extra_key": "default",
            },
            "complex_list": [
                {"key1": "default_value"},
                {"key2": "default_value"},
                {"key3": "default_value"},
            ],
        },
    }

    user_config = {
        "name": "Example",
        "settings": {
            "debug": True,
            "max_connections": 10,
            "threshold": 0.85,
            "timeout": 30.5,
            "nested_dict": {"inner_key": "inner_value", "inner_list": [1, 2, 3]},
            "complex_list": [
                {"key1": "value1"},
                {"key2": "value2"},
                {"key3": [10, 20, 30]},
            ],
        },
    }

    config_loader = ConfigLoader([])
    merged = config_loader._merge_configs(default_config, user_config)

    assert merged["name"] == "Example"
    assert merged["settings"]["debug"] is True
    assert merged["settings"]["max_connections"] == 10
    assert merged["settings"]["threshold"] == 0.85
    assert merged["settings"]["timeout"] == 30.5
    assert merged["settings"]["nested_dict"]["inner_key"] == "inner_value"
    assert merged["settings"]["nested_dict"]["inner_list"] == [1, 2, 3]
    assert merged["settings"]["nested_dict"]["extra_key"] == "default"
    assert merged["settings"]["complex_list"][0]["key1"] == "value1"
    assert merged["settings"]["complex_list"][1]["key2"] == "value2"
    assert merged["settings"]["complex_list"][2]["key3"] == [10, 20, 30]
    assert merged["settings"]["clarity"] == 0.9


def test_custom_default_filepath():
    FILE1 = config_file_mapping["yaml"]
    DEFAULT_DIRECTORY = Path("tests/default2/")
    config_loader = ConfigLoader([FILE1], default_directory=DEFAULT_DIRECTORY)
    config = config_loader.load()
    assert config["name"] == "Example"
    assert config["version"] == 1.0
    assert config["settings"]["debug"] is True
    assert config["settings"]["max_connections"] == 10
    assert config["settings"]["threshold"] == 0.85
    assert config["settings"]["timeout"] == 30.5
    assert config["settings"]["nested_dict"]["inner_key"] == "inner_value"
    assert config["settings"]["nested_dict"]["inner_list"] == [1, 2, 3]
    assert config["settings"]["complex_list"][0]["key1"] == "value1"
    assert config["settings"]["complex_list"][2]["key3"] == [10, 20, 30]
    assert config["settings"]["default_unique_key"] == "other_value"


def test_custom_default_incorrect_suffix():
    FILE = config_file_mapping["json"]
    DEFAULT_DIRECTORY = Path("tests/default2/")
    config_loader = ConfigLoader([FILE], default_directory=DEFAULT_DIRECTORY)
    config = config_loader.load()
    assert config["name"] == "Example"
    assert config["version"] == 1.0
    assert config["settings"]["debug"] is True
    assert config["settings"]["max_connections"] == 10
    assert config["settings"]["threshold"] == 0.85
    assert config["settings"]["timeout"] == 30.5
    assert config["settings"]["nested_dict"]["inner_key"] == "inner_value"
    assert config["settings"]["nested_dict"]["inner_list"] == [1, 2, 3]
    assert config["settings"]["complex_list"][0]["key1"] == "value1"
    assert config["settings"]["complex_list"][2]["key3"] == [10, 20, 30]
    assert config["settings"]["default_unique_key"] == "other_value"


def test_load_configs_function(multiple_configs):
    from config_loader import load_configs

    FILE1 = config_file_mapping["yaml"]
    FILE2 = config_file_mapping["toml2"]

    configs = load_configs([FILE1, FILE2])
    for config in configs:
        assert configs[config]["name"] == "Example"
        assert configs[config]["version"] == 1.0
        assert configs[config]["settings"]["debug"] is True
        assert configs[config]["settings"]["max_connections"] == 10
        assert configs[config]["settings"]["threshold"] == 0.85
        assert configs[config]["settings"]["timeout"] == 30.5


def test_default_only(default_only_config):
    """
    [primary]
    primary_0 = 'A'
    primary_1 = 'B'
    primary_2 = 'C'

    [primary.secondary]
    secondary_0 = 'D'
    secondary_1 = 'E'
    secondary_2 = 'F'

    [primary.secondary.tertiary]
    tertiary_0 = 'G'
    tertiary_1 = 'H'
    tertiary_2 = 'I'
    """
    config = default_only_config.load()

    assert config["primary"]["primary_0"] == "A"
    assert config["primary"]["primary_1"] == "B"
    assert config["primary"]["primary_2"] == "C"
    assert config["primary"]["secondary"]["secondary_0"] == "D"
    assert config["primary"]["secondary"]["secondary_1"] == "E"
    assert config["primary"]["secondary"]["secondary_2"] == "F"
    assert config["primary"]["secondary"]["tertiary"]["tertiary_0"] == "G"
    assert config["primary"]["secondary"]["tertiary"]["tertiary_1"] == "H"
    assert config["primary"]["secondary"]["tertiary"]["tertiary_2"] == "I"

    assert len(config) == 1
    assert len(config["primary"]) == 4
    assert len(config["primary"]["secondary"]) == 4
    assert len(config["primary"]["secondary"]["tertiary"]) == 3
