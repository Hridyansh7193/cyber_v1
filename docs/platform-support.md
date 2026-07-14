# Platform Support

BugHunter v1.0 is designed with a specific canonical runtime environment in mind, dictated by the heavy reliance on external security tools (like ProjectDiscovery's `nuclei`, `subfinder`, `httpx`, etc.) which are natively optimized for and tested on Linux environments.

## Canonical Runtime

The officially supported, production-ready environment for BugHunter v1.0 is:

- **OS:** Ubuntu 24.04 LTS (Native)
- **Runtime:** Python 3.11+ Virtual Environment
- **Dependencies:** Go 1.21+ (for installing tools via `go install`), Docker (for Juice Shop testing)

## Windows Support Limitation

**Windows is NOT a supported environment for production scans.**

While BugHunter's internal Python engine is cross-platform and development/testing on Windows is supported, the external security binaries have inconsistent behavior on Windows. 

If you are developing or running BugHunter on Windows, you must use one of the following approaches:

### 1. Windows Subsystem for Linux (WSL2)
The recommended approach for Windows users is to use WSL2 with Ubuntu.

1. Install WSL2: `wsl --install`
2. Install Ubuntu 24.04 from the Microsoft Store.
3. Clone BugHunter inside the WSL filesystem (e.g., `~/bughunter`).
4. Follow the Ubuntu installation instructions.

### 2. Docker (Coming Soon)
We plan to provide a self-contained Docker image that runs the BugHunter agent along with all required security binaries.

## Environment Resolution
BugHunter utilizes a robust `ExecutableResolver` to locate dependencies. It searches standard `PATH` locations as well as common paths like `~/go/bin`. However, to prevent naming collisions (e.g., Python's `httpx` module vs. ProjectDiscovery's `httpx` binary), BugHunter explicitly validates binaries based on their expected CLI signatures before execution.
