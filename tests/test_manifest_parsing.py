import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.emit_phase1 import _load_workload


def test_load_workload_yaml_path(tmp_path):
    workload_path = tmp_path / "work.yaml"
    workload_path.write_text(
        """
project: AS
items:
  - type: Story
    summary: YAML path
""".strip()
    )

    loaded = _load_workload(str(workload_path), manifest_format="yaml")

    assert loaded["project"] == "AS"
    assert loaded["items"][0]["summary"] == "YAML path"


def test_load_workload_json_path(tmp_path):
    workload_path = tmp_path / "work.json"
    workload_path.write_text(
        '{"project":"AS","items":[{"type":"Story","summary":"JSON path"}]}'
    )

    loaded = _load_workload(str(workload_path), manifest_format="json")

    assert loaded["project"] == "AS"
    assert loaded["items"][0]["summary"] == "JSON path"


def test_load_workload_invalid_json_has_helpful_error(tmp_path):
    workload_path = tmp_path / "invalid.json"
    workload_path.write_text('{"project":"AS",')

    with pytest.raises(SystemExit, match=r"Failed to parse JSON manifest:"):
        _load_workload(str(workload_path), manifest_format="json")
