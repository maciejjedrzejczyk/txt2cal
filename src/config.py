"""Configuration data models and loader for Calendar Event Converter.

This module handles loading and managing application configuration from YAML files.
It provides sensible defaults for all settings and supports configuration override
through the config.yaml file.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class LLMConfig:
    """Configuration for LLM server connection.
    
    Attributes:
        api_base: Base URL for the LLM API endpoint (e.g., "http://localhost:1234/v1")
        model: Name of the LLM model to use (e.g., "ibm/granite-4-h-tiny")
        api_key: API key for authentication (default: "not-needed" for LM Studio)
        timeout: Request timeout in seconds (default: 30)
    
    Example:
        >>> config = LLMConfig(
        ...     api_base="http://localhost:1234/v1",
        ...     model="ibm/granite-4-h-tiny"
        ... )
    """
    api_base: str
    model: str
    api_key: str = "not-needed"
    timeout: int = 30


@dataclass
class ServerConfig:
    """Configuration for the application server.
    
    Attributes:
        host: Host address to bind the server to (default: "0.0.0.0")
        port: Port number to listen on (default: 8000)
    
    Example:
        >>> config = ServerConfig(host="0.0.0.0", port=8000)
    """
    host: str
    port: int


@dataclass
class LimitsConfig:
    """Configuration for resource limits.
    
    Attributes:
        max_file_size_mb: Maximum file upload size in megabytes (default: 10)
        max_text_length: Maximum text input length in characters (default: 50000)
    
    Example:
        >>> config = LimitsConfig(max_file_size_mb=10, max_text_length=50000)
    """
    max_file_size_mb: int
    max_text_length: int


@dataclass
class AppConfig:
    """Complete application configuration.
    
    This is the top-level configuration object that contains all configuration
    sections (LLM, server, and limits).
    
    Attributes:
        llm: LLM server configuration
        server: Application server configuration
        limits: Resource limits configuration
    
    Example:
        >>> config = load_config(Path("config/config.yaml"))
        >>> print(config.llm.model)
        'ibm/granite-4-h-tiny'
    """
    llm: LLMConfig
    server: ServerConfig
    limits: LimitsConfig


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """Load configuration from YAML file with defaults.
    
    This function loads configuration from a YAML file and merges it with
    sensible defaults. If the config file doesn't exist, it returns the
    default configuration.
    
    Default configuration:
    - LLM: LM Studio at http://host.docker.internal:1234/v1 with ibm/granite-4-h-tiny
    - Server: 0.0.0.0:8000
    - Limits: 10MB max file size, 50000 character max text length
    
    Args:
        config_path: Path to config.yaml file. If None, uses "config/config.yaml"
        
    Returns:
        AppConfig with loaded or default values
        
    Raises:
        yaml.YAMLError: If config file exists but is invalid YAML
    
    Example:
        >>> config = load_config()  # Uses default path
        >>> config = load_config(Path("/custom/path/config.yaml"))  # Custom path
    """
    if config_path is None:
        config_path = Path("config/config.yaml")
    
    # Default configuration (LM Studio defaults)
    default_config = {
        "llm": {
            "api_base": "http://host.docker.internal:1234/v1",
            "model": "ibm/granite-4-h-tiny",
            "api_key": "not-needed",
            "timeout": 30
        },
        "server": {
            "host": "0.0.0.0",
            "port": 8000
        },
        "limits": {
            "max_file_size_mb": 10,
            "max_text_length": 50000
        }
    }
    
    # Load from file if it exists
    if config_path.exists():
        with open(config_path, 'r') as f:
            file_config = yaml.safe_load(f) or {}
        
        # Merge file config with defaults (file config takes precedence)
        merged_config = _deep_merge(default_config, file_config)
    else:
        merged_config = default_config
    
    # Build configuration objects
    llm_config = LLMConfig(**merged_config["llm"])
    server_config = ServerConfig(**merged_config["server"])
    limits_config = LimitsConfig(**merged_config["limits"])
    
    return AppConfig(
        llm=llm_config,
        server=server_config,
        limits=limits_config
    )


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries, with override taking precedence.
    
    This function recursively merges two dictionaries. For nested dictionaries,
    it performs a deep merge rather than replacing the entire nested dict.
    
    Args:
        base: Base dictionary with default values
        override: Dictionary with override values
        
    Returns:
        Merged dictionary with override values taking precedence
    
    Example:
        >>> base = {"a": {"b": 1, "c": 2}, "d": 3}
        >>> override = {"a": {"b": 10}, "e": 4}
        >>> _deep_merge(base, override)
        {'a': {'b': 10, 'c': 2}, 'd': 3, 'e': 4}
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result
