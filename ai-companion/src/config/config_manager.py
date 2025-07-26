"""
Configuration management for AI Companion.
Handles YAML/JSON configuration files, environment variables, and runtime updates.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30


class ElevenLabsConfig(BaseModel):
    """Eleven Labs voice configuration."""
    api_key: Optional[str] = None
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice
    model_id: str = "eleven_monolingual_v1"
    stability: float = 0.75
    similarity_boost: float = 0.75


class MemoryConfig(BaseModel):
    """Memory system configuration."""
    max_memories: int = 10000
    consolidation_threshold: int = 5
    importance_decay_rate: float = 0.1
    abridgment_min_length: int = 100
    backup_interval_hours: int = 24


class BehaviorTreeConfig(BaseModel):
    """Behavior tree configuration."""
    max_states: int = 100
    state_timeout_seconds: int = 300
    modification_cooldown_seconds: int = 60
    backup_before_modification: bool = True


class SecurityConfig(BaseModel):
    """Security and privacy configuration."""
    encrypt_memories: bool = True
    tool_sandbox_enabled: bool = True
    max_tool_execution_time: int = 30
    audit_logging: bool = True


class UIConfig(BaseModel):
    """User interface configuration."""
    theme: str = "dark"
    auto_minimize_to_tray: bool = True
    show_debug_console: bool = False
    voice_activation_enabled: bool = True
    chat_history_limit: int = 1000


class CompanionConfig(BaseSettings):
    """Main configuration class for AI Companion."""
    
    # Core settings
    debug: bool = False
    log_level: str = "INFO"
    data_directory: str = "./data"
    
    # Component configurations
    llm: LLMConfig = Field(default_factory=LLMConfig)
    elevenlabs: ElevenLabsConfig = Field(default_factory=ElevenLabsConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    behavior_tree: BehaviorTreeConfig = Field(default_factory=BehaviorTreeConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    
    # Server settings
    host: str = "localhost"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


class ConfigManager:
    """Manages configuration loading, validation, and runtime updates."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path or "config/config.yaml")
        self.config: Optional[CompanionConfig] = None
        self._watchers = []
    
    def load_config(self) -> CompanionConfig:
        """Load configuration from file and environment variables."""
        config_data = {}
        
        # Load from YAML file if it exists
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        
        # Create config with data, allowing env var overrides
        self.config = CompanionConfig(**config_data)
        return self.config
    
    def save_config(self, config: Optional[CompanionConfig] = None) -> None:
        """Save configuration to file."""
        config_to_save = config or self.config
        if not config_to_save:
            raise ValueError("No configuration to save")
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and save as YAML
        config_dict = config_to_save.model_dump()
        with open(self.config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def update_config(self, updates: Dict[str, Any]) -> CompanionConfig:
        """Update configuration at runtime."""
        if not self.config:
            self.load_config()
        
        # Create new config with updates
        config_dict = self.config.model_dump()
        self._deep_update(config_dict, updates)
        
        # Validate new config
        new_config = CompanionConfig(**config_dict)
        self.config = new_config
        
        # Notify watchers
        for watcher in self._watchers:
            watcher(new_config)
        
        return new_config
    
    def add_config_watcher(self, callback):
        """Add a callback to be notified of config changes."""
        self._watchers.append(callback)
    
    def remove_config_watcher(self, callback):
        """Remove a config change watcher."""
        if callback in self._watchers:
            self._watchers.remove(callback)
    
    def validate_config(self, config: Optional[CompanionConfig] = None) -> bool:
        """Validate configuration."""
        config_to_validate = config or self.config
        if not config_to_validate:
            return False
        
        try:
            # Pydantic validation happens automatically
            # Additional custom validations can be added here
            
            # Check if required directories exist or can be created
            data_dir = Path(config_to_validate.data_directory)
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Validate API keys if needed
            if config_to_validate.llm.provider == "openai" and not config_to_validate.llm.api_key:
                if not os.getenv("OPENAI_API_KEY"):
                    print("Warning: OpenAI API key not configured")
            
            if config_to_validate.elevenlabs.api_key is None:
                if not os.getenv("ELEVENLABS_API_KEY"):
                    print("Warning: Eleven Labs API key not configured")
            
            return True
            
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    @staticmethod
    def _deep_update(base_dict: Dict, update_dict: Dict) -> None:
        """Deep update dictionary."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                ConfigManager._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


# Global config manager instance
config_manager = ConfigManager()


def get_config() -> CompanionConfig:
    """Get the current configuration."""
    if config_manager.config is None:
        config_manager.load_config()
    return config_manager.config


def update_config(updates: Dict[str, Any]) -> CompanionConfig:
    """Update configuration at runtime."""
    return config_manager.update_config(updates)
