import yaml
import os
from pathlib import Path
from config.schemas import (
    SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig, BugHunterConfig
)

def load_config(config_dir: str | Path) -> BugHunterConfig:
    config_path = Path(config_dir)
    
    with open(config_path / "defaults" / "settings.yaml", "r", encoding="utf-8") as f:
        settings_data = yaml.safe_load(f) or {}
        
    with open(config_path / "defaults" / "llm.yaml", "r", encoding="utf-8") as f:
        llm_data = yaml.safe_load(f) or {}
        
    with open(config_path / "defaults" / "tools.yaml", "r", encoding="utf-8") as f:
        tools_data = yaml.safe_load(f) or {}
        
    with open(config_path / "defaults" / "timeouts.yaml", "r", encoding="utf-8") as f:
        timeouts_data = yaml.safe_load(f) or {}
        
    with open(config_path / "defaults" / "reporting.yaml", "r", encoding="utf-8") as f:
        reporting_data = yaml.safe_load(f) or {}
        
    # Environment variable overrides for API Keys
    if "OPENAI_API_KEY" in os.environ:
        llm_data["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]
    if "GOOGLE_API_KEY" in os.environ:
        llm_data["GOOGLE_API_KEY"] = os.environ["GOOGLE_API_KEY"]
    if "ANTHROPIC_API_KEY" in os.environ:
        llm_data["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_API_KEY"]

    return BugHunterConfig(
        settings=SettingsConfig(**settings_data),
        llm=LLMConfig(**llm_data),
        tools=ToolsConfig(**tools_data),
        timeouts=TimeoutsConfig(**timeouts_data),
        reporting=ReportingConfig(**reporting_data)
    )
