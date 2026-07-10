import typer
import time
from rich.console import Console
from rich.table import Table
from typing import List
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from cli.exit_codes import SUCCESS
from config.loader import load_config
from services.scan_service import ScanService
from services.job_registry import JobRegistry
from services.orchestrator_adapter import OrchestratorAdapter

app = typer.Typer(help="Benchmark BugHunter across standard targets")
console = Console()

@app.command("benchmark")
@timed_cli_command
def benchmark_cmd(
    targets: List[str] = typer.Argument(
        ["localhost", "DVWA", "testphp.vulnweb.com", "scanme.nmap.org"], 
        help="List of targets to benchmark against"
    ),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """Run pipeline benchmark against multiple targets."""
    console.print("[bold]BugHunter Benchmark Suite[/bold]\n")
    
    config = load_config()
    
    registry = JobRegistry()
    adapter = OrchestratorAdapter(registry, config)
    scan_service = ScanService(adapter=adapter, registry=registry)
    
    table = Table("Target", "Runtime (s)", "Findings", "Errors", "Avg CPU (%)", "Avg RAM (MB)")
    
    total_runtime = 0.0
    total_findings = 0
    total_retries = 0 
    total_cpu = 0.0
    total_mem = 0.0
    
    results = []
    
    for target in targets:
        console.print(f"Benchmarking [cyan]{target}[/cyan]...")
        start_time = time.time()
        
        try:
            job_id = registry.create_job(target)
            
            import psutil
            process = psutil.Process()
            cpu_before = process.cpu_percent()
            
            # Run graph synchronously
            scan_service.run_scan_sync(target, config=config, job_id=job_id)
            
            import os
            import json
            from schemas.state import ExecutionState
            
            checkpoint_path = os.path.join("workspaces", target, "sessions", job_id, "checkpoint.json")
            final_state = None
            if os.path.exists(checkpoint_path):
                with open(checkpoint_path, "r", encoding="utf-8") as f:
                    final_state = ExecutionState(**json.load(f))
            
            end_time = time.time()
            runtime = end_time - start_time
            findings_count = len(final_state.findings) if final_state else 0
            errors_count = len([log for log in final_state.logs if not log.success]) if final_state else 0
            
            cpu_after = process.cpu_percent()
            mem_mb = process.memory_info().rss / (1024 * 1024)
            
            total_runtime += runtime
            total_findings += findings_count
            total_retries += errors_count
            total_cpu += cpu_after
            total_mem += mem_mb
            
            table.add_row(
                target, 
                f"{runtime:.2f}", 
                str(findings_count), 
                str(errors_count),
                f"{cpu_after:.1f}",
                f"{mem_mb:.1f}"
            )
            
            results.append({
                "target": target,
                "runtime": runtime,
                "findings": findings_count,
                "retries": errors_count,
                "cpu": cpu_after,
                "memory_mb": mem_mb
            })
            
        except Exception as e:
            console.print(f"[red]Error benchmarking {target}: {e}[/red]")
            table.add_row(target, "ERROR", "-", "-", "-", "-")

    if json_out:
        OutputFormatter.render(results, format="json")
    else:
        console.print(table)
        
        if len(results) > 0:
            console.print("\n[bold]Averages[/bold]")
            avg_runtime = total_runtime / len(results)
            avg_findings = total_findings / len(results)
            avg_retries = total_retries / len(results)
            avg_cpu = total_cpu / len(results)
            avg_mem = total_mem / len(results)
            
            console.print(f"Average runtime : {avg_runtime:.2f} s")
            console.print(f"Average findings: {avg_findings:.1f}")
            console.print(f"Average retries : {avg_retries:.1f}")
            console.print(f"Average CPU     : {avg_cpu:.1f} %")
            console.print(f"Average memory  : {avg_mem:.1f} MB")
            
    raise typer.Exit(code=SUCCESS)

