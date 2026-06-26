import pytest
from runtime.doctor import Doctor
from schemas.runtime import RuntimeReport

def test_doctor_diagnose():
    doctor = Doctor()
    report = doctor.diagnose()
    assert isinstance(report, RuntimeReport)
    assert report.environment.os in ["Windows", "Linux", "Darwin"]
    assert report.environment.python_version.startswith("3.")
    
    assert len(report.dependencies) > 0
    assert len(report.plugins) > 0
    assert len(report.checks) > 0
    
    assert report.summary_pass + report.summary_warn + report.summary_fail == (
        len(report.dependencies) + len(report.plugins) + len(report.checks)
    )
