# ADR-001: Plugin Routing and Eligibility

## Status
Accepted

## Context
Originally, plugins in BugHunter were executed based on hard-coded `if-else` blocks in `PluginExecutor`. This caused brittle coupling where `PluginExecutor` needed intimate knowledge of every plugin, preventing dynamic capability discovery and leading to issues where plugins like Swagger received thousands of unrelated HTML targets.

## Alternatives Considered
- **Regex Mapping in Config**: Allow users to define target-to-plugin regexes in the YAML config. (Rejected: places too much burden on the user and reduces out-of-the-box reliability).
- **Hardcoded Type Checking**: Checking `if target.endswith('.js')` inside the orchestrator. (Rejected: violates separation of concerns).

## Decision
We implemented explicit target eligibility contracts directly on the `PluginMetadata` via `target_eligibility` and an `is_candidate()` method on `BaseExecutionPlugin`.

## Consequences
- The planner and orchestrator are now fully decoupled from plugin-specific logic.
- Plugins act as independent agents defining their own intake parameters.
- Target misrouting is completely eliminated.
- Adding a new plugin requires zero changes to the orchestrator.
