# IssueForge

> Repository: **issue-forge**

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

## Supported Inputs

- `.yaml` / `.yml` (recommended)
- `.json` (schema-validated directly)

---

## Installation

```bash
pip install jsonschema requests pyyaml yamllint
```

---

## Quickstart

```bash
# Lint (no mutation)
yamllint sample/sample-workload.yaml

# Lint + normalize (optional)
python scripts/lint_work.py sample/sample-workload.yaml --fix

# Validate structure + semantics
python scripts/validate_work.py sample/sample-workload.yaml

# Emit Jira + GitHub issues
python scripts/emit_phase1.py sample/sample-workload.yaml
```

---

## Validation Rules (Enforced)

- Epics may only contain children
- Stories must include Gherkin (`Scenario:`)
- Spikes require artifact subtasks
- Tasks require checklist subtasks
- Bugs require blocking regression subtasks
- Phases and milestones are forbidden
- All items get `Refinement-required`
- No auto-assignment

---

## Files

- `schema/work-graph.schema.json` – canonical schema
- `scripts/lint_work.py` – linter / normalizer
- `scripts/validate_work.py` – structural + semantic validation
- `scripts/emit_phase1.py` – Jira / GitHub emitters
- `.yamllint.yml` – YAML style rules
- `sample/sample-workload.yaml` – commented authoring example

---

## Philosophy

- Validation never mutates input
- Fixing is explicit and opt-in
- Execution is deterministic
- Drift is impossible unless you bypass the tool
