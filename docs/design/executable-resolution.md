# Executable Resolution Design

BugHunter dynamically invokes a wide variety of external security tools. Reliably resolving these tools across different environments poses several challenges:

1. **Non-Standard Paths**: Go binaries are often installed in `~/go/bin`, which may not be in the system `$PATH`.
2. **Naming Collisions**: Common binary names can collide with system tools or Python packages (e.g., ProjectDiscovery's `httpx` vs. the Python HTTP client library `httpx`).
3. **Missing Dependencies**: Failing fast with a clear error message is critical for user experience.

## The `ExecutableResolver`

To solve these issues, BugHunter uses the `ExecutableResolver` (`execution/utils/executable_resolver.py`).

### Resolution Strategy

When a plugin requests a binary (e.g., `httpx`), the resolver follows these steps:

1. **Path Inspection**: It looks up the binary in the standard system `$PATH` using `shutil.which`.
2. **Fallback Paths**: If not found, it expands and checks common fallback locations (e.g., `~/go/bin`).
3. **Signature Validation**: This is the most crucial step. Once a candidate executable path is found, the resolver invokes the binary with a validation flag (typically `-version` or `-h`) and inspects the standard output/error against an expected Regex signature.

### Signature Examples

For example, when resolving `httpx`:
- Expected signature: `(?i)projectdiscovery`
- Why? If a user has a Python virtual environment activated with the `httpx` package installed, typing `httpx` in the terminal might launch the Python REPL or script instead of the security tool. The signature validation ensures that the located `httpx` binary actually prints `projectdiscovery` in its version output.

### Caching

To avoid incurring the performance penalty of spawning validation processes on every plugin execution, the `ExecutableResolver` caches the validated absolute paths of binaries in memory. 

### Usage

Plugins should **never** hardcode binary paths. Instead, they should request the resolved path from the `PluginContext` or `ProcessRunner`, which transparently utilizes the `ExecutableResolver`.
