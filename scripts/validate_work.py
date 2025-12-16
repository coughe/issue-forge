#!/usr/bin/env python3
import json, sys, yaml, pathlib
from jsonschema import validate

def load(path):
    p = pathlib.Path(path)
    if p.suffix in [".yaml", ".yml"]:
        return yaml.safe_load(open(p))
    return json.load(open(p))

work = load(sys.argv[1])
schema = json.load(open("schema/work-graph.schema.json"))
validate(instance=work, schema=schema)
print("Validation OK")
