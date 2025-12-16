import subprocess
import sys
from pathlib import Path


def test_dry_run_emits_intent_without_side_effects(tmp_path):
    """
    Dry-run must:
    - Exit successfully
    - Produce human-readable output
    - Not require Jira/GitHub credentials
    - Not perform any external calls
    """

    # Minimal valid workload
    workload = """
    project: AS
    items:
    - type: Epic
        summary: Test Mode
        children:
        - type: Bug
            summary: Example bug
            subtasks:
            - summary: Regression test
                blocks_parent: true
    """

    workload_path = tmp_path / "work.yaml"
    workload_path.write_text(workload)

    # Run emit_phase1.py in dry-run mode
    result = subprocess.run(
        [
            sys.executable,
            "scripts/emit_phase1.py",
            str(workload_path),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parents[1],
    )

    # Process-level assertions
    assert result.returncode == 0, result.stderr

    stdout = result.stdout

    # Contract assertions
    assert "DRY RUN" in stdout
    assert "Test Mode" in stdout
    assert "Example bug" in stdout or "Bug" in stdout

    # Safety assertion: no accidental credential access
    assert "JIRA_" not in stdout
    assert "GITHUB_" not in stdout
