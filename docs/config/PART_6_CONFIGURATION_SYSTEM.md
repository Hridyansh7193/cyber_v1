# PART 6 — CONFIGURATION SYSTEM

Version: 1.0

Status: FROZEN

---

# Purpose

Centralize all configurable behavior.

No hardcoded values.

Configuration should be environment independent.

---

# Principles

1. No magic numbers.

2. Environment-specific values belong in config.

3. Config files are read-only during execution.

4. Defaults must exist.

5. Secrets are never stored in YAML.

---

# Directory

config/

settings.yaml

models.yaml

tools.yaml

timeouts.yaml

reporting.yaml

---

# settings.yaml

Contains:

scan_depth

max_retries

max_concurrency

cache_size

log_level

---

# models.yaml

Contains:

planner_model

analyzer_model

reporter_model

temperature

max_tokens

timeouts

---

# tools.yaml

Contains:

tool paths

docker container names

enable flags

wordlists

tool arguments

---

# timeouts.yaml

Contains:

subfinder timeout

nuclei timeout

dalfox timeout

ffuf timeout

global timeout

---

# reporting.yaml

Contains:

report formats

confidence thresholds

severity mapping

output directories

---

# Environment Variables

Used for:

OPENAI_API_KEY

GOOGLE_API_KEY

ANTHROPIC_API_KEY

Never stored in repository.

---

# Validation

All config files validated using Pydantic.

Invalid configuration:

Abort startup.

---

# Access Rules

Agents never read YAML directly.

Wrappers never read YAML directly.

Only ConfigManager reads configs.

---

# ConfigManager Responsibilities

Load configs.

Validate configs.

Provide typed access.

Cache values.

---

# Future Compatibility

Vault

Redis config

Remote config

Secrets manager

---

# Architecture Review

Strengths

Centralized configuration.

Easy testing.

Environment independent.

Weaknesses

Multiple YAML files.

Acceptable for V1.

---

# Final Verdict

Correctness: 10/10

Maintainability: 10/10

Scalability: 10/10

V1 Ready: Yes

---

Freeze Status

Part: 6

Status: FROZEN
