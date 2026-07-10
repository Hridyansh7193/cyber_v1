from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
import time
import threading

# How long (seconds) to wait between polls
_POLL_INTERVAL = 0.5
# How many consecutive dead-thread polls before we declare failure
_DEAD_THREAD_GRACE_POLLS = 3


def track_scan_progress(scan_service, job_id: str):
    """
    Poll scan status and render a Rich progress bar.

    Also monitors the worker thread health — if the thread dies while the job
    is still marked RUNNING, we detect it and mark it FAILED instead of
    polling indefinitely.
    """
    from services.job_registry import JobStatus

    worker_thread: threading.Thread = None
    if hasattr(scan_service, "get_worker_thread"):
        worker_thread = scan_service.get_worker_thread(job_id)

    dead_thread_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Initializing scan...", total=100.0)

        while True:
            status = scan_service.get_status(job_id)
            if not status:
                progress.update(task, description="[red]Scan not found")
                break

            state = status["status"]
            if state in ("completed", "failed", "cancelled"):
                color = "green" if state == "completed" else "red"
                progress.update(task, completed=100.0, description=f"[{color}]Scan {state}")
                break

            # --- Watchdog: detect dead worker thread ---
            if worker_thread is not None and not worker_thread.is_alive():
                dead_thread_count += 1
                if dead_thread_count >= _DEAD_THREAD_GRACE_POLLS:
                    # Thread is gone but status never updated — this is the silent-crash bug.
                    # Force a registry update so callers know the scan failed.
                    progress.update(task, description="[red]Scan worker died unexpectedly")
                    if hasattr(scan_service, "_registry"):
                        from services.job_registry import JobStatus
                        reg = scan_service._registry
                        job = reg.get_job(job_id)
                        if job and job.status not in (
                            JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED
                        ):
                            reg.update_status(
                                job_id, JobStatus.FAILED,
                                "Worker thread died without updating status"
                            )
                    break
            else:
                dead_thread_count = 0  # reset if thread comes back alive

            stage = status.get("current_stage", "unknown")
            pct = status.get("progress", 0.0)

            # Prevent Rich from thinking we're done early if math rounds up
            if pct >= 100.0 and state not in ("completed", "failed", "cancelled"):
                pct = 99.0

            progress.update(task, completed=pct, description=f"[cyan]Running stage: {stage}")
            time.sleep(_POLL_INTERVAL)

    # Block CLI exit until the worker thread actually finishes.
    # This prevents the process from exiting and killing any remaining work.
    if worker_thread is not None and worker_thread.is_alive():
        worker_thread.join()
