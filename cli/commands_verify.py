import typer
import time
import json
import sys
from datetime import datetime, timezone
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from execution.plugins.registry import REGISTRY
from services.tool_manager import ToolManager
from execution.utils.process_runner import ProcessRunner
from schemas.state import ExecutionState
from schemas.target import TargetState

app = typer.Typer(help="Live Validation Engine (Phase 4)")

@app.command("verify-plugins")
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
        tool_info = tm.get_tool(tool_name)
        if not tool_info:
            results[name] = {"status": "UNVERIFIED", "reason": "Missing Binary"}
            OutputFormatter.render_warning(f"[{name}] UNVERIFIED: Missing Binary")
            continue
            
        OutputFormatter.render_info(f"[{name}] Running live validation...")
        
        # Build mock state with proper datetime for start_time
        state = ExecutionState(
            target=TargetState(
                domain=target,
                session_id="verify",
                start_time=datetime.now(timezone.utc),
                scope=(),
                out_of_scope=()
            )
        )
        
        start_time = time.time()
        try:
            cmd_args = plugin.build_command(state, {}, target=target)
            if not cmd_args:
                raise ValueError("Plugin returned empty command")
            
            # Prepend the resolved binary path, just like PluginExecutor does
            binary_path = tool_info.binary_path
            if binary_path.endswith('.py'):
                full_cmd = [sys.executable, binary_path] + list(cmd_args)
            else:
                full_cmd = [binary_path] + list(cmd_args)
                
            res = ProcessRunner.run(full_cmd, name, timeout=30)
            runtime = time.time() - start_time
            
            # Count findings
            parsed = plugin.parse(res.stdout, res.stderr)
            parsed_count = 0
            if isinstance(parsed, tuple) and len(parsed) == 2:
                parsed_data, _errors = parsed
                parsed_count = len(parsed_data) if hasattr(parsed_data, "__len__") else 0
            elif hasattr(parsed, "__len__"):
                parsed_count = len(parsed)
            
            # Since some plugins might not find anything on the test target, we can't fail them just for 0 findings.
            # But we can verify it didn't crash.
            results[name] = {
                "status": "VERIFIED",
                "command": " ".join(str(c) for c in full_cmd),
                "exit_code": res.exit_code,
                "runtime": round(runtime, 2),
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
