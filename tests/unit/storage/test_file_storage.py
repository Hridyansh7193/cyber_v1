import pytest
from uuid import uuid4
from schemas.generated_report import GeneratedReport
from storage.file_storage import save_generated_file
import os
import stat
import platform

def test_save_generated_file(tmp_path):
    report = GeneratedReport(
        report_id=uuid4(),
        format="markdown",
        filename="test.md",
        mime_type="text/markdown",
        encoding="utf-8",
        content="Hello, World!",
        is_binary=False
    )
    
    saved_path = save_generated_file(report, tmp_path)
    
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8") == "Hello, World!"

def test_save_generated_file_overwrite(tmp_path):
    report = GeneratedReport(
        report_id=uuid4(),
        format="markdown",
        filename="test.md",
        mime_type="text/markdown",
        encoding="utf-8",
        content="First",
        is_binary=False
    )
    save_generated_file(report, tmp_path)
    
    report2 = GeneratedReport(
        report_id=report.report_id,
        format="markdown",
        filename="test.md",
        mime_type="text/markdown",
        encoding="utf-8",
        content="Second",
        is_binary=False
    )
    saved_path = save_generated_file(report2, tmp_path)
    assert saved_path.read_text(encoding="utf-8") == "Second"

def test_permission_error_propagation(tmp_path):
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    
    # Change permissions
    os.chmod(readonly_dir, stat.S_IREAD)
    
    report = GeneratedReport(
        report_id=uuid4(),
        format="markdown",
        filename="test.md",
        mime_type="text/markdown",
        encoding="utf-8",
        content="Fail",
        is_binary=False
    )
    
    try:
        if platform.system() != "Windows":
            with pytest.raises(PermissionError):
                save_generated_file(report, readonly_dir)
        else:
            # On Windows, os.chmod on directory does not strictly block file creation. 
            # We'll test with a read-only file instead.
            file_path = readonly_dir / "test.md"
            file_path.write_text("Hello")
            os.chmod(file_path, stat.S_IREAD)
            with pytest.raises(PermissionError):
                save_generated_file(report, readonly_dir)
    finally:
        os.chmod(readonly_dir, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
        if platform.system() == "Windows":
            os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
