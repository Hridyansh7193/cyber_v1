# Plugin Acceptance Criteria

Before a new wrapper plugin can be merged into BugHunter, it must satisfy all of the following requirements. This ensures we never ship a "half-integrated" plugin.

## Acceptance Checklist

- [ ] **Binary Detection**: The plugin successfully identifies its required binary via `shutil.which`.
- [ ] **Version Detection**: The plugin successfully captures the installed version of the binary.
- [ ] **Self Test**: `plugin.self_test()` verifies binary, parser, routing, and execution gracefully.
- [ ] **Capability Declaration**: Explicitly defines `accepts()`, `produces()`, `requires()`, etc. in `PluginMetadata`.
- [ ] **Routing Declaration**: Explicitly implements `is_candidate()` to prevent invalid targets.
- [ ] **Parser Tests**: Has unit tests covering both valid outputs and error scenarios.
- [ ] **Metadata Tests**: Verifies `build_metadata()` maps to the correct `ExecutionState` keys.
- [ ] **Live Validation**: Passes end-to-end live testing against real targets.
- [ ] **Evidence Support**: Fully supports storing raw inputs and outputs to the `workspace/` evidence directory.
- [ ] **Documentation**: The plugin configuration and capabilities are documented in the Plugin Reference.
- [ ] **Doctor Integration**: Properly integrated into `bughunter doctor`.
