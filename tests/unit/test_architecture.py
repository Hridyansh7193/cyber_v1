import ast
import glob

def get_imports(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except Exception:
            return set()
            
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
                imports.add(node.module)
    return imports

def test_api_imports_no_repositories():
    for f in glob.glob("api/**/*.py", recursive=True):
        imports = get_imports(f)
        for imp in imports:
            assert not imp.startswith("repositories")
            assert not imp.startswith("storage")

def test_api_imports_no_orchestrator():
    for f in glob.glob("api/**/*.py", recursive=True):
        imports = get_imports(f)
        for imp in imports:
            assert not imp.startswith("orchestrator")

def test_cli_imports_no_repositories():
    for f in glob.glob("cli/**/*.py", recursive=True):
        imports = get_imports(f)
        for imp in imports:
            assert not imp.startswith("repositories")
            assert not imp.startswith("storage")

def test_cli_imports_no_orchestrator():
    for f in glob.glob("cli/**/*.py", recursive=True):
        imports = get_imports(f)
        for imp in imports:
            assert not imp.startswith("orchestrator")

def test_services_import_no_fastapi():
    for f in glob.glob("services/**/*.py", recursive=True):
        imports = get_imports(f)
        for imp in imports:
            assert not imp.startswith("fastapi")

def test_services_import_no_typer():
    for f in glob.glob("services/**/*.py", recursive=True):
        imports = get_imports(f)
        for imp in imports:
            assert not imp.startswith("typer")
            assert not imp.startswith("rich")

def test_job_registry_imports_no_langgraph():
    imports = get_imports("services/job_registry.py")
    for imp in imports:
        assert not imp.startswith("langgraph")

def test_only_adapter_imports_orchestrator():
    # Only orchestrator_adapter.py inside services can import orchestrator
    for f in glob.glob("services/**/*.py", recursive=True):
        from pathlib import Path
        if Path(f).name != "orchestrator_adapter.py":
            imports = get_imports(f)
            for imp in imports:
                assert not imp.startswith("orchestrator")
