import sys, yaml
from scripts.execution_context import ExecutionContext

dry_run = "--dry-run" in sys.argv
path = sys.argv[1]

work = yaml.safe_load(open(path))
ctx = ExecutionContext(dry_run=dry_run)

for epic in work["items"]:
    payload = {"type": "Epic", "summary": epic["summary"]}
    ctx.record_jira(payload)
    print(f"{'DRY RUN' if dry_run else 'CREATE'} Jira Epic: {epic['summary']}")

print("Done")
