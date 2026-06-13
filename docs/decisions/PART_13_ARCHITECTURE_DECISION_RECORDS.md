# PART 13 — ARCHITECTURE DECISION RECORDS (ADRs)

Version: 1.0

Status: FROZEN

---

# Purpose

Capture the rationale behind architectural decisions.

Goals:

* Prevent architectural drift.
* Preserve maintainability.
* Explain tradeoffs.
* Support future evolution.
* Enable disciplined change.

---

# ADR-001 — Three-Layer Architecture

Decision

Use:

Directives

↓

Orchestration

↓

Execution

Reason

Strong separation of concerns.

Consequences

Higher maintainability.

Status

Accepted

---

# ADR-002 — LangGraph Orchestration

Decision

Use LangGraph.

Reason

State-based workflows and retries.

Alternatives

Custom state machine.

Status

Accepted

---

# ADR-003 — Python 3.12

Decision

Python-only implementation.

Reason

Security tooling ecosystem.

Alternatives

Go

Rust

Status

Accepted

---

# ADR-004 — SQLite for V1

Decision

SQLite initially.

Reason

Simple deployment.

Alternatives

PostgreSQL

Status

Accepted

Migration Path

PostgreSQL in V2.

---

# ADR-005 — Dockerized Execution

Decision

Execute tools inside containers.

Reason

Isolation and reproducibility.

Status

Accepted

---

# ADR-006 — CLI-only V1

Decision

No UI.

Reason

Focus on functionality.

Alternatives

Web dashboard

Desktop app

Status

Accepted

---

# ADR-007 — No Browser Agents in V1

Decision

No Selenium or Playwright.

Reason

Avoid complexity.

Status

Accepted

Future

Optional V3.

---

# ADR-008 — Agents Are Reasoning Only

Decision

Agents never execute subprocesses.

Reason

Testability and separation.

Status

Accepted

---

# ADR-009 — Wrappers Are Deterministic

Decision

Wrappers contain no AI.

Reason

Reliability.

Status

Accepted

---

# ADR-010 — Repositories Own Persistence

Decision

No SQL outside repositories.

Reason

Maintainability.

Status

Accepted

---

# ADR-011 — Prompts Live Outside Code

Decision

External prompt files.

Reason

Easy iteration.

Status

Accepted

---

# ADR-012 — Partial Failures Allowed

Decision

Pipeline continues after failures.

Reason

Resilience.

Status

Accepted

---

# ADR-013 — No Vector Database in V1

Decision

Avoid vector databases.

Reason

Unnecessary complexity.

Status

Accepted

Future

Possible V3.

---

# ADR-014 — No Fine-Tuning

Decision

Use prompting only.

Reason

Faster iteration.

Status

Accepted

---

# ADR-015 — Tests Are Mandatory

Decision

No code without tests.

Reason

Prevent regressions.

Status

Accepted

---

# ADR-016 — Architecture Changes Require ADR Updates

Decision

Architecture modifications require ADR changes.

Reason

Prevent silent drift.

Status

Accepted

---

# ADR-017 — No Global Mutable State

Decision

State flows through ExecutionState only.

Reason

Predictability.

Status

Accepted

---

# ADR-018 — One Responsibility Per File

Decision

Avoid god classes.

Reason

Maintainability.

Status

Accepted

---

# ADR-019 — ConfigManager Owns Configuration

Decision

No direct YAML access.

Reason

Centralization.

Status

Accepted

---

# ADR-020 — LoggerFactory Owns Logging

Decision

No print statements.

Reason

Structured observability.

Status

Accepted

---

# ADR-021 — Bottom-Up Development

Decision

Implement:

Schemas

↓

Storage

↓

Wrappers

↓

Agents

↓

Orchestration

Reason

Minimize rework.

Status

Accepted

---

# ADR-022 — No Hidden State

Decision

State transitions are explicit.

Reason

Debuggability.

Status

Accepted

---

# ADR-023 — Correctness Before Performance

Decision

Optimize after measurement.

Reason

Avoid premature optimization.

Status

Accepted

---

# ADR-024 — Human Approval Required

Decision

Human reviews findings.

Reason

Avoid false positives.

Status

Accepted

---

# ADR-025 — No Autonomous Exploitation

Decision

Detection and reporting only.

Reason

Safety and reliability.

Status

Accepted

---

# Architecture Change Process

Proposal

↓

Review

↓

ADR Update

↓

Approval

↓

Implementation

No exceptions.

---

# Architecture Review

Strengths

Captures rationale.

Prevents drift.

Supports future evolution.

Weaknesses

Adds process overhead.

Acceptable tradeoff.

---

# Final Verdict

Correctness: 10/10

Maintainability: 10/10

Governance: Excellent

Architecture Drift Resistance: Excellent

V1 Ready: Yes

---

# Freeze Status

Part: 13

Version: 1.0

Status: FROZEN

Approved: True

This document is the constitution of BugHunter-Agent.

Any architecture change must first update these ADRs.
