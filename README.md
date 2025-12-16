# IssueForge

IssueForge is a work-definition compiler that turns **human-authored YAML** into validated Jira work items and GitHub issues.

Humans write YAML. Machines validate JSON. Emitters stay deterministic.

---

## Architecture

```
YAML (authoring, commented)
  ↓
yamllint (style & syntax)
  ↓
YAML → JSON (normalization)
  ↓
JSON Schema validation
  ↓
Semantic validation
  ↓
Jira / GitHub emitters
```

---

## Installation (UV)

Install uv once:

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

Set up the project:

```bash
uv python install 3.11
uv venv
source .venv/bin/activate
uv pip install
```

---

## Quickstart

```bash
# Lint YAML
yamllint sample/sample-workload.yaml

# Optional: normalize YAML formatting
python scripts/lint_work.py sample/sample-workload.yaml --fix

# Validate structure + semantics
python scripts/validate_work.py sample/sample-workload.yaml

# Preview changes (no external calls)
python scripts/emit_phase1.py sample/sample-workload.yaml --dry-run

# Execute for real
python scripts/emit_phase1.py sample/sample-workload.yaml
```

---

## Dry Run Mode

When `--dry-run` is supplied:

- No Jira or GitHub API calls are made
- All validation still runs
- All issue payloads are constructed
- Output is printed for inspection

Dry-run is strongly recommended before first execution.

---

## Running Tests

All tests mock external integrations.

```bash
source .venv/bin/activate
pytest
```

---

## Repository Layout

```
issue-forge/
├── README.md
├── .yamllint.yml
├── pyproject.toml
├── uv.lock
├── schema/
│   └── work-graph.schema.json
├── scripts/
│   ├── execution_context.py
│   ├── lint_work.py
│   ├── validate_work.py
│   └── emit_phase1.py
├── sample/
│   └── sample-workload.yaml
└── tests/
    └── test_dry_run.py
```

---

## Philosophy

- Validation never mutates input
- Fixing is explicit and opt-in
- Execution is deterministic
- Drift is impossible unless bypassed
