# python-config-loader
## A module to load user configuration files from multiple formats, with support for default configurations.

The `ConfigLoader` class is designed to handle configurations in multiple file formats (JSON, YAML, TOML). It allows you to merge configuration files, and optionally, you can provide a default configuration for each file.

## Installation

```
pip install -r requirements.txt
```

## Usage
### Basic Usage with a Single Configuration File

To load and merge a single configuration file with its corresponding default configuration (if it exists in the `config/default/` directory):

```python

from config_loader import ConfigLoader

config1_filepath = "config/config1.toml"
config_loader = ConfigLoader(config1_filepath)
config1 = config_loader.load()
print(config1)  # Returns the merged configuration for config1.toml
```

### Loading Multiple Configuration Files

You can load and merge multiple configuration files at once. Each configuration will be merged with its corresponding default configuration (if it exists):

```python

from config_loader import ConfigLoader

config1_filepath = "config/config1.toml"
config2_filepath = "config/config2.toml"
config_loader = ConfigLoader([config1_filepath, config2_filepath])
configs = config_loader.load()

config1 = configs["config1"]  # Access merged configuration for config1.toml
config2 = configs["config2"]  # Access merged configuration for config2.toml
```
### Loading via function
One can load configurations simply by calling a helper function
```python
from config_loader import load_configs
config_filepaths = ["config/config1.toml", "config/config2.toml"]
configs = load_configs(config_filepaths)
print(configs["config1"])
print(configs["config2"])
```

### Providing a Custom Default File

If you want to provide a custom default configuration file (instead of using the default directory `config/default/`), you can pass it to the `ConfigLoader`:

```python
from config_loader import ConfigLoader

config1_filepath = "config/config1.yaml"
default_filepath = "custom/default/global-default.yaml"
config_loader = ConfigLoader(config1_filepath, default_filepath=default_filepath)
config = config_loader.load()
print(config)  # Merged configuration with global-default.yaml
```

### Preventing Key Conflicts

If two configuration files have the same stem (e.g., `config1.yaml` and `config1.json`), the loader will raise an error to prevent key conflicts:

```python
from config_loader import ConfigLoader

config1_filepath = "config/config1.yaml"
config2_filepath = "config/config1.json"  # Conflict due to same stem as config1.yaml
config_loader = ConfigLoader([config1_filepath, config2_filepath])  # Raises ValueError
```

### Supported Formats

The `ConfigLoader` currently supports the following file formats:

    JSON (.json)
    YAML (.yaml, .yml)
    TOML (.toml)

### Default Configurations

The `ConfigLoader` will automatically look for a corresponding default configuration file in the `config/default/` directory if no custom default is provided. The default config file is expected to follow the naming pattern `{file_stem}-default.{file_extension}`.

For example:

- If loading `config1.yaml`, the loader will check for `config/default/config1-default.yaml`.

## Testing

You can run the tests using pytest:

```console
pytest tests/
```

### Example test structures:
#### YAML
```yaml
name: "Example"
version: 1.0
settings:
  debug: true
  max_connections: 10
  threshold: 0.85
```
#### TOML
```toml
name = "Example"
version = 1.0
[settings]
debug = true
max_connections = 10
threshold = 0.85
```
#### JSON
```json
{
  "name": "Example",
  "version": 1.0,
  "settings": {
    "debug": true,
    "max_connections": 10,
    "threshold": 0.85
  }
}
```
