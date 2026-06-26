from typing import List, Dict, Any, Optional
from schemas.runtime import RuntimeReport, InstallSummary, EnvironmentStatus
from runtime.doctor import Doctor
from runtime.installer import Installer
from runtime.verify import Verifier
from runtime.self_test import SelfTest
from runtime.preflight import Preflight

class RuntimeService:
    """Service layer abstraction for all operational commands."""

    def __init__(self):
        self.doctor = Doctor()
        self.installer = Installer()
        self.verifier = Verifier()
        self.self_test = SelfTest()
        self.preflight = Preflight()

    def run_doctor(self) -> RuntimeReport:
        """Diagnose the host machine environment."""
        return self.doctor.diagnose()

    def run_preflight(self, target: str, profile: str) -> bool:
        """Validate requirements for an upcoming scan."""
        return self.preflight.validate(target, profile)

    def run_install(self, dry_run: bool = False) -> InstallSummary:
        """Install dependencies and create installation manifest."""
        return self.installer.install(dry_run=dry_run)

    def run_verify(self) -> RuntimeReport:
        """Check installation integrity."""
        return self.verifier.verify()

    def run_self_test(self) -> bool:
        """Validate BugHunter's internal components."""
        return self.self_test.run()

    def run_release_check(self) -> bool:
        """Ultimate gate checking all systems."""
        # Orchestrate everything
        report_doctor = self.run_doctor()
        if report_doctor.summary_fail > 0:
            return False
            
        report_verify = self.run_verify()
        if report_verify.summary_fail > 0:
            return False
            
        if not self.run_self_test():
            return False
            
        return True
