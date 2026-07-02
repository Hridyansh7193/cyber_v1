import os

def replace_in_file(path, replacements):
    with open(path, 'r') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(path, 'w') as f:
        f.write(content)

base_dir = "tests/unit/orchestrator"
files = [
    "test_empty_pipeline.py",
    "test_error_handler.py",
    "test_failed_pipeline.py",
    "test_orchestrator.py",
    "test_transitions_full.py"
]

replacements = [
    ("task_status={\"recon\":", "task_status={\"passive_recon\":"),
    ("task_status={\"recon\": \"FAILED\"}", "task_status={\"passive_recon\": \"FAILED\"}"),
    ("passive_recon_transition(state) == \"js_node\"", "passive_recon_transition(state) == \"scope_enforcement_node\""),
    ("passive_recon_transition(graph_state) == \"js_node\"", "passive_recon_transition(graph_state) == \"scope_enforcement_node\"")
]

for file in files:
    path = os.path.join(base_dir, file)
    if os.path.exists(path):
        replace_in_file(path, replacements)
        print(f"Updated {path}")
