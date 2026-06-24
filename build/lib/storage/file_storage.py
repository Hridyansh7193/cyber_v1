from pathlib import Path
from schemas.generated_report import GeneratedReport

def save_generated_file(generated_report: GeneratedReport, output_dir: Path) -> Path:
    # Storage owns filesystem writes only
    output_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = output_dir / generated_report.filename
    
    mode = "wb" if generated_report.is_binary else "w"
    kwargs = {} if generated_report.is_binary else {"encoding": "utf-8", "newline": "\n"}
    
    with open(file_path, mode, **kwargs) as f:
        f.write(generated_report.content)
        
    return file_path
