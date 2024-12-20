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
from typing import Union, List, Dict, Any
import logging

from .secrets_loader import load_secrets, parse_secrets

logger = logging.getLogger(__name__)


class DuplicateConfigKeyError(Exception):
    """
    Raised when multiple configuration files have the same stem.
    """

    pass


def load_configs(
    filepaths: Union[str, Path, List[Union[str, Path]]],
    default_directory: Union[str, Path, None] = None,
    secrets_filepath: Union[str, Path, None] = None,
) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    """
    Load and merge configurations for the filepaths.
    If only one filepath is passed, return the merged config for that file.
    If multiple filepaths are passed, return a dictionary with file stems as keys and merged configs as values.
    Raise an error if multiple filepaths have the same stem.
    """
    loader = ConfigLoader(filepaths, default_directory)
    configs = loader.load()
    loader.parse_secrets(configs, secrets_filepath)
    return configs


class ConfigLoader:
    """
    A class to load and merge configuration files from multiple formats, with support for default configurations.
    """

    def __init__(
        self,
        filepaths: Union[str, Path, List[Union[str, Path]]],
        default_directory: Union[str, Path, None] = None,
    ):
        """
        Initialize with a list of file paths or a single file path.
        An optional default path to a directory can be provided. If not, defaults to 'config/default/'.
        """
        if isinstance(filepaths, (str, Path)):
            self.filepaths = [Path(filepaths)]
        else:
            self.filepaths = [
                Path(filepath) if isinstance(filepath, str) else filepath
                for filepath in filepaths
            ]
        # If no default_directory is provided, use the default directory for defaults if it exists
        # Otherwise, set it to None
        if default_directory:
            self.default_directory = Path(default_directory)
        elif Path("config/default").exists():
            self.default_directory = Path("config/default")
        else:
            self.default_directory = None

    def load(self) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """
        Load and merge configurations for the filepaths.
        If only one filepath is passed, return the merged config for that file.
        If multiple filepaths are passed, return a dictionary with file stems as keys and merged configs as values.
        Raise an error if multiple filepaths have the same stem.
        """
        configs = {}

        for filepath in self.filepaths:
            stem = filepath.stem

            # Ensure no duplicate stems across filepaths
            if stem in configs:
                raise DuplicateConfigKeyError(
                    f"Duplicate configuration key detected: '{stem}' from file '{filepath}' conflicts with an existing file."
                )

            # Check if the file or its default exists, and log appropriately
            default_filepath = self._get_default_filepath(filepath)
            if not filepath.exists():
                if not default_filepath or not default_filepath.exists():
                    raise FileNotFoundError(
                        f"File not found: {filepath}. No default found in {self.default_directory}."
                    )
                logger.warning(
                    f"File not found: {filepath}. Using default from {default_filepath}."
                )

            # Load configurations (default and user) and merge them
            default_config = self._load_defaults(filepath)
            user_config = self._load_file(filepath) if filepath.exists() else {}
            configs[stem] = self._merge_configs(default_config, user_config)

        # Return single config if only one filepath was provided
        return configs[self.filepaths[0].stem] if len(self.filepaths) == 1 else configs

    def _load_file(self, filepath: Path) -> dict:
        """
        Load a single configuration file based on the file extension.
        Returns an empty dictionary if the file does not exist.
        """
        if not filepath.exists():
            return {}
        file_extension = filepath.suffix
        if file_extension == ".json":
            return self._load_json(filepath)
        elif file_extension == ".yaml":
            return self._load_yaml(filepath)
        elif file_extension == ".toml":
            return self._load_toml(filepath)
        else:
            return {}

    def _get_default_filepath(self, filepath: Path) -> dict:
        """
        Load the corresponding default configuration file if it exists.
        If a default_directory was provided at initialization, use that. Otherwise, look in 'config/default/'.
        """
        if self.default_directory is None:
            return None
        return self.default_directory / Path(
            f"{filepath.stem}-default{filepath.suffix}"
        )

    def _load_defaults(self, filepath: Path) -> dict:
        # Determine the default configuration file path
        default_path = self._get_default_filepath(filepath)

        if not default_path:
            return {}

        # If the default file exists and matches the main file's extension, load it
        if (
            default_path
            and default_path.suffix == filepath.suffix
            and default_path.exists()
        ):
            return self._load_file(default_path)

        # Search for an alternative default file with a different extension
        for file in self.default_directory.iterdir():
            if (
                file.stem == f"{filepath.stem}-default"
                and file.suffix != filepath.suffix
            ):
                logger.warning(f"Loading default file with different extension: {file}")
                return self._load_file(file)

        # Return an empty dictionary if no suitable file is found
        return {}

    def _merge_configs(self, base_config: dict, new_config: dict) -> dict:
        """
        Recursively merge two dictionaries. Values from new_config overwrite base_config.
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

    def _load_json(self, filepath: Path) -> dict:
        """
        Load JSON configuration file.
        """
        import json

        with open(filepath, "r") as file:
            return json.load(file)

    def _load_yaml(self, filepath: Path) -> dict:
        """
        Load YAML configuration file.
        """
        import yaml

        with open(filepath, "r") as file:
            return yaml.safe_load(file)

    def _load_toml(self, filepath: Path) -> dict:
        """
        Load TOML configuration file.
        """
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib  # Fallback for older versions
        with open(filepath, "rb") as file:
            return tomllib.load(file)

    @classmethod
    def parse_secrets(cls, configs: dict[str, str], secrets_filepath=None) -> dict:
        """
        Parse secrets with environment variables.
        """
        # Load environment variables from secrets file
        load_secrets(filepath=secrets_filepath)
        # Replace environment variables in the configs
        return parse_secrets(configs)
