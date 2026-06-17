import pytest
import os
import glob

def test_planner_unused():
    # Verify grep -r "plan(" orchestrator/ and grep -r "PlannerAgent" orchestrator/ yield 0
    # We do a fast Python-based search here
    orchestrator_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "orchestrator")
    
    for root, _, files in os.walk(orchestrator_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    assert "plan(" not in content, f"plan() leaked in {file}"
                    assert "PlannerAgent" not in content, f"PlannerAgent leaked in {file}"
