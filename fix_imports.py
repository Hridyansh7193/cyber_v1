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
    ("recon_transition", "passive_recon_transition"),
    ("recon_node", "passive_recon_node"),
    ("orchestration_state.task_status.get(\"recon\"", "orchestration_state.task_status.get(\"passive_recon\"")
]

for file in files:
    path = os.path.join(base_dir, file)
    if os.path.exists(path):
        replace_in_file(path, replacements)
        print(f"Updated {path}")
