import subprocess
import sys
import pytest

@pytest.mark.skipif(sys.version_info < (3, 12), reason="Requires Python >= 3.12 for pyproject.toml requirements")
def test_pip_install_and_import():
    # Install the package locally
    # It assumes that pyproject.toml exists in the current directory
    subprocess.run([sys.executable, "-m", "pip", "install", ".", "--ignore-requires-python"], check=True)
    
    # Import modules to verify packaging exposes them correctly
    script = (
        "import schemas\n"
        "import config\n"
        "import execution\n"
        "import agents\n"
        "import orchestrator\n"
        "import reporting\n"
        "import storage\n"
        "print('All modules imported successfully!')"
    )
    
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
    assert "All modules imported successfully!" in result.stdout
