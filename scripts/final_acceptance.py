import subprocess
import os

def run_cmd(cmd):
    print(f"Running: {cmd}")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    result = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
    return result

def main():
    print("Running Final Acceptance Script for BugHunter V1")
    
    # 1. Version
    res = run_cmd("python cli/main.py version")
    assert res.returncode == 0
    assert "BugHunter v0.1.0" in res.stdout
    print("[PASS] Version command")
    
    # 2. Config validation
    res = run_cmd("python cli/main.py validate-config config")
    assert res.returncode == 0, f"Failed config validation: {res.stderr} {res.stdout}"
    print("[PASS] Config validation command")
    
    # 3. Status for non-existent job
    res = run_cmd("python cli/main.py status non_existent_job_123")
    assert res.returncode == 1
    assert "Job not found" in res.stdout
    print("[PASS] Status for missing job")
    
    # 4. Jobs command
    res = run_cmd("python cli/main.py jobs")
    assert res.returncode == 0
    print("[PASS] Jobs command")
    
    # 5. Missing logs command
    res = run_cmd("python cli/main.py logs non_existent_job_123")
    assert res.returncode == 1
    print("[PASS] Logs command for missing job")
    
    print("\nAll CLI commands executed properly without unhandled exceptions.")
    print("Final acceptance passed.")
    
if __name__ == "__main__":
    main()
