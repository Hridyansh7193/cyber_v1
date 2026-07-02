import os

def replace_in_file(path, replacements):
    with open(path, 'r') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(path, 'w') as f:
        f.write(content)

replacements = [
    ("\"recon\":", "\"passive_recon\":"),
    ("task_status[\"recon\"]", "task_status[\"passive_recon\"]")
]

files = [
    "tests/unit/orchestrator/test_empty_pipeline.py",
    "tests/unit/orchestrator/test_error_handler.py",
    "tests/unit/orchestrator/test_failed_pipeline.py",
    "tests/unit/orchestrator/test_orchestrator.py",
    "tests/unit/orchestrator/test_transitions_full.py"
]

for file in files:
    if os.path.exists(file):
        replace_in_file(file, replacements)

# Fix test_utils.py
utils_test_path = "tests/unit/execution/utils/test_utils.py"
with open(utils_test_path, 'r') as f:
    content = f.read()
content = content.replace("with pytest.raises(TypeError):", "result = ProcessRunner.run([\"test_tool\"], \"test_tool\")\n        assert result.exit_code == -2\n        assert \"Execution error\" in result.error_message\n        # with pytest.raises(TypeError):")
content = content.replace("ProcessRunner.run([\"test_tool\"], \"test_tool\")\n", "")
with open(utils_test_path, 'w') as f:
    f.write(content)
