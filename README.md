# IssueForge

IssueForge is a lightweight work-definition compiler that turns **human-authored YAML** into validated Jira work items and GitHub issues.

Humans write YAML. Machines validate structure. Emitters stay deterministic.

---

## Design Goals

- Explicit, file-based inputs
- Deterministic execution
- No hidden side effects
- Safe dry-run previews
- Tooling-first, not process-first

IssueForge is intentionally opinion-light. It provides structure, not policy.

---

## Architecture

YAML (authoring)
→ yamllint (syntax & style)
→ in-memory model
→ schema validation
→ dry-run or emit
→ Jira / GitHub (optional)

---

## Python Environment (uv)

IssueForge uses **uv** for Python versioning, virtual environments, and dependency management.

Install `uv` once:

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

Restart your shell and confirm:

```bash
uv --version
```

---

## Project Setup

IssueForge uses **uv-native dependency groups** and does not require manual virtual
environment activation.

From the repository root:

```bash
uv python install 3.11
uv sync --group dev
```

This will:
- install Python 3.11 if needed
- create a virtual environment in `.venv`
- install runtime and development dependencies
- generate a deterministic `uv.lock`

---

## Running Commands

Use `uv run` to execute tools inside the environment:

```bash
uv run pytest
uv run black .
uv run yamllint sample/sample-workload.yaml
```

Manual activation is optional and not required for normal use.

---

## Dry Run Mode

When `--dry-run` is enabled:

- No Jira or GitHub API calls are made
- All validation still runs
- Issue payloads are constructed
- Output is printed for inspection

Dry-run is strongly recommended before first execution.

---

## Code Formatting

IssueForge uses **Black** for deterministic formatting.

```bash
uv run black .
```

CI enforces formatting using:

```bash
black --check .
```

---

## Running Tests

All tests mock external integrations.
No credentials or network access are required.

```bash
uv run pytest
```

---

## Credentials (Jira / GitHub)

IssueForge supports a safe `--dry-run` mode that requires no credentials.
When you later enable real Jira/GitHub emitters, you’ll typically provide credentials via environment variables.

An example template is provided in [.env.example](.env.example).

### Local setup using `.env`

Copy the template:

```bash
cp .env.example .env
```

Fill in values, then export them into your shell session.

Bash (macOS/Linux/Git Bash):

```bash
set -a
source .env
set +a
```

PowerShell:

```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^[A-Za-z_][A-Za-z0-9_]*=') {
        $k, $v = $_ -split '=', 2
        [Environment]::SetEnvironmentVariable($k, $v, 'Process')
    }
}
```

### GitHub token (PAT / fine-grained token)

You need a token that can create/update issues in the target repository.

Recommended (fine-grained token):
- Resource owner: your user or org
- Repository access: select the repo you’ll target
- Repository permissions:
    - **Issues**: Read and write
    - **Metadata**: Read

Classic PAT (legacy):
- Public repos: `public_repo`
- Private repos: `repo`

Set:
- `GITHUB_REPO=owner/repo`
- `GITHUB_TOKEN=...`

### Jira API token (Atlassian Cloud)

For Jira Cloud, you authenticate with your Atlassian email + an API token (not your password).

How to create a token:
- Go to Atlassian account settings → Security → API tokens
- Create a token and copy it once (store it in a password manager)

Your Jira user must also have Jira permissions in the target project (e.g., “Create issues” / “Edit issues”).

Set:
- `JIRA_BASE_URL=https://your-domain.atlassian.net`
- `JIRA_EMAIL=you@company.com`
- `JIRA_API_TOKEN=...`
- `JIRA_PROJECT_KEY=ABC` (commonly needed by emitters)

---

## Repository Layout

```
issue-forge/
├── README.md
├── pyproject.toml
├── uv.lock
├── .yamllint.yml
├── schema/
│   └── work-graph.schema.json
├── scripts/
│   ├── emit_phase1.py
│   ├── execution_context.py
│   ├── lint_work.py
│   └── validate_work.py
├── sample/
│   └── sample-workload.yaml
└── tests/
    └── test_dry_run.py
```

---

## Notes on Samples

Sample workload files are intentionally minimal and generic.
They demonstrate valid structure and nesting, not recommended workflows or
organizational practices.

Each workload file targets a single project.

---

## Philosophy

- Authoring should be human-friendly
- Validation should be strict
- Execution should be boring
- Surprises should be impossible
