import pytest
from uuid import uuid4
from schemas.generated_report import GeneratedReport
from pydantic import ValidationError

def test_generated_report_immutability():
    report = GeneratedReport(
        report_id=uuid4(),
        format="markdown",
        filename="test.md",
        mime_type="text/markdown",
        content="hello"
    )
    
    with pytest.raises(ValidationError):
        report.filename = "new.md"
