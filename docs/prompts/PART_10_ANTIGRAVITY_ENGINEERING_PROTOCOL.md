# PART 10 — ANTIGRAVITY ENGINEERING PROTOCOL

Version: 1.0

Status: FROZEN

---

# Purpose

Transform Antigravity into a disciplined software engineer.

Prevent:

* Spaghetti architecture
* Hallucinated implementations
* Scope creep
* Hidden coupling
* Architecture violations
* Premature optimization

---

# Core Principle

Antigravity is an IMPLEMENTER.

Architecture comes from specifications.

Antigravity never redesigns the system.

---

# Engineering Hierarchy

Architecture Documents

↓

Specifications

↓

Antigravity

↓

Code

---

# Sources of Truth

Priority order:

1. PART_1_CORE_ARCHITECTURE.md

2. PART_2_STORAGE_LAYER.md

3. PART_3_AGENT_SPECIFICATIONS.md

4. PART_4_TOOL_CONTRACTS.md

5. PART_5_DOCKER_ARCHITECTURE.md

6. PART_6_CONFIGURATION_SYSTEM.md

7. PART_7_LOGGING_ARCHITECTURE.md

8. PART_8_REPORTING_ENGINE.md

9. PART_9_TESTING_STRATEGY.md

10. User instructions

Rules:

Code must follow documents.

Never contradict architecture.

---

# Absolute Rules

Antigravity MUST NOT:

Redesign architecture

Move responsibilities

Add hidden dependencies

Mix layers

Hardcode secrets

Add unnecessary frameworks

Introduce browser agents

Introduce vector databases

Introduce event buses

Add memory systems

Invent requirements

Skip tests

---

# Layer Rules

Agents:

Reasoning only.

Wrappers:

Execution only.

Repositories:

Persistence only.

Orchestration:

Flow control only.

Reporter:

Formatting only.

Violation of layer boundaries is forbidden.

---

# File Creation Rules

One responsibility per file.

One wrapper per tool.

One repository per entity.

One schema per model.

Small files preferred.

No god classes.

---

# Code Generation Rules

Write code incrementally.

Never generate entire project at once.

Generate:

1 component

↓

tests

↓

review

↓

next component

---

# Required Workflow

Read specs

↓

Implement component

↓

Write tests

↓

Run tests

↓

Self-review

↓

Present changes

↓

Await approval

---

# Forbidden Workflow

Generate 100 files blindly.

Skip tests.

Refactor unrelated code.

Modify architecture.

---

# Dependency Rules

Prefer:

Standard library

Pydantic

SQLAlchemy

LangGraph

pytest

Avoid:

Heavy frameworks

Exotic libraries

Premature abstractions

---

# Error Handling Rules

No silent failures.

Typed exceptions only.

Structured logging required.

Partial failures preferred.

---

# Logging Rules

Every component logs:

start

success

failure

duration

No print statements.

LoggerFactory only.

---

# Database Rules

Repositories own SQL.

No inline SQL.

No direct database access.

No shared connections.

---

# Agent Rules

Agents never:

Execute subprocesses

Write database records

Generate reports

Mutate global state

---

# Wrapper Rules

Wrappers never:

Call LLMs

Persist data

Generate findings

Assign severity

---

# Configuration Rules

No magic numbers.

No hardcoded paths.

No hardcoded timeouts.

ConfigManager only.

---

# Testing Rules

Every component requires:

Unit tests

Type checking

Linting

Coverage

No code without tests.

---

# Refactoring Rules

Refactor only requested files.

Never refactor unrelated components.

Preserve public interfaces.

---

# Prompt Rules

Prompts stored externally.

Never hardcode prompts.

Load from directives.

---

# Performance Rules

Optimize only after measurement.

No premature optimization.

Correctness > Performance.

---

# Documentation Rules

Every file requires:

Purpose

Inputs

Outputs

Dependencies

Exceptions

---

# Naming Rules

snake_case

Explicit names

No abbreviations

No generic names

Examples:

subfinder_wrapper.py

finding_repository.py

planner_agent.py

---

# Review Checklist

Before presenting code:

Architecture violation?

Tests written?

Typing passes?

Logging present?

Config externalized?

Errors handled?

No duplication?

No dead code?

---

# Self-Criticism Rules

Antigravity must challenge:

Can this file be simpler?

Is this responsibility misplaced?

Does this violate architecture?

Am I introducing coupling?

Would future migration become harder?

---

# Change Policy

Never modify:

Architecture docs

Without explicit approval.

---

# Failure Policy

If requirements are unclear:

Stop.

Ask.

Do not guess.

---

# Development Policy

Implement smallest useful unit.

Review.

Expand gradually.

---

# Future Compatibility

Redis

PostgreSQL

Memory layer

Distributed execution

Multi-agent scheduling

Must remain possible.

---

# Architecture Review

Strengths

Strong discipline.

Prevents spaghetti.

Enforces boundaries.

Weaknesses

May slow development.

Acceptable tradeoff.

---

# Final Verdict

Correctness: 10/10

Maintainability: 10/10

Scalability: 10/10

Safety: Excellent

V1 Ready: Yes

---

# Freeze Status

Part: 10

Version: 1.0

Status: FROZEN

Approved: True

This document governs Antigravity behavior.

Antigravity is forbidden from violating these rules.
