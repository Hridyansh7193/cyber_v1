import pytest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone

from storage.database import override_db

@pytest.fixture(scope="session")
def fixtures_dir():
    return Path(__file__).parent.parent / "fixtures"

@pytest.fixture
def mock_subprocess_run(fixtures_dir):
    def side_effect(command, tool_name, cwd=None, timeout=None):
        # Determine the tool from the command
        cmd_str = " ".join(command)
        stdout_data = ""
        
        if "subfinder" in cmd_str:
            stdout_data = (fixtures_dir / "subfinder.txt").read_text(encoding="utf-8")
        elif "httpx" in cmd_str:
            stdout_data = (fixtures_dir / "httpx.json").read_text(encoding="utf-8")
        elif "katana" in cmd_str:
            stdout_data = (fixtures_dir / "katana.json").read_text(encoding="utf-8")
        elif "nuclei" in cmd_str:
            stdout_data = (fixtures_dir / "nuclei.json").read_text(encoding="utf-8")
        
        # Return a mock ProcessResult
        from execution.utils.process_runner import ProcessResult
        return ProcessResult(exit_code=0, stdout=stdout_data, stderr="", execution_time=1.0)

    with patch("execution.utils.process_runner.ProcessRunner.run", side_effect=side_effect) as m:
        yield m

@pytest.fixture
def e2e_db(tmp_path):
    db_path = tmp_path / "e2e_bughunter.db"
    db_url = f"sqlite:///{db_path}"
    override_db(db_url)
    
    import storage.models as models
    from storage.database import get_engine
    
    # Create tables
    engine = get_engine()
    models.Base.metadata.create_all(engine)
    
    yield db_url
    
    models.Base.metadata.drop_all(engine)

@pytest.fixture
def base_config(tmp_path):
    from config.loader import load_config
    config_dir = Path(__file__).parent.parent.parent / "config"
    config = load_config(config_dir)
    
    from config.schemas import ReportingConfig
    # Update reporting to use tmp_path
    new_reporting = ReportingConfig(
        report_formats=["markdown", "json"],
        output_directories={
            "markdown": str(tmp_path / "reports/markdown"),
            "json": str(tmp_path / "reports/json")
        }
    )
    
    return config.model_copy(update={"reporting": new_reporting})

@pytest.fixture
def deterministic_target():
    from schemas.target import TargetState
    return TargetState(
        domain="example.com",
        scope=("example.com", "api.example.com"),
        session_id="e2e_test_session",
        start_time=datetime(2024, 1, 1, tzinfo=timezone.utc)
    )
