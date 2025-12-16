import sys, json, yaml, pathlib
from jsonschema import validate

p = pathlib.Path(sys.argv[1])
data = yaml.safe_load(open(p)) if p.suffix in [".yaml", ".yml"] else json.load(open(p))
schema = json.load(open("schema/work-graph.schema.json"))
validate(instance=data, schema=schema)
print("Validation OK")
