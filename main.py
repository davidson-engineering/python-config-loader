#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2024-01-01
# ---------------------------------------------------------------------------
"""Example usage of the config_loader package."""
# ---------------------------------------------------------------------------


from config_loader.config_loader import load_configs


def main():

    # Configuration file
    # 'test': {'user': '${USER}', 'password': '${PASSWORD}'}
    config_filepath = "config/app-config.toml"
    # Optional secrets file
    # {'USER=some_user', 'PASSWORD=super_secret_password'}
    secrets_filepath = "example.env"

    # Load the configuration file
    config = load_configs(
        filepaths=[config_filepath], secrets_filepath=secrets_filepath
    )

    print(config)
    # >>> {'defaults': {'foo': 'bar'}, 'test': {'user': 'some_user', 'password': 'super_secret_password'}}

    # Note that defaults inside `default/{config_filepath}-default.toml` will be included if it exists, even if not specified in the `config_filepath`
    # To prevent this, specify the load_defaults=False parameter
    config = load_configs(
        filepaths=[config_filepath],
        secrets_filepath=secrets_filepath,
        load_defaults=False,
    )

    print(config)
    # >>> {'test': {'user': 'some_user', 'password': 'super_secret_password'}}
    # Note that the defaults are no longer included


if __name__ == "__main__":
    main()
