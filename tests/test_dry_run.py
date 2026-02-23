import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.emit_phase1 import _emit_item
from scripts.execution_context import ExecutionContext


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


def test_existing_items_are_not_created_but_parent_children():
    ctx = ExecutionContext(dry_run=True)

    item = {
        "type": "Epic",
        "summary": "Existing Epic",
        "existing": "ABC-123",
        "children": [
            {
                "type": "Story",
                "summary": "Created child",
                "subtasks": [{"summary": "Created subtask"}],
            },
            {
                "type": "Task",
                "summary": "Existing child",
                "existing": "ABC-456",
                "children": [{"type": "Bug", "summary": "Created grandchild"}],
            },
        ],
    }

    _emit_item(ctx, item, dry_run=True)

    assert len(ctx.jira) == 3

    created_child = next(
        payload for payload in ctx.jira if payload["summary"] == "Created child"
    )
    created_subtask = next(
        payload for payload in ctx.jira if payload["summary"] == "Created subtask"
    )
    created_grandchild = next(
        payload for payload in ctx.jira if payload["summary"] == "Created grandchild"
    )

    assert created_child["parent"] == "ABC-123"
    assert created_subtask["parent"] == "DRY-RUN-JIRA"
    assert created_grandchild["parent"] == "ABC-456"


def test_description_is_passed_through_in_dry_run_payload():
    ctx = ExecutionContext(dry_run=True)

    item = {
        "type": "Task",
        "summary": "Task with description",
        "description": "Detailed text for Jira description",
    }

    _emit_item(ctx, item, dry_run=True)

    assert len(ctx.jira) == 1
    assert ctx.jira[0]["description"] == "Detailed text for Jira description"


def test_labels_are_omitted_when_not_present_in_manifest_item():
    ctx = ExecutionContext(dry_run=True)

    item = {
        "type": "Epic",
        "summary": "Existing anchor",
        "existing": "ABC-123",
        "children": [{"type": "Task", "summary": "Created child"}],
    }

    _emit_item(ctx, item, dry_run=True)

    assert len(ctx.jira) == 1
    assert ctx.jira[0]["summary"] == "Created child"
    assert "labels" not in ctx.jira[0]


def test_labels_are_passed_through_from_manifest_item():
    ctx = ExecutionContext(dry_run=True)

    item = {
        "type": "Task",
        "summary": "Created child",
        "labels": ["backend", "priority-high"],
    }

    _emit_item(ctx, item, dry_run=True)

    assert len(ctx.jira) == 1
    assert ctx.jira[0]["summary"] == "Created child"
    assert ctx.jira[0]["labels"] == ["backend", "priority-high"]


def test_manifest_project_is_required_and_not_taken_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("JIRA_PROJECT_KEY", "ABC")

    workload = """
    items:
    - summary: Missing project
    """

    workload_path = tmp_path / "work.yaml"
    workload_path.write_text(workload)

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

    assert result.returncode != 0
    assert "Manifest must include a non-empty 'project' field" in result.stderr
