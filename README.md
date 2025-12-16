# IssueForge

IssueForge is a lightweight work-definition compiler that turns **human-authored YAML** into validated Jira work items and GitHub issues.

Humans write YAML. Machines validate structure. Emitters stay deterministic.

---

## Design Goals

* Explicit, file-based inputs
* Deterministic execution
* No hidden side effects
* Safe dry-run previews
* Tooling-first, not process-first

IssueForge is intentionally opinion-light. It provides structure, not policy.

---

## Architecture

```
YAML (authoring)
  ↓
yamllint (syntax & style)
  ↓
YAML → in-memory model
  ↓
Schema validation
  ↓
Dry-run or emit
  ↓
Jira / GitHub (optional)
```

---

## Python Environment (uv)

IssueForge uses **uv** for Python and dependency management.

### Install uv (once)

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

Restart your shell and confirm:

```bash
uv --version
```

---

## Project Setup

From the repo root:

```bash
uv python install 3.11
uv venv
source .venv/bin/activate
uv pip install
```

All required tooling is installed by default, including:

* pytest
* black
* yamllint

---

## Quickstart

```bash
# Lint YAML (syntax & style only)
yamllint sample/sample-workload.yaml

# Validate structure
python scripts/validate_work.py sample/sample-workload.yaml

# Preview changes (no external calls)
python scripts/emit_phase1.py sample/sample-workload.yaml --dry-run

# Execute for real
python scripts/emit_phase1.py sample/sample-workload.yaml
```

---

## Dry Run Mode

IssueForge supports a **--dry-run** mode to safely preview changes.

When enabled:

* No Jira or GitHub API calls are made
* All validation still runs
* All issue payloads are constructed
* Output is printed for inspection

Dry-run is strongly recommended before first execution.

---

## Code Formatting

IssueForge uses **Black** to enforce deterministic Python formatting.

```bash
source .venv/bin/activate
black .
```

CI enforces formatting using `black --check .`.

---

## Running Tests

All tests use mocked integrations. No network access or credentials are required.

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
├── .github/
│   └── workflows/
│       └── lint.yml
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

## Notes on Samples

Sample workload files are intentionally minimal. They demonstrate valid shapes and nesting, not recommended workflows or organizational practices.

Each workload file targets a single project.

---

## Philosophy

* Authoring should be human-friendly
* Validation should be strict
* Execution should be boring
* Surprises should be impossible
