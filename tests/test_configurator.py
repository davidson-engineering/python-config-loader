import pytest
from pathlib import Path
from config_loader import ConfigLoader

# Sample file paths for testing (assuming you have these test files in a `tests` directory)
YAML_FILE = Path("tests/config-test.yaml")
TOML_FILE = Path("tests/config-test.toml")
JSON_FILE = Path("tests/config-test.json")
TOML2_FILE = Path("tests/config2-test.toml")
YAML_DEFAULT = Path("tests/default/config-default.yaml")
TOML_DEFAULT = Path("tests/default/config-default.toml")


@pytest.fixture
def yaml_config():
    return ConfigLoader([YAML_FILE])


@pytest.fixture
def toml_config():
    return ConfigLoader([TOML_FILE])


@pytest.fixture
def json_config():
    return ConfigLoader([JSON_FILE])


@pytest.fixture
def multiple_configs():
    return ConfigLoader([YAML_FILE, TOML2_FILE])


@pytest.fixture
def multiple_configs_duplicate():
    return ConfigLoader([YAML_FILE, TOML_FILE])


def test_yaml_loading(yaml_config):
    config = yaml_config.load()
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


def test_toml_loading(toml_config):
    config = toml_config.load()
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


def test_json_loading(json_config):
    config = json_config.load()
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
    with pytest.raises(ValueError):
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
    config_loader = ConfigLoader([YAML_FILE], default_filepath=TOML_DEFAULT)
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
    assert config["settings"]["clarity"] == 0.9


def test_load_configs_function(multiple_configs):
    from config_loader import load_configs

    configs = load_configs([YAML_FILE, TOML2_FILE])
    for config in configs:
        assert configs[config]["name"] == "Example"
        assert configs[config]["version"] == 1.0
        assert configs[config]["settings"]["debug"] is True
        assert configs[config]["settings"]["max_connections"] == 10
        assert configs[config]["settings"]["threshold"] == 0.85
        assert configs[config]["settings"]["timeout"] == 30.5
