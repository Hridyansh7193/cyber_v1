# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-26

### Added
- Autonomous intelligence engine powered by LangGraph for security scan orchestration.
- Plugin capability matrix with support for drop-in tool replacements via dynamic capabilities (RECON, DNS, HTTP, SECRETS, VULN, etc).
- Checkpoint-safe deterministic state architecture across executions.
- `bughunter install` transactional installer for seamless dependency fetching and setup.
- Multi-stage Docker deployment configurations.
- Preflight validation blocking invalid scans before they trigger graph execution.
- Operational runtime reporting commands: `bughunter doctor`, `bughunter verify`, and `bughunter self-test`.
- Centralized workspace management for handling outputs and reports automatically.
- Scan profiles support: `minimal`, `bug_bounty`, `stealth`, and `full`.
- Strict semantic exit codes indicating success (0), runtime error (1), missing dependency (2), config issue (3), plugin failure (4), installation fail (5), preflight fail (6).

### Fixed
- Stabilized SQLite and Checkpoint storage architecture.
- Re-architected executing agents to guarantee deterministic outputs.

### Known limitations
- Deep API vulnerability scans (`graphql_wrapper`, `swagger_wrapper`) require high-quality specifications to avoid timeouts.
- Does not currently scan for binary exploitation vulnerabilities; web applications are the primary target context.
