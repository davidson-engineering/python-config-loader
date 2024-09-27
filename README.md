# python-config-loader
## A module to load user configuration files from multiple formats, with support for default configurations.

The `ConfigLoader` class is designed to handle configurations in multiple file formats (JSON, YAML, TOML). It allows you to merge configuration files, and optionally, you can provide a default configuration for each file.

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
### Loading Via function
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
default_filepath = "custom/default/"
config_loader = ConfigLoader(config1_filepath, default_filepath=default_filepath)
config = config_loader.load()
print(config)  # Merged configuration with 'custom/default/config1-default.yaml'
```

### Preventing Key Conflicts

If two configuration files have the same stem (e.g., `config1.yaml` and `config1.json`), the loader will raise an error to prevent key conflicts:

```python
from config_loader import ConfigLoader

config1_filepath = "config/config1.yaml"
config2_filepath = "config/config1.json"  # Conflict due to same stem as config1.yaml
config_loader = ConfigLoader([config1_filepath, config2_filepath])  # Raises DuplicateConfigKeyError
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

### Secrets Parsing in Configurations

In addition to loading and merging configurations, the `ConfigLoader` supports parsing environment variables from configuration files. This is particularly useful when you want to keep sensitive information, such as API keys or database credentials, outside of your configuration files and load them dynamically from environment variables.

The `parse_secrets` method is designed to scan your configuration for placeholders in the format `${VAR_NAME}` and replace them with the values of corresponding environment variables. You can also load secrets from an external file (e.g., .env file), allowing you to securely manage sensitive data.

### Example Configuration with Secrets

Here’s an example of a configuration file (config/config1.yaml) with placeholders for environment variables:

```yaml

database:
  username: "user123"
  password: "${DB_PASSWORD}"  # This will be replaced by the value of the DB_PASSWORD environment variable
  host: "localhost"
apikey: "${API_KEY}"  # This will be replaced by the value of the API_KEY environment variable
```

### Setting Up Environment Variables

You can set the required environment variables before running the code:

```bash
export DB_PASSWORD="mysecretpassword"
export API_KEY="abcd1234"
```

Alternatively, you can load these variables from a secrets file:

```bash
DB_PASSWORD=mysecretpassword
API_KEY=abcd1234
```
### Loading Configuration with Secrets Parsing

To load the configuration file and replace the environment variables, use the load_configs function and pass the secrets_filepath parameter:

```python
from config_loader import load_configs

config_filepath = "config/config1.yaml"
secrets_filepath = "path/to/secrets.env"  # Optional, if you want to load secrets from a file

configs = load_configs(config_filepath, secrets_filepath=secrets_filepath)
print(configs)
```
### Expected Output

If the environment variables are set or loaded from the secrets file, the placeholders in the configuration will be replaced with their values:

```python

{
    "database": {
        "username": "user123",
        "password": "mysecretpassword",  # Replaced from environment
        "host": "localhost"
    },
    "apikey": "abcd1234"  # Replaced from environment
}
```