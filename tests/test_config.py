"""Unit tests for configuration management."""

import pytest
from pathlib import Path
import tempfile
import yaml

from src.config import (
    LLMConfig,
    ServerConfig,
    LimitsConfig,
    AppConfig,
    load_config,
    _deep_merge
)


class TestConfigDataModels:
    """Test configuration data model creation."""
    
    def test_llm_config_creation(self):
        """Test LLMConfig can be created with required fields."""
        config = LLMConfig(
            api_base="http://localhost:1234/v1",
            model="test-model"
        )
        assert config.api_base == "http://localhost:1234/v1"
        assert config.model == "test-model"
        assert config.api_key == "not-needed"
        assert config.timeout == 30
    
    def test_server_config_creation(self):
        """Test ServerConfig can be created."""
        config = ServerConfig(host="0.0.0.0", port=8000)
        assert config.host == "0.0.0.0"
        assert config.port == 8000
    
    def test_limits_config_creation(self):
        """Test LimitsConfig can be created."""
        config = LimitsConfig(max_file_size_mb=10, max_text_length=50000)
        assert config.max_file_size_mb == 10
        assert config.max_text_length == 50000


class TestConfigLoader:
    """Test configuration loading functionality."""
    
    def test_load_default_configuration(self):
        """Test loading default configuration when file doesn't exist."""
        # Requirements: 7.2, 7.3
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.yaml"
            config = load_config(config_path)
            
            # Verify LM Studio defaults
            assert config.llm.api_base == "http://host.docker.internal:1234/v1"
            assert config.llm.model == "ibm/granite-4-h-tiny"
            assert config.llm.api_key == "not-needed"
            assert config.llm.timeout == 30
            
            # Verify server defaults
            assert config.server.host == "0.0.0.0"
            assert config.server.port == 8000
            
            # Verify limits defaults
            assert config.limits.max_file_size_mb == 10
            assert config.limits.max_text_length == 50000
    
    def test_load_custom_configuration(self):
        """Test loading custom configuration from file."""
        # Requirements: 7.2, 7.3
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "custom.yaml"
            
            # Create custom config file
            custom_config = {
                "llm": {
                    "api_base": "http://custom-server:5000/v1",
                    "model": "custom-model",
                    "api_key": "custom-key",
                    "timeout": 60
                },
                "server": {
                    "host": "127.0.0.1",
                    "port": 9000
                },
                "limits": {
                    "max_file_size_mb": 20,
                    "max_text_length": 100000
                }
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(custom_config, f)
            
            config = load_config(config_path)
            
            # Verify custom values are loaded
            assert config.llm.api_base == "http://custom-server:5000/v1"
            assert config.llm.model == "custom-model"
            assert config.llm.api_key == "custom-key"
            assert config.llm.timeout == 60
            
            assert config.server.host == "127.0.0.1"
            assert config.server.port == 9000
            
            assert config.limits.max_file_size_mb == 20
            assert config.limits.max_text_length == 100000
    
    def test_partial_configuration_override(self):
        """Test that partial config overrides defaults correctly."""
        # Requirements: 7.3
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "partial.yaml"
            
            # Only override LLM model, keep other defaults
            partial_config = {
                "llm": {
                    "model": "different-model"
                }
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(partial_config, f)
            
            config = load_config(config_path)
            
            # Verify override
            assert config.llm.model == "different-model"
            
            # Verify defaults are preserved
            assert config.llm.api_base == "http://host.docker.internal:1234/v1"
            assert config.llm.api_key == "not-needed"
            assert config.server.host == "0.0.0.0"
            assert config.server.port == 8000


class TestDeepMerge:
    """Test the deep merge utility function."""
    
    def test_deep_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        base = {
            "a": {"x": 1, "y": 2},
            "b": 3
        }
        override = {
            "a": {"y": 99},
            "c": 4
        }
        
        result = _deep_merge(base, override)
        
        assert result["a"]["x"] == 1  # Preserved from base
        assert result["a"]["y"] == 99  # Overridden
        assert result["b"] == 3  # Preserved from base
        assert result["c"] == 4  # Added from override
    
    def test_deep_merge_complete_override(self):
        """Test that non-dict values are completely replaced."""
        base = {"a": 1, "b": {"x": 2}}
        override = {"a": 100, "b": {"x": 200, "y": 300}}
        
        result = _deep_merge(base, override)
        
        assert result["a"] == 100
        assert result["b"]["x"] == 200
        assert result["b"]["y"] == 300



class TestConfigurationOverrideProperty:
    """Property-based tests for configuration override behavior."""
    
    @pytest.mark.parametrize("_", range(100))
    def test_configuration_override_property(self, _):
        """
        Property 13: Configuration Override
        
        For any custom LLM configuration provided (API base URL, model name, API key),
        the system should use those values instead of defaults when communicating
        with the LLM server.
        
        Feature: calendar-event-converter, Property 13: Configuration Override
        Validates: Requirements 7.5
        """
        from hypothesis import given, strategies as st
        
        @given(
            api_base=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            model=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            api_key=st.text(min_size=0, max_size=100),
            timeout=st.integers(min_value=1, max_value=300)
        )
        def property_test(api_base, model, api_key, timeout):
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = Path(tmpdir) / "override.yaml"
                
                # Create config with custom LLM settings
                custom_config = {
                    "llm": {
                        "api_base": api_base,
                        "model": model,
                        "api_key": api_key,
                        "timeout": timeout
                    }
                }
                
                with open(config_path, 'w') as f:
                    yaml.dump(custom_config, f)
                
                # Load configuration
                config = load_config(config_path)
                
                # Verify custom values are used instead of defaults
                assert config.llm.api_base == api_base, \
                    f"Expected api_base={api_base}, got {config.llm.api_base}"
                assert config.llm.model == model, \
                    f"Expected model={model}, got {config.llm.model}"
                assert config.llm.api_key == api_key, \
                    f"Expected api_key={api_key}, got {config.llm.api_key}"
                assert config.llm.timeout == timeout, \
                    f"Expected timeout={timeout}, got {config.llm.timeout}"
                
                # Verify other sections still have defaults
                assert config.server.host == "0.0.0.0"
                assert config.server.port == 8000
                assert config.limits.max_file_size_mb == 10
                assert config.limits.max_text_length == 50000
        
        property_test()
