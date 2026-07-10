"""Performance Baseline Measurement for BugHunter v1.0.0-rc1.

Measures:
- Import / startup time
- Doctor execution time
- Plugin registry load time
- Test suite execution time
"""
import time
import sys
import subprocess
import json

sys.path.insert(0, ".")


def measure(label: str, func):
    start = time.perf_counter()
    result = func()
    elapsed = time.perf_counter() - start
    print(f"  {label}: {elapsed:.3f}s")
    return elapsed, result


def measure_import():
    """Measure core module import time."""
    start = time.perf_counter()
    from execution.plugins.registry import REGISTRY  # noqa: F401
    from schemas.state import ExecutionState  # noqa: F401
    from services.scan_service import ScanService  # noqa: F401
    elapsed = time.perf_counter() - start
    print(f"  Core import: {elapsed:.3f}s")
    return elapsed


def measure_doctor():
    """Measure doctor command execution time."""
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-m", "cli.main", "doctor"],
        capture_output=True, text=True, timeout=60
    )
    elapsed = time.perf_counter() - start
    print(f"  Doctor: {elapsed:.3f}s")
    return elapsed


def measure_registry():
    """Measure plugin registry load and iteration."""
    from execution.plugins.registry import REGISTRY
    start = time.perf_counter()
    plugins = REGISTRY.list_plugins()
    for name in plugins:
        p = REGISTRY.get_plugin(name)
        _ = p.metadata()
    elapsed = time.perf_counter() - start
    print(f"  Registry ({len(plugins)} plugins): {elapsed:.3f}s")
    return elapsed


def measure_tests():
    """Measure test suite execution time."""
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--tb=no", "-q"],
        capture_output=True, text=True, timeout=120
    )
    elapsed = time.perf_counter() - start
    # Parse results
    last_line = result.stdout.strip().split("\n")[-1]
    print(f"  Test suite: {elapsed:.3f}s ({last_line})")
    return elapsed


def main():
    print("=" * 60)
    print("   BugHunter v1.0.0-rc1 Performance Baseline")
    print("=" * 60)
    print()

    results = {}

    print("[1/4] Startup / Import")
    results["import"] = measure_import()

    print("[2/4] Plugin Registry")
    results["registry"] = measure_registry()

    print("[3/4] Doctor Command")
    results["doctor"] = measure_doctor()

    print("[4/4] Full Test Suite")
    results["tests"] = measure_tests()

    print()
    print("=" * 60)
    print("   BASELINE SUMMARY")
    print("=" * 60)
    print(f"  Import:   {results['import']:.3f}s")
    print(f"  Registry: {results['registry']:.3f}s")
    print(f"  Doctor:   {results['doctor']:.3f}s")
    print(f"  Tests:    {results['tests']:.3f}s")
    print()

    with open("performance_baseline_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results written to performance_baseline_results.json")


if __name__ == "__main__":
    main()
