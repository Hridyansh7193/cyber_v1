import os
import sys
import zipfile
from pathlib import Path

def main():
    root = Path(__file__).parent.parent
    packages = [
        "agents", "api", "cli", "config", "core_logging", 
        "execution", "memory", "orchestration", "orchestrator",
        "reporting", "runtime", "schemas", "services", "storage"
    ]
    
    # 1. Check __init__.py in all packages
    print("Checking __init__.py files...")
    for pkg in packages:
        pkg_path = root / pkg
        if not pkg_path.exists():
            print(f"ERROR: Package directory {pkg} does not exist.")
            sys.exit(1)
        init_file = pkg_path / "__init__.py"
        if not init_file.exists():
            print(f"ERROR: Missing __init__.py in {pkg}")
            sys.exit(1)
            
    # 2. Check MANIFEST.in
    print("Checking MANIFEST.in...")
    manifest = root / "MANIFEST.in"
    if not manifest.exists():
        print("ERROR: Missing MANIFEST.in")
        sys.exit(1)
        
    manifest_content = manifest.read_text()
    if "include README.md" not in manifest_content or "include LICENSE" not in manifest_content:
        print("ERROR: MANIFEST.in is missing core file inclusions")
        sys.exit(1)
        
    # 3. Check for specific YAML files existence
    print("Checking essential YAMLs...")
    yamls = ["minimal.yaml", "bug_bounty.yaml", "stealth.yaml", "full.yaml"]
    for y in yamls:
        y_path = root / "config" / "scan_profiles" / "default" / y
        if not y_path.exists():
            print(f"ERROR: Missing YAML profile {y}")
            sys.exit(1)

    print("Checking dist/*.whl contents (if exists)...")
    dist_dir = root / "dist"
    if dist_dir.exists():
        wheels = list(dist_dir.glob("*.whl"))
        for w in wheels:
            with zipfile.ZipFile(w, 'r') as zf:
                files = zf.namelist()
                has_yaml = any(f.endswith('.yaml') for f in files)
                if not has_yaml:
                    print(f"ERROR: Wheel {w.name} does not contain any .yaml files")
                    sys.exit(1)
                    
    print("Package check PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
