import os
from pathlib import Path
import pytest
from config_loader import ConfigLoader

# Sample file paths for testing (assuming you have these test files in a `tests` directory)
config_file_mapping = {
    "yaml": Path("tests/config-test.yaml"),
    "toml": Path("tests/config-test.toml"),
    "json": Path("tests/config-test.json"),
    "toml2": Path("tests/config2-test.toml"),
    "defaultonly": Path("tests/defaultonly.toml"),
}
default_directory = Path("tests/default/")


@pytest.fixture(params=["yaml", "toml", "json"])
def config_file(request):
    return ConfigLoader(filepaths=[config_file_mapping[request.param]])


@pytest.fixture
def multiple_configs():
    return ConfigLoader([config_file_mapping["yaml"], config_file_mapping["toml2"]])


@pytest.fixture
def multiple_configs_duplicate():
    return ConfigLoader([config_file_mapping["yaml"], config_file_mapping["toml"]])


@pytest.fixture
def default_only_config():
    return ConfigLoader(
        [config_file_mapping["defaultonly"]], default_directory=default_directory
    )


@pytest.fixture(autouse=True)
def setup_env_vars():
    os.environ["DB_PASSWORD"] = "secret_pass"
    os.environ["API_KEY"] = "12345"
    yield
    # Clean up environment variables after the test
    del os.environ["DB_PASSWORD"]
    del os.environ["API_KEY"]
