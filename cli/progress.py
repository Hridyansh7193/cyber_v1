from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
import time
import threading
import logging

# How long (seconds) to wait between polls
_POLL_INTERVAL = 0.5
# How many consecutive dead-thread polls before we declare failure
_DEAD_THREAD_GRACE_POLLS = 10  # Increased from 3 to 10 (5 seconds)


def track_scan_progress(scan_service, job_id: str):
    """
    Poll scan status and render a Rich progress bar.

    Also monitors the worker thread health — if the thread dies while the job
    is still marked RUNNING, we detect it and mark it FAILED instead of
    polling indefinitely.
    
    CRITICAL: This function MUST block until either:
    1. The scan completes (status in completed/failed/cancelled AND progress >= 100%)
    2. The worker thread dies unexpectedly
    3. Timeout occurs (should not happen in normal operation)
    
    This ensures the CLI never exits while work is still being done.
    """
    from services.job_registry import JobStatus
    
    logger = logging.getLogger("cli.progress")

    worker_thread: threading.Thread = None
    if hasattr(scan_service, "get_worker_thread"):
        worker_thread = scan_service.get_worker_thread(job_id)
        if worker_thread:
            logger.debug(f"[PROGRESS] Worker thread found: {worker_thread.name} (alive={worker_thread.is_alive()})")
        else:
            logger.warning(f"[PROGRESS] No worker thread found for job {job_id}")

    dead_thread_count = 0
    poll_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Initializing scan...", total=100.0)

        while True:
            poll_count += 1
            status = scan_service.get_status(job_id)
            
            if not status:
                logger.error(f"[PROGRESS] Scan {job_id} not found in registry")
                progress.update(task, description="[red]Scan not found")
                break

            state = status["status"]
            pct = status.get("progress", 0.0)
            stage = status.get("current_stage", "unknown")
            
            logger.debug(
                f"[PROGRESS] Poll #{poll_count} | status={state} | progress={pct:.1f}% | stage={stage}"
            )
            
            # --- Check for terminal states first ---
            if state in ("completed", "failed", "cancelled"):
                color = "green" if state == "completed" else "red"
                # Always set to 100% when done
                progress.update(task, completed=100.0, description=f"[{color}]Scan {state}")
                logger.info(f"[PROGRESS] Scan terminal state reached: {state}")
                break

            # --- Watchdog: detect dead worker thread ---
            if worker_thread is not None:
                if not worker_thread.is_alive():
                    dead_thread_count += 1
                    logger.warning(
                        f"[PROGRESS] Worker thread not alive (count={dead_thread_count}/{_DEAD_THREAD_GRACE_POLLS})"
                    )
                    
                    if dead_thread_count >= _DEAD_THREAD_GRACE_POLLS:
                        # Thread is gone but status never updated — silent-crash bug
                        logger.error(
                            f"[PROGRESS] Worker thread died unexpectedly after {dead_thread_count} polls. "
                            f"Current status: {state}, progress: {pct:.1f}%"
                        )
                        progress.update(task, description="[red]Scan worker died unexpectedly")
                        
                        # Force status update if needed
                        if hasattr(scan_service, "_registry") and state not in (
                            "completed", "failed", "cancelled"
                        ):
                            reg = scan_service._registry
                            job = reg.get_job(job_id)
                            if job and job.status not in (
                                JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED
                            ):
                                reg.update_status(
                                    job_id, JobStatus.FAILED,
                                    "Worker thread died without updating status"
                                )
                                logger.error(f"[PROGRESS] Forced job status to FAILED")
                        break
                else:
                    # Thread is alive, reset counter
                    if dead_thread_count > 0:
                        logger.debug(f"[PROGRESS] Worker thread is alive again, resetting dead count")
                    dead_thread_count = 0

            # --- Update progress bar ---
            # Prevent Rich from thinking we're done if math rounds up
            display_pct = pct if pct < 100.0 else 99.0 if state not in ("completed", "failed", "cancelled") else 100.0
            
            progress.update(task, completed=display_pct, description=f"[cyan]Running stage: {stage}")
            time.sleep(_POLL_INTERVAL)

    # --- Block CLI exit until the worker thread actually finishes ---
    # This is the MOST CRITICAL part. Without this, the CLI exits while work is still running.
    if worker_thread is not None:
        logger.info(f"[PROGRESS] Waiting for worker thread to finish: {worker_thread.name}")
        worker_thread.join(timeout=None)  # No timeout - wait forever
        logger.info(f"[PROGRESS] Worker thread finished")
    else:
        logger.warning("[PROGRESS] No worker thread to join - CLI may exit while scan is running")
