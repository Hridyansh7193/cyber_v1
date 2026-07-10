"""Plugin Certification Matrix Generator.

Imports the plugin registry and tests each plugin for:
1. Binary availability (is the tool installed and on PATH?)
2. Version detection
3. Self-test (parser + command builder smoke test)
"""
import sys
import shutil
import subprocess
import json

sys.path.insert(0, ".")

from execution.plugins.registry import REGISTRY
from schemas.runtime import SelfTestResult


def get_version(binary_name: str) -> str:
    """Try common version flags to detect tool version."""
    for flag in ["-version", "--version", "version"]:
        try:
            res = subprocess.run(
                [binary_name, flag],
                capture_output=True, text=True, timeout=5
            )
            output = (res.stdout or res.stderr or "").strip()
            if output:
                # Return first non-empty line, truncated
                first_line = output.split("\n")[0].strip()
                return first_line[:40]
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return "Detected"


def certify_plugins():
    plugins = REGISTRY.list_plugins()
    results = []

    for name in plugins:
        plugin = REGISTRY.get_plugin(name)
        meta = plugin.metadata()

        # 1. Binary check
        binary_name = None
        for tool in meta.supported_tools:
            binary_name = tool
            break

        installed = False
        version = "N/A"

        if binary_name:
            path = shutil.which(binary_name)
            if path:
                installed = True
                version = get_version(binary_name)
            else:
                installed = False
                version = "Missing"
        else:
            # Pure-python plugin (e.g., swagger, graphql)
            installed = True
            version = "Python"

        # 2. Self-test
        self_test_pass = False
        self_test_detail = ""
        try:
            result: SelfTestResult = plugin.self_test()
            self_test_pass = result.passed
            self_test_detail = result.message if hasattr(result, 'message') else ""
        except Exception as e:
            self_test_detail = str(e)[:50]

        # 3. Certification status
        if installed and self_test_pass:
            status = "CERTIFIED"
        elif installed and not self_test_pass:
            status = "WARN"
        else:
            status = "FAIL"

        results.append({
            "plugin": name,
            "installed": installed,
            "version": version,
            "self_test": self_test_pass,
            "self_test_detail": self_test_detail,
            "status": status,
            "capabilities": [c.value for c in meta.capabilities],
        })

    # Print table
    print("=" * 90)
    print("                    PLUGIN CERTIFICATION MATRIX")
    print("=" * 90)
    print(f"{'Plugin':<16} | {'Installed':<10} | {'Version':<20} | {'Self Test':<10} | {'Status'}")
    print("-" * 90)

    certified = 0
    warned = 0
    failed = 0
    for r in results:
        inst = "Yes" if r["installed"] else "No"
        st = "PASS" if r["self_test"] else "FAIL"
        print(f"{r['plugin']:<16} | {inst:<10} | {r['version']:<20} | {st:<10} | {r['status']}")
        if r["status"] == "CERTIFIED":
            certified += 1
        elif r["status"] == "WARN":
            warned += 1
        else:
            failed += 1

    print("-" * 90)
    print(f"Total: {len(results)}  |  Certified: {certified}  |  Warn: {warned}  |  Fail: {failed}")
    print()

    # Write JSON for artifact generation
    with open("plugin_certification_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results written to plugin_certification_results.json")


if __name__ == "__main__":
    certify_plugins()
