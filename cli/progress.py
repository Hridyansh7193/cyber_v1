from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
import time

def track_scan_progress(scan_service, job_id: str):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Initializing scan...", total=100.0)
        
        while not progress.finished:
            status = scan_service.get_status(job_id)
            if not status:
                break
                
            state = status["status"]
            if state in ("completed", "failed", "cancelled"):
                color = "green" if state == "completed" else "red"
                progress.update(task, completed=100.0, description=f"[{color}]Scan {state}")
                break
                
            stage = status.get("current_stage", "unknown")
            pct = status.get("progress", 0.0)
            progress.update(task, completed=pct, description=f"[cyan]Running stage: {stage}")
            time.sleep(0.5)
