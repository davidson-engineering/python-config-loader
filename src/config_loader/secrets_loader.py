import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from dotenv import dotenv_values

import logging

logger = logging.getLogger(__name__)

FILEPATH_SECRETS_DEFAULT = Path(".env")
MIN_EXPOSED_LENGTH = 3
MAX_VISIBLE_LENGTH = 15


def load_secrets(filepath: Union[str, Path] = None) -> Dict:
    """
    Load secrets from environment variables and an optional `.env` file.

    This function combines secrets from the system's environment variables and
    a specified `.env` file. If no filepath is provided, it defaults to `./.env`.

    Args:
        filepath: Path to the `.env` file. Defaults to `.env`.

    Returns:
        A dictionary containing secrets from both the environment variables
        and the `.env` file. Secrets from the environment override those from
        the `.env` file.

    Raises:
        FileNotFoundError: If the specified `.env` file does not exist.
    """
    env_secrets = {key: value for key, value in os.environ.items()}

    if filepath is None and FILEPATH_SECRETS_DEFAULT.exists():
        logger.warning(
            f"No secrets file specified, but file found at {FILEPATH_SECRETS_DEFAULT}. Loading secrets from {FILEPATH_SECRETS_DEFAULT}"
        )
        filepath = FILEPATH_SECRETS_DEFAULT

    if filepath is None:
        logger.info(
            f"No secrets file specified and no file found at {FILEPATH_SECRETS_DEFAULT}. Loading secrets from environment only"
        )
        return env_secrets

    if isinstance(filepath, str):
        filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Specified secrets file was not found: '{filepath}'")

    file_secrets = dotenv_values(filepath)
    logger.info(
        f"Loaded {len(file_secrets)} secrets from file: '{filepath}'",
        extra={"secrets": file_secrets.keys()},
    )
    return {**env_secrets, **file_secrets}


def get_secrets(secrets: List[str] = None) -> Dict:
    """
    Retrieve specified secrets from the environment variables.

    If no secrets are specified, all environment variables are returned.
    Otherwise, only the specified secrets are retrieved.

    Args:
        secrets: A list of secret names to retrieve from the environment variables.
                 Defaults to `None`, which retrieves all environment variables.

    Returns:
        A dictionary containing the requested secrets and their values.

    Raises:
        KeyError: If a requested secret is not found in the environment variables.
    """
    if secrets is None:
        return dict(os.environ)

    for secret in secrets:
        if secret not in os.environ:
            raise KeyError(f"Secret not found: '{secret}'")

    return {secret: os.getenv(secret) for secret in secrets}


def parse_secrets(configs: Dict, secrets: Optional[Dict] = None) -> Dict:
    """
    Replace environment variable placeholders in configuration values.

    This function recursively parses a configuration dictionary to replace
    placeholders (in the form `${VAR_NAME}`) with values from the provided
    secrets dictionary. If no secrets dictionary is provided, it loads secrets
    using the `load_secrets` function.

    Args:
        configs: A dictionary containing configurations with potential environment variable placeholders.
        secrets: An optional dictionary of secrets to use for placeholder replacement.
                 If `None`, secrets are loaded using `load_secrets`.

    Returns:
        The configuration dictionary with environment variable placeholders replaced.

    Raises:
        ValueError: If a placeholder references an environment variable that is not found.

    Example:
        configs = {
            "api_key": "${API_KEY}",
            "nested": {"url": "http://${HOST}:${PORT}"}
        }
        secrets = {"API_KEY": "12345", "HOST": "example.com", "PORT": "8080"}

        parse_secrets(configs, secrets)
        # Result:
        # {
        #     "api_key": "12345",
        #     "nested": {"url": "http://example.com:8080"}
        # }
    """
    env_var_pattern = re.compile(r"\$\{(\w+)\}")

    def replace_env_var(match):
        """
        Replace a matched environment variable placeholder with its value.

        Args:
            match: A regex match object for the placeholder.

        Returns:
            The value of the matched environment variable.

        Raises:
            ValueError: If the variable is not found in the secrets dictionary.
        """
        var_name = match.group(1)
        if var_name in secrets:
            visible_length = min(MIN_EXPOSED_LENGTH, len(secrets[var_name]))
            max_total_length = max(MAX_VISIBLE_LENGTH, len(secrets[var_name]))
            logger.debug(
                f"Replacing placeholder with value: `{var_name}` -> `{secrets[var_name][:visible_length]}{(max_total_length-visible_length) * '*'}`"
            )
            return secrets[var_name]
        else:
            raise ValueError(f"Environment variable '{var_name}' not found")

    def parse_value(value):
        """
        Recursively parse a value to replace environment variable placeholders.

        Args:
            value: The value to parse. Can be a string, dictionary, or list.

        Returns:
            The parsed value with placeholders replaced.
        """
        if isinstance(value, dict):
            # Recursively process dictionaries
            for k, v in value.items():
                value[k] = parse_value(v)
            return value
        elif isinstance(value, list):
            # Recursively process lists
            return [parse_value(item) for item in value]
        elif isinstance(value, str):
            # Apply regex substitution for placeholders in strings
            return env_var_pattern.sub(replace_env_var, value)
        else:
            # Return other types unchanged
            return value

    if secrets is None:
        secrets = load_secrets()
    if not secrets:
        return configs

    return parse_value(configs)
