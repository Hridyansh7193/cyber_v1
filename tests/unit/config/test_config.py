import pytest
from pathlib import Path
from pydantic import ValidationError

from config.loader import load_config

CONFIG_DIR = Path("config")

def test_load_config_success():
    cfg = load_config(CONFIG_DIR)
    
    # Assert top-level fields
    assert cfg.settings is not None
    assert cfg.llm is not None
    assert cfg.tools is not None
    assert cfg.timeouts is not None
    assert cfg.reporting is not None
    
    # Assert values loaded from defaults
    assert cfg.settings.scan_depth == 1
    assert cfg.llm.provider == "openai"
    assert "subfinder" in cfg.tools.tool_paths
    assert cfg.timeouts.global_timeout == 3600
    assert "json" in cfg.reporting.report_formats

def test_env_var_override(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    cfg = load_config(CONFIG_DIR)
    assert cfg.llm.OPENAI_API_KEY == "test-key-123"
    
def test_multiple_env_vars(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    cfg = load_config(CONFIG_DIR)
    assert cfg.llm.GOOGLE_API_KEY == "google-key"
    assert cfg.llm.ANTHROPIC_API_KEY == "anthropic-key"
    assert cfg.llm.OPENAI_API_KEY is None

def test_invalid_yaml_raises_validation_error(tmp_path):
    # Setup mock config dir
    defaults_dir = tmp_path / "defaults"
    defaults_dir.mkdir()
    
    # Write invalid setting type (string instead of int for scan_depth)
    (defaults_dir / "settings.yaml").write_text("scan_depth: 'invalid'\nmax_concurrency: 10\nlog_level: 'INFO'")
    (defaults_dir / "llm.yaml").write_text("provider: 'openai'\ndefault_model: 'gpt-4o'\ntimeout: 30")
    (defaults_dir / "tools.yaml").write_text("tool_paths: {}\ndocker_container_names: {}\nenable_flags: {}\nwordlists: {}")
    (defaults_dir / "timeouts.yaml").write_text("subfinder_timeout: 300\nnuclei_timeout: 600\ndalfox_timeout: 600\nffuf_timeout: 600\nglobal_timeout: 3600")
    (defaults_dir / "reporting.yaml").write_text("report_formats: []\noutput_directories: {}")

    with pytest.raises(ValidationError):
        load_config(tmp_path)

def test_missing_required_fields(tmp_path):
    defaults_dir = tmp_path / "defaults"
    defaults_dir.mkdir()
    
    # Missing default_model which is required in LLMConfig
    (defaults_dir / "settings.yaml").write_text("scan_depth: 1\nmax_concurrency: 10\nlog_level: 'INFO'")
    (defaults_dir / "llm.yaml").write_text("provider: 'openai'\ntimeout: 30")
    (defaults_dir / "tools.yaml").write_text("tool_paths: {}\ndocker_container_names: {}\nenable_flags: {}\nwordlists: {}")
    (defaults_dir / "timeouts.yaml").write_text("subfinder_timeout: 300\nnuclei_timeout: 600\ndalfox_timeout: 600\nffuf_timeout: 600\nglobal_timeout: 3600")
    (defaults_dir / "reporting.yaml").write_text("report_formats: []\noutput_directories: {}")

    with pytest.raises(ValidationError):
        load_config(tmp_path)

def test_stateless_and_isolated():
    cfg1 = load_config(CONFIG_DIR)
    cfg2 = load_config(CONFIG_DIR)
    
    assert cfg1 is not cfg2
    assert cfg1.settings is not cfg2.settings
    assert cfg1.llm is not cfg2.llm

def test_immutability():
    cfg = load_config(CONFIG_DIR)
    
    with pytest.raises(ValidationError) as exc_info:
        cfg.settings.scan_depth = 99
        
    assert "Instance is frozen" in str(exc_info.value)
    
    with pytest.raises(ValidationError):
        cfg.llm.provider = "anthropic"

def test_pathlib_support():
    # Verify pathlib.Path works natively as the config_dir argument
    path = Path("config")
    cfg = load_config(path)
    assert cfg is not None
