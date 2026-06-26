import json
from pathlib import Path
from schemas.runtime import RuntimeReport
from runtime.doctor import Doctor
from runtime.workspace import WorkspaceManager

class Verifier:
    """Verifies installation integrity and runtime compatibility."""

    def verify(self) -> RuntimeReport:
        # Check if installation.json exists
        if not Path("installation.json").exists():
            print("WARNING: installation.json is missing. Please run `bughunter install`.")
            
        ws = WorkspaceManager()
        if not ws.verify_integrity():
            print("Repairing missing workspace directories...")
            ws.initialize()
            
        doctor = Doctor()
        report = doctor.diagnose()
        
        print("\nBugHunter Compatibility Report")
        print("------------------------------")
        print(f"Python: {'PASS' if report.environment.python_version else 'FAIL'}")
        print(f"Go: {'PASS' if report.environment.go_version else 'FAIL'}")
        print(f"Kernel: {'PASS' if report.environment.kernel else 'FAIL'}")
        print(f"Plugins: {'PASS' if all(p.status == 'PASS' for p in report.plugins) else 'WARN'}")
        print(f"Workspace: {'PASS' if ws.verify_integrity() else 'FAIL'}")
        print("------------------------------")
        
        return report
