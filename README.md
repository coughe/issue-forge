# IssueForge

> Repository: **issue-forge**

IssueForge is a JSON-first work compiler that turns structured intent into coordinated Jira work items and GitHub issues.

It enforces strict contracts for features, bugs, spikes, and tasks, creates linked artifacts across systems, and acts as a deliberate bridge between planning, execution, and agent-driven workflows.

IssueForge is intentionally boring: explicit inputs, deterministic outputs, no sync, and no background magic.

---

## Why IssueForge

Teams plan work in Jira, execute work in GitHub, and slowly lose alignment between the two.

IssueForge fixes this by:

- Treating work definition as code
- Compiling a single source of truth into multiple systems
- Enforcing discipline through validation instead of process docs
- Creating agent-friendly GitHub issues without weakening Jira rigor

One run. One snapshot. No drift.

---

## Phase 1 Behavior

- Jira issues always created
- GitHub issues created for **Epics (Features)** and **Bugs** only
- Explicit cross-linking
- No syncing, no webhooks, no UI

---

## Repository Layout

```
issue-forge/
├── README.md
├── schema/
│   └── work-graph.schema.json
└── scripts/
    ├── validate_work.py
    └── emit_phase1.py
```

---

## Installation

```bash
pip install jsonschema requests
```

---

## Usage

```bash
python scripts/validate_work.py work.json
python scripts/emit_phase1.py work.json
```

---

## Philosophy

IssueForge avoids:

- Implicit behavior
- Automatic syncing
- Long-running services
- UI-driven workflows

It favors:

- Explicit structure
- Deterministic output
- Human-readable artifacts
- Agent-friendly execution

---

## Roadmap (Not Implemented)

- YAML-based config
- --dry-run
- GitHub labels and agent hints
- Optional Jira → GitHub sync
- Minimal control-plane UI
