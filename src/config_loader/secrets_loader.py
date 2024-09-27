import os
import re
from pathlib import Path
from typing import Union

from dotenv import load_dotenv

FILEPATH_SECRETS_DEFAULT = Path("./.env")


def load_secrets(filepath: Union[str, Path] = None) -> dict:
    """Load secrets from environment or a specified .env file"""
    filepath = filepath or FILEPATH_SECRETS_DEFAULT
    if isinstance(filepath, str):
        filepath = Path(filepath)

    if not Path(filepath).exists() and filepath != FILEPATH_SECRETS_DEFAULT:
        raise FileNotFoundError(f"File not found: {filepath}")

    load_dotenv(filepath)


def get_secrets(secrets: list[str] = None) -> dict:
    """Return specified secrets from environment"""
    if secrets is None:
        return dict(os.environ)

    for secret in secrets:
        if secret not in os.environ:
            raise KeyError(f"Secret not found: {secret}")

    secrets = {secret: os.getenv(secret) for secret in secrets}

    return secrets


def parse_secrets(configs: dict) -> dict:
    """Parse secrets in configs, recursively replacing environment variables."""
    env_var_pattern = re.compile(r"\$\{(\w+)\}")

    def replace_env_var(match):
        var_name = match.group(1)
        if var_name in os.environ:
            return os.environ[var_name]
        else:
            raise ValueError(f"Environment variable '{var_name}' not found")

    def parse_value(value):
        """Recursively parse a value to replace environment variables."""
        if isinstance(value, dict):
            # Recursively process dictionaries
            for k, v in value.items():
                value[k] = parse_value(v)
            return value
        elif isinstance(value, list):
            # Recursively process lists
            return [parse_value(item) for item in value]
        elif isinstance(value, str):
            # Apply the regex substitution to strings
            return env_var_pattern.sub(replace_env_var, value)
        else:
            # Return the value unchanged if it's not a string, dict, or list
            return value

    # Modify the original configs in place
    return parse_value(configs)
