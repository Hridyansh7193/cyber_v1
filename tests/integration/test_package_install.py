import subprocess
import sys


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
