# BugHunter Coding Standards

All code contributed to BugHunter must adhere to the following standards.

## 1. Static Analysis & Formatting
- **Ruff**: Code must be 100% Ruff clean. No `noqa` suppressions without documented justification.
- **Black**: All files must be formatted with Black.
- **Mypy**: Strict type hinting is required. Functions must define return types and argument types.

## 2. Pydantic Validation
- All state objects, configurations, and schemas must inherit from Pydantic `BaseModel`.
- Mutating state outside of Pydantic constraints is forbidden.
- No mutable defaults in dataclasses or Pydantic models.

## 3. Logging & Output
- **No `print()` statements**. All output must flow through the structured logger (`utils.logger.get_logger()`).
- CLI outputs should use the `rich` library for consistent formatting.

## 4. Testing
- Every wrapper must have a dedicated test for `parse()` and `build_metadata()`.
- Every parser must have a fixture for both successful execution and corrupted JSON output.
