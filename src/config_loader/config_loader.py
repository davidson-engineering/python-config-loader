#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2024-09-07
# ---------------------------------------------------------------------------
"""
A module to load and merge configuration files from multiple formats.
Configuration files can be loaded from JSON, YAML, or TOML formats.
Default configurations can be provided to merge with user configurations.
"""
# ---------------------------------------------------------------------------

from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import logging

from .secrets_loader import load_secrets, parse_secrets

logger = logging.getLogger(__name__)


class DuplicateConfigKeyError(Exception):
    """
    Custom exception raised when multiple configuration files have the same stem.

    This helps prevent unintended overwriting of configurations when merging.
    """

    pass


def load_configs(
    filepaths: Union[str, Path, List[Union[str, Path]]],
    default_directory: Optional[Union[str, Path]] = None,
    secrets_filepath: Optional[Union[str, Path]] = None,
) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    """
    Load and merge configurations for the specified filepaths.

    Args:
        filepaths: A single file path or a list of file paths to load configurations from.
        default_directory: An optional directory containing default configurations.
        secrets_filepath: An optional file path for a secrets file to parse and merge.

    Returns:
        A merged configuration dictionary. If multiple filepaths are provided, returns
        a dictionary where the keys are the file stems and the values are the configurations.

    Raises:
        DuplicateConfigKeyError: If multiple filepaths have the same stem.
    """
    loader = ConfigLoader(filepaths, default_directory)
    configs = loader.load()
    loader.parse_secrets(configs, secrets_filepath)
    return configs


class ConfigLoader:
    """
    A class to load and merge configuration files from multiple formats.

    Supports JSON, YAML, and TOML formats, as well as optional default configurations
    located in a specified directory.
    """

    def __init__(
        self,
        filepaths: Union[str, Path, List[Union[str, Path]]],
        default_directory: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize the ConfigLoader with filepaths and an optional default directory.

        Args:
            filepaths: A single file path or a list of file paths to load configurations from.
            default_directory: An optional directory containing default configuration files.
        """
        if isinstance(filepaths, (str, Path)):
            self.filepaths = [Path(filepaths)]
        else:
            self.filepaths = [
                Path(filepath) if isinstance(filepath, str) else filepath
                for filepath in filepaths
            ]

        self.default_directory = (
            Path(default_directory)
            if default_directory
            else Path("config/default") if Path("config/default").exists() else None
        )

    def load(self) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """
        Load and merge configurations for the provided file paths.

        Returns:
            A single configuration dictionary if only one file path is provided.
            Otherwise, returns a dictionary where keys are file stems and values are merged configurations.

        Raises:
            FileNotFoundError: If neither the file nor its corresponding default configuration exists.
            DuplicateConfigKeyError: If multiple file paths have the same stem.
        """
        configs: Dict[str, Any] = {}

        for filepath in self.filepaths:
            stem = filepath.stem

            # Check for duplicate stems in the provided file paths
            if stem in configs:
                raise DuplicateConfigKeyError(
                    f"Duplicate configuration key detected: '{stem}' from file '{filepath}' conflicts with an existing file."
                )

            # Determine if a default configuration file exists for this file
            default_filepath = self._get_default_filepath(filepath)
            if not filepath.exists():
                if not default_filepath or not default_filepath.exists():
                    raise FileNotFoundError(
                        f"File not found: {filepath}. No default found in {self.default_directory}."
                    )
                logger.warning(
                    f"File not found: {filepath}. Using default from {default_filepath}."
                )

            # Load the default configuration and the user-provided configuration
            default_config = self._load_defaults(filepath)
            user_config = self._load_file(filepath) if filepath.exists() else {}
            configs[stem] = self._merge_configs(default_config, user_config)

        # Return a single configuration if only one file path was provided
        return configs[self.filepaths[0].stem] if len(self.filepaths) == 1 else configs

    def _load_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Load a single configuration file based on its extension.

        Supports JSON, YAML, and TOML formats.

        Args:
            filepath: The file path to load.

        Returns:
            A dictionary representing the loaded configuration.

        Raises:
            ValueError: If the file extension is unsupported.
        """
        if not filepath.exists():
            return {}
        if filepath.suffix == ".json":
            return self._load_json(filepath)
        elif filepath.suffix == ".yaml":
            return self._load_yaml(filepath)
        elif filepath.suffix == ".toml":
            return self._load_toml(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

    def _get_default_filepath(self, filepath: Path) -> Optional[Path]:
        """
        Get the default configuration file path corresponding to a given file.

        Args:
            filepath: The file path to find a default for.

        Returns:
            The path to the default configuration file, or None if it doesn't exist.
        """
        if self.default_directory is None:
            return None
        return self.default_directory / f"{filepath.stem}-default{filepath.suffix}"

    def _load_defaults(self, filepath: Path) -> Dict[str, Any]:
        """
        Load the default configuration file for a given file.

        Args:
            filepath: The file path for which to load the default configuration.

        Returns:
            A dictionary representing the default configuration.
        """
        default_path = self._get_default_filepath(filepath)

        if not default_path:
            return {}

        if default_path.suffix == filepath.suffix and default_path.exists():
            return self._load_file(default_path)

        # Search for alternate default files with a matching stem but different extensions
        for file in self.default_directory.iterdir():
            if (
                file.stem == f"{filepath.stem}-default"
                and file.suffix != filepath.suffix
            ):
                logger.warning(f"Loading default file with different extension: {file}")
                return self._load_file(file)

        return {}

    def _merge_configs(
        self, base_config: Dict[str, Any], new_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recursively merge two configuration dictionaries.

        Values from `new_config` overwrite those in `base_config`.

        Args:
            base_config: The base configuration dictionary.
            new_config: The new configuration dictionary to merge.

        Returns:
            The merged configuration dictionary.
        """
        for key, value in new_config.items():
            if (
                isinstance(value, dict)
                and key in base_config
                and isinstance(base_config[key], dict)
            ):
                base_config[key] = self._merge_configs(base_config[key], value)
            else:
                base_config[key] = value
        return base_config

    def _load_json(self, filepath: Path) -> Dict[str, Any]:
        """
        Load a JSON configuration file.

        Args:
            filepath: The JSON file path.

        Returns:
            A dictionary representing the loaded configuration.
        """
        import json

        with open(filepath, "r") as file:
            return json.load(file)

    def _load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """
        Load a YAML configuration file.

        Args:
            filepath: The YAML file path.

        Returns:
            A dictionary representing the loaded configuration.
        """
        import yaml

        with open(filepath, "r") as file:
            return yaml.safe_load(file)

    def _load_toml(self, filepath: Path) -> Dict[str, Any]:
        """
        Load a TOML configuration file.

        Args:
            filepath: The TOML file path.

        Returns:
            A dictionary representing the loaded configuration.
        """
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                raise ImportError(
                    "TOML parsing requires either the `tomllib` library (Python 3.11+) or the `tomli` package. "
                    "Please install `tomli` with `pip install tomli` for Python versions below 3.11."
                )

        with open(filepath, "rb") as file:
            return tomllib.load(file)

    @classmethod
    def parse_secrets(
        cls,
        configs: Dict[str, Any],
        secrets_filepath: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """
        Parse secrets from the secrets file and replace placeholders in configurations.

        Args:
            configs: The configurations to parse for secrets placeholders.
            secrets_filepath: The path to the secrets file.

        Returns:
            The configurations with secrets resolved.
        """
        secrets = load_secrets(filepath=secrets_filepath)
        return parse_secrets(configs, secrets)
