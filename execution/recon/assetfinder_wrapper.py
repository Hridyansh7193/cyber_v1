from typing import Tuple, Any, Mapping, List
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class AssetfinderWrapper(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="assetfinder",
            version="0.1.1",
            description="Subdomain discovery via assetfinder",
            capabilities=("subdomain_discovery",),
            supported_tools=("assetfinder",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("assetfinder", "--subs-only", str(target))

    def validate(self, target: Any, config: Mapping[str, Any]) -> bool:
        return bool(target)

    def parse(self, stdout: str, stderr: str) -> List[str]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if line:
                results.append(line)
        return list(dict.fromkeys(results))

    def health_check(self) -> bool:
        return True

    @staticmethod
    def execute(domain: str) -> ToolResult:
        plugin = AssetfinderWrapper()
        command = plugin.build_command(domain, {})
        exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "assetfinder")
        
        parsed = []
        if exit_code == 0:
            parsed = plugin.parse(stdout, stderr)

        return ToolResult(
            tool_name="assetfinder",
            success=exit_code == 0,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            metadata={"domain": domain, "new_subdomains": parsed},
        )
