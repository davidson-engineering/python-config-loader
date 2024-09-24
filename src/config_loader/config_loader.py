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

logger = logging.getLogger(__name__)


class DuplicateConfigKeyError(Exception):
    """
    Raised when multiple configuration files have the same stem.
    """

    pass


def load_configs(
    filepaths: Union[str, Path, List[Union[str, Path]]],
    default_directory: Union[str, Path, None] = None,
) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    """
    Load and merge configurations for the filepaths.
    If only one filepath is passed, return the merged config for that file.
    If multiple filepaths are passed, return a dictionary with file stems as keys and merged configs as values.
    Raise an error if multiple filepaths have the same stem.
    """
    loader = ConfigLoader(filepaths, default_directory)
    return loader.load()


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

        # If no default_directory is provided, use the default directory for defaults
        self.default_directory = (
            Path(default_directory) if default_directory else Path("config/default")
        )

    def load(self) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """
        Load and merge configurations for the filepaths.
        If only one filepath is passed, return the merged config for that file.
        If multiple filepaths are passed, return a dictionary with file stems as keys and merged configs as values.
        Raise an error if multiple filepaths have the same stem.
        """
        configs = {}
        # Check if all filepaths exist and raise an error if not
        for filepath in self.filepaths:
            default_filepath = self._get_default_filepath(filepath)
            if not filepath.exists() and not default_filepath.exists():
                raise FileNotFoundError(
                    f"File not found: {filepath}, also no defaults found in {self.default_directory}"
                )
            if not filepath.exists() and default_filepath.exists():
                logger.warning(
                    f"File not found: {filepath}, but using defaults from {default_filepath}"
                )
            stem = filepath.stem
            if stem in configs:
                raise DuplicateConfigKeyError(
                    f"Duplicate configuration key detected: '{stem}' from file '{filepath}' conflicts with an existing file."
                )

            # Load the default configuration if it exists
            default_config = self._load_defaults(filepath)
            # Load the main configuration file
            user_config = self._load_file(filepath)
            # Merge the two configurations (default and main)
            merged_config = self._merge_configs(default_config, user_config)
            # Store the merged config with the filename stem (as a string) as the key
            configs[stem] = merged_config

        # Return single config if only one filepath was provided
        if len(self.filepaths) == 1:
            return configs[self.filepaths[0].stem]

        return configs

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
        return self.default_directory / Path(
            f"{filepath.stem}-default{filepath.suffix}"
        )

    def _load_defaults(self, filepath: Path) -> dict:
        # If the default configuration file has the same extension as the main configuration file, load it
        # If the default configuration file does not exists, then walk directory for a default configuration file with a different extension in default directory
        # If found, warn the user and load it
        default_path = self._get_default_filepath(filepath)
        if default_path.suffix == filepath.suffix and default_path.exists():
            return self._load_file(default_path)
        elif not default_path.exists():
            for file in self.default_directory.iterdir():
                if (
                    file.stem == filepath.stem + "-default"
                    and file.suffix != filepath.suffix
                ):
                    logger.warning(
                        f"Default configuration file with different extension found: {file}. Loading this file instead."
                    )
                    return self._load_file(file)
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
