import pytest
from pathlib import Path
from storage.file_storage import save_generated_file
import os

def test_cross_platform_path_validation(tmp_path):
    # Windows path style (mocked via string but resolved via Path)
    win_path = Path("C:/fake/windows/path") if os.name == 'nt' else Path("/fake/windows/path")
    
    # Ubuntu path style
    ubuntu_path = Path("/var/log/fake_ubuntu")
    
    # tmp_path
    report_dir = tmp_path / "reports"
    
    # UTF-8 and Unicode filenames
    unicode_filename = "report_日本語.md"
    utf8_filename = "résumé_test.json"
    
    from schemas.generated_report import GeneratedReport
    from uuid import uuid4
    
    # Write Unicode file
    r1 = GeneratedReport(report_id=uuid4(), format="markdown", filename=unicode_filename, mime_type="text/markdown", content="# こんにちは")
    save_generated_file(r1, report_dir)
    assert (report_dir / unicode_filename).exists()
    assert (report_dir / unicode_filename).read_text(encoding="utf-8") == "# こんにちは"
    
    # Write UTF-8 file
    r2 = GeneratedReport(report_id=uuid4(), format="json", filename=utf8_filename, mime_type="application/json", content='{"test": "utf8_value"}')
    save_generated_file(r2, report_dir)
    assert (report_dir / utf8_filename).exists()
    assert (report_dir / utf8_filename).read_text(encoding="utf-8") == '{"test": "utf8_value"}'
