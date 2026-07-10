import os
import ast
from collections import defaultdict

def audit_repo(root_dir):
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        if 'venv' in root or '.git' in root or '__pycache__' in root or '.pytest_cache' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    classes = defaultdict(list)
    functions = defaultdict(list)
    todos = []
    not_implemented = []
    imports = defaultdict(list)

    for filepath in python_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for TODO, FIXME
            for i, line in enumerate(content.split('\n')):
                if 'TODO' in line or 'FIXME' in line:
                    todos.append((filepath, i+1, line.strip()))
                if 'NotImplementedError' in line or 'pass' == line.strip():
                    not_implemented.append((filepath, i+1, line.strip()))
            
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes[node.name].append(filepath)
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('test_'):
                        functions[node.name].append(filepath)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports[alias.name].append(filepath)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports[node.module].append(filepath)
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")

    # Duplicates
    print("--- DUPLICATE CLASSES ---")
    for name, paths in classes.items():
        if len(paths) > 1 and name not in ['Config', 'Meta', 'BaseModel']:
            print(f"{name} found in: {paths}")

    print("\n--- TODOs & FIXMEs ---")
    for todo in todos:
        print(f"{todo[0]}:{todo[1]} - {todo[2]}")

    print("\n--- POTENTIAL STUBS / NotImplemented ---")
    for ni in not_implemented:
        print(f"{ni[0]}:{ni[1]} - {ni[2]}")

if __name__ == "__main__":
    audit_repo(".")
