import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

import sys, yaml
from scripts.execution_context import ExecutionContext

def _workload_path_from_argv(argv: list[str]) -> str:
    for arg in argv[1:]:
        if not arg.startswith("-"):
            return arg
    raise SystemExit("Missing workload path argument")


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


def _load_workload_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    try:
        loaded = yaml.safe_load(raw)
    except Exception:
        loaded = yaml.safe_load(_normalize_yaml_for_indented_inline_mappings(raw))
    if not isinstance(loaded, dict):
        raise SystemExit("Workload must be a mapping at the top level")
    return loaded


def _emit_item(ctx: ExecutionContext, item: dict, *, dry_run: bool) -> None:
    item_type = item.get("type") or "Subtask"
    summary = item.get("summary", "")
    payload = {"type": item_type, "summary": summary}
    ctx.record_jira(payload)
    print(f"{'DRY RUN' if dry_run else 'CREATE'} Jira {item_type}: {summary}")

    for child in item.get("children", []) or []:
        if isinstance(child, dict):
            _emit_item(ctx, child, dry_run=dry_run)

    for subtask in item.get("subtasks", []) or []:
        if isinstance(subtask, dict):
            _emit_item(ctx, subtask, dry_run=dry_run)


dry_run = "--dry-run" in sys.argv
path = _workload_path_from_argv(sys.argv)

work = _load_workload_yaml(path)
ctx = ExecutionContext(dry_run=dry_run)

for item in work.get("items", []) or []:
    if isinstance(item, dict):
        _emit_item(ctx, item, dry_run=dry_run)

print("Done")
