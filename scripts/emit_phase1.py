import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

import json
import yaml
from scripts.execution_context import ExecutionContext


def _parse_cli_args(argv: list[str]) -> tuple[str, bool, str]:
    dry_run = False
    manifest_format = "yaml"
    workload_path: str | None = None

    index = 1
    while index < len(argv):
        arg = argv[index]

        if arg == "--dry-run":
            dry_run = True
            index += 1
            continue

        if arg == "--format":
            if index + 1 >= len(argv):
                raise SystemExit("Missing value for --format (expected 'yaml' or 'json')")
            manifest_format = argv[index + 1].strip().lower()
            index += 2
            continue

        if arg.startswith("--format="):
            manifest_format = arg.split("=", 1)[1].strip().lower()
            index += 1
            continue

        if arg.startswith("-"):
            raise SystemExit(f"Unknown option: {arg}")

        if workload_path is None:
            workload_path = arg
            index += 1
            continue

        raise SystemExit(f"Unexpected extra argument: {arg}")

    if workload_path is None:
        raise SystemExit("Missing workload path argument")

    if manifest_format not in {"yaml", "json"}:
        raise SystemExit("Invalid --format value (expected 'yaml' or 'json')")

    return workload_path, dry_run, manifest_format


def _normalize_yaml_for_indented_inline_mappings(yaml_text: str) -> str:
    # Only used as a fallback when PyYAML rejects input.
    # Converts lines like "<indent>- key: value" into:
    #   <indent>-
    #   <indent><4 spaces>key: value
    fixed_lines: list[str] = []
    for line in yaml_text.splitlines():
        stripped = line.lstrip(" ")
        if not stripped.startswith("- "):
            fixed_lines.append(line)
            continue

        after_dash = stripped[2:]
        colon_index = after_dash.find(":")
        if colon_index <= 0:
            fixed_lines.append(line)
            continue

        key = after_dash[:colon_index]
        rest = after_dash[colon_index + 1 :]
        if not key or any(ch.isspace() for ch in key):
            fixed_lines.append(line)
            continue

        indent = " " * (len(line) - len(stripped))
        fixed_lines.append(f"{indent}-")
        fixed_lines.append(f"{indent}    {key}:{rest}")

    return "\n".join(fixed_lines) + ("\n" if yaml_text.endswith("\n") else "")


def _load_workload(path: str, manifest_format: str = "yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    if manifest_format == "yaml":
        try:
            loaded = yaml.safe_load(raw)
        except Exception:
            try:
                loaded = yaml.safe_load(_normalize_yaml_for_indented_inline_mappings(raw))
            except Exception as exc:
                raise SystemExit(f"Failed to parse YAML manifest: {exc}") from exc
    elif manifest_format == "json":
        try:
            loaded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(
                f"Failed to parse JSON manifest: {exc.msg} (line {exc.lineno}, column {exc.colno})"
            ) from exc
    else:
        raise SystemExit("Invalid --format value (expected 'yaml' or 'json')")

    if not isinstance(loaded, dict):
        raise SystemExit("Workload must be a mapping at the top level")
    return loaded


def _emit_item(
    ctx: ExecutionContext,
    item: dict,
    *,
    dry_run: bool,
    parent_issue: str | None = None,
    project: str | None = None,
) -> None:
    item_type = item.get("type") or "Subtask"
    summary = item.get("summary", "")
    description = item.get("description")
    existing_issue = item.get("existing")

    issue_for_children = parent_issue
    if existing_issue:
        issue_for_children = str(existing_issue)
        print(
            f"{'DRY RUN' if dry_run else 'USE'} Existing Jira {issue_for_children}: {summary}"
        )
    else:
        payload = {"type": item_type, "summary": summary}
        if "labels" in item and isinstance(item.get("labels"), list):
            payload["labels"] = item["labels"]
        if project:
            payload["project"] = project
        if description is not None:
            payload["description"] = description
        if parent_issue:
            payload["parent"] = parent_issue
        created_issue = ctx.record_jira(payload)
        issue_for_children = created_issue or parent_issue
        print(f"{'DRY RUN' if dry_run else 'CREATE'} Jira {item_type}: {summary}")

    for child in item.get("children", []) or []:
        if isinstance(child, dict):
            _emit_item(
                ctx,
                child,
                dry_run=dry_run,
                parent_issue=issue_for_children,
                project=project,
            )

    for subtask in item.get("subtasks", []) or []:
        if isinstance(subtask, dict):
            _emit_item(
                ctx,
                subtask,
                dry_run=dry_run,
                parent_issue=issue_for_children,
                project=project,
            )


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    path, dry_run, manifest_format = _parse_cli_args(argv)

    work = _load_workload(path, manifest_format=manifest_format)
    project = work.get("project")
    if not isinstance(project, str) or not project.strip():
        raise SystemExit("Manifest must include a non-empty 'project' field")

    ctx = ExecutionContext(dry_run=dry_run)

    for item in work.get("items", []) or []:
        if isinstance(item, dict):
            _emit_item(ctx, item, dry_run=dry_run, project=project)

    print("Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
