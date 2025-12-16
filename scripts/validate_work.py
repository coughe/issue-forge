#!/usr/bin/env python3
import json, sys
from jsonschema import validate, ValidationError

BASE_LABEL = "Refinement-required"

def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)

schema = json.load(open("schema/work-graph.schema.json"))
work = json.load(open(sys.argv[1]))

try:
    validate(instance=work, schema=schema)
except ValidationError as e:
    fail(e.message)

for epic in work["items"]:
    for item in epic.get("children", []):
        t = item["type"]
        desc = item.get("description", "")
        subtasks = item.get("subtasks", [])

        labels = set(item.get("labels", []))
        labels.add(BASE_LABEL)
        item["labels"] = sorted(labels)

        if t == "Story" and "Scenario:" not in desc:
            fail(f"Story '{item['summary']}' missing Gherkin")

        if t == "Spike" and not subtasks:
            fail(f"Spike '{item['summary']}' missing artifact subtasks")

        if t == "Task" and not subtasks:
            fail(f"Task '{item['summary']}' missing checklist subtasks")

        if t == "Bug":
            if not subtasks:
                fail(f"Bug '{item['summary']}' missing regression subtask")
            if not any(st.get("blocks_parent") for st in subtasks):
                fail(f"Bug '{item['summary']}' regression subtask must block parent")

print("Validation OK")
