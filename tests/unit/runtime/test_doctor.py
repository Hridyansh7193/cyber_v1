from runtime.doctor import Doctor
from schemas.runtime import RuntimeReport
from execution.api.graphql_wrapper import GraphQLPlugin
from services.tool_manager import ToolManager


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


def test_graphql_self_test_uses_supported_tool_name(monkeypatch):
    monkeypatch.setattr(ToolManager, "available", lambda self, name: name in {"graphql_discover", "graphql"})

    result = GraphQLPlugin().self_test()

    assert result.binary is True


def test_tool_manager_detects_arjun(monkeypatch):
    tm = ToolManager()
    tm._tools = {}
    monkeypatch.setattr(tm, "_find_binary", lambda name: "/usr/bin/arjun" if name == "arjun" else None)
    monkeypatch.setattr(tm, "_detect_version", lambda path, tool_name: "2.1.0")

    tm.detect()

    assert tm.get_tool("arjun") is not None
