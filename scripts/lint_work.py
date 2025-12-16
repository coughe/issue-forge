import sys, yaml

path = sys.argv[1]
fix = "--fix" in sys.argv
data = yaml.safe_load(open(path))

if fix:
    yaml.safe_dump(data, open(path, "w"), sort_keys=True)
    print("Normalized YAML")
else:
    print("Lint OK")
