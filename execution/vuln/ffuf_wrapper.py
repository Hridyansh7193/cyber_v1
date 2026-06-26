import json
from typing import Tuple, Any, Mapping, List
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class FfufPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ffuf",
            version="2.0.0",
            description="Content discovery via ffuf",
            capabilities=("content_discovery", "fuzzing"),
            supported_tools=("ffuf",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        wordlist = config.get("wordlist", "common.txt")
        return ("ffuf", "-u", f"{str(target)}/FUZZ", "-w", wordlist, "-json", "-silent")

    def validate(self, target: Any, config: Mapping[str, Any]) -> bool:
        return bool(target)

    def parse(self, stdout: str, stderr: str) -> List[Mapping[str, Any]]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if "results" in data:
                    results.extend(data["results"])
                else:
                    results.append(data)
            except json.JSONDecodeError:
                pass
        return results

    def health_check(self) -> bool:
        return True

class FfufWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
    @staticmethod
    def execute(target_url: str, wordlist: str) -> ToolResult:
        plugin = FfufPlugin()
        command = plugin.build_command(target_url, {"wordlist": wordlist})
        exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "ffuf")

        parsed = []
        if exit_code == 0:
            parsed = plugin.parse(stdout, stderr)

        return ToolResult(
            tool_name="ffuf",
            success=exit_code == 0,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            metadata={"target_url": target_url, "wordlist": wordlist, "parsed_results": parsed},
        )
