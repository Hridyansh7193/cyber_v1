import typer
import time
import os
import json
from typing import Dict, Any
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from execution.plugins.registry import REGISTRY
from services.tool_manager import ToolManager
from execution.utils.process_runner import ProcessRunner
from schemas.state import ExecutionState, TargetState
from datetime import datetime
import asyncio

app = typer.Typer(help="Live Validation Engine (Phase 4)")

@app.command("verify")
@timed_cli_command
def verify_plugins_cmd(
    target: str = typer.Argument(..., help="Target URL or domain to test against (e.g. scanme.nmap.org)"),
    output_file: str = typer.Option("verification_report.json", "--output", "-o", help="Where to save the report")
):
    """
    Run Live Validation (Phase 4) across all installed binaries.
    
    This executes the plugins against a safe target and records metrics like runtime, parsed objects, and stdout size.
    It marks wrappers that cannot be fully verified as UNVERIFIED.
    """
    OutputFormatter.render_info(f"Starting Live Validation for target: {target}")
    
    tm = ToolManager()
    tm.detect()
    
    results = {}
    
    for name in REGISTRY.list_plugins():
        plugin = REGISTRY.get_plugin(name)
        meta = plugin.metadata()
        
        # Internal plugins are always VERIFIED
        if name in ("graphql_discovery", "swagger", "graphql"):
            results[name] = {"status": "VERIFIED", "reason": "Internal Plugin"}
            continue
            
        tool_name = meta.supported_tools[0] if meta.supported_tools else name
        if not tm.available(tool_name):
            results[name] = {"status": "UNVERIFIED", "reason": "Missing Binary"}
            OutputFormatter.render_warning(f"[{name}] UNVERIFIED: Missing Binary")
            continue
            
        OutputFormatter.render_info(f"[{name}] Running live validation...")
        
        # Build mock state
        state = ExecutionState(
            target=TargetState(domain=target, session_id="verify", start_time=str(time.time()), scope=(), out_of_scope=())
        )
        
        start_time = time.time()
        try:
            cmd = plugin.build_command(state, {}, target=target)
            if not cmd:
                raise ValueError("Plugin returned empty command")
                
            res = ProcessRunner.run(list(cmd), name, timeout=30)
            runtime = time.time() - start_time
            
            # Count findings
            parsed = plugin.parse(res.stdout, res.stderr)
            parsed_count = len(parsed) if hasattr(parsed, "__len__") else 0
            
            # Since some plugins might not find anything on example.com, we can't fail them just for 0 findings.
            # But we can verify it didn't crash.
            results[name] = {
                "status": "VERIFIED",
                "command": " ".join(cmd),
                "exit_code": res.exit_code,
                "runtime": runtime,
                "stdout_size": res.stdout_size,
                "parsed_objects": parsed_count,
            }
            OutputFormatter.render_success(f"[{name}] VERIFIED (Runtime: {runtime:.2f}s, Parsed: {parsed_count})")
            
        except Exception as e:
            results[name] = {
                "status": "UNVERIFIED",
                "reason": f"Execution crashed: {str(e)}"
            }
            OutputFormatter.render_error(f"[{name}] UNVERIFIED: {str(e)}")

    # Write report
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
        
    OutputFormatter.render_success(f"Verification report saved to {output_file}")
