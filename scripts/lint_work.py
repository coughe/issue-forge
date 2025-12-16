#!/usr/bin/env python3
import sys, yaml, pathlib

def load(path):
    return yaml.safe_load(open(path))

def save(path, data):
    yaml.safe_dump(data, open(path, "w"), sort_keys=True)

if __name__ == "__main__":
    path = pathlib.Path(sys.argv[1])
    fix = "--fix" in sys.argv

    data = load(path)

    if fix:
        save(path, data)
        print(f"Normalized {path}")
    else:
        print("Lint OK (no changes made)")
