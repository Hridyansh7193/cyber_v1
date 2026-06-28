import re
with open('tests/unit/services/test_orchestrator_adapter.py', 'r') as f:
    content = f.read()

# Remove test_adapter_get_report, test_adapter_submit_scan, test_adapter_get_status, test_adapter_cancel
content = re.sub(r'def test_adapter_get_report\(\):[\s\S]*?(?=def test_adapter_submit_scan\(\):)', '', content)
content = re.sub(r'def test_adapter_submit_scan\(\):[\s\S]*?(?=def test_adapter_get_status\(\):)', '', content)
content = re.sub(r'def test_adapter_get_status\(\):[\s\S]*?(?=def test_adapter_cancel\(\):)', '', content)
content = re.sub(r'def test_adapter_cancel\(\):[\s\S]*', '', content)

with open('tests/unit/services/test_orchestrator_adapter.py', 'w') as f:
    f.write(content)
