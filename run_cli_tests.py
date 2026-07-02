import subprocess
import time

commands = [
    ["python", "-m", "cli.main", "--version"],
    ["python", "-m", "cli.main", "--help"],
    ["python", "-m", "cli.main", "doctor"],
    ["python", "-m", "cli.main", "verify"],
    ["python", "-m", "cli.main", "self-test"],
    ["python", "-m", "cli.main", "plugins"],
    ["python", "-m", "cli.main", "jobs"],
    ["python", "-m", "cli.main", "status", "123"],
    ["python", "-m", "cli.main", "search", "test"],
    ["python", "-m", "cli.main", "workspace", "list"],
    ["python", "-m", "cli.main", "scan", "--help"],
    ["python", "-m", "cli.main", "report", "--help"],
    ["python", "-m", "cli.main", "workspace", "--help"],
]

for cmd in commands:
    print(f"\nRunning: {' '.join(cmd)}")
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        end = time.time()
        print(f"Exit Code: {result.returncode}")
        print(f"Runtime: {end - start:.2f}s")
        if result.returncode != 0:
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
    except subprocess.TimeoutExpired:
        print("TIMEOUT EXPIRED (10s)")
