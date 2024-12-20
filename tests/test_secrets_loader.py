import os
import pytest

from config_loader.secrets_loader import parse_secrets, get_secrets, load_secrets


# Set up environment variables before the test


def test_parse_secrets_success():
    config = {
        "database": "${DB_PASSWORD}",
        "apikey": "${API_KEY}",
        "plain_secret": "my_secret",
    }

    expected_output = {
        "database": "secret_pass",
        "apikey": "12345",
        "plain_secret": "my_secret",
    }

    result = parse_secrets(config)
    assert result == expected_output


def test_parse_secrets_missing_env_var():
    secrets = {"database": "${DB_PASSWORD}", "missing_var": "${MISSING_VAR}"}

    with pytest.raises(
        ValueError, match="Environment variable 'MISSING_VAR' not found"
    ):
        parse_secrets(secrets)


def test_parse_secrets_no_env_var():
    secrets = {"plain_secret": "my_secret"}

    expected_output = {"plain_secret": "my_secret"}

    result = parse_secrets(secrets)
    assert result == expected_output


def test_get_secrets_success():
    secrets = ["DB_PASSWORD", "API_KEY"]

    expected_output = {
        "DB_PASSWORD": "secret_pass",
        "API_KEY": "12345",
    }

    result = get_secrets(secrets)
    assert result == expected_output


def test_load_secrets_file():
    secrets_filepath = "tests/test.env"
    secrets = load_secrets(secrets_filepath)

    assert secrets["DB_PASSWORD2"] == "secret_pass2"
    assert secrets["API_KEY2"] == "123456"


def test_env_secrets():
    secrets = {
        "database": "${DB_PASSWORD}",
        "apikey": "${API_KEY}",
        "plain_secret": "my_secret",
    }

    expected_output = {
        "database": "12345",
        "apikey": "12345",
        "plain_secret": "my_secret",
    }

    os.environ["DB_PASSWORD"] = "12345"
    os.environ["API_KEY"] = "12345"

    result = parse_secrets(secrets)
    assert result == expected_output

    del os.environ["DB_PASSWORD"]
    del os.environ["API_KEY"]

    assert pytest.raises(
        ValueError, match="Environment variable 'DB_PASSWORD' not found"
    )


def test_secrets_precendence():
    config = {
        "database": "${DB_PASSWORD}",
        "apikey": "${API_KEY}",
        "plain_secret": "my_secret",
    }

    expected_output = {
        "database": "12345",
        "apikey": "12345",
        "plain_secret": "my_secret",
    }

    os.environ["DB_PASSWORD"] = "UNWANTED"
    os.environ["API_KEY"] = "UNWANTED"

    secrets = {
        "DB_PASSWORD": "12345",
        "API_KEY": "12345",
    }

    result = parse_secrets(config, secrets)

    assert result == expected_output
