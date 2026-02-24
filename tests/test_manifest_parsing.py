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


def test_load_workload_top_level_issue_payload_is_rejected(tmp_path):
    workload_path = tmp_path / "single-issue.json"
    workload_path.write_text(
        '{"project":"AS","issue_type":"Spike","summary":"Investigate ClickHouse","description":"2-day spike","acceptance_criteria":["Run locally","Document findings"]}'
    )

    with pytest.raises(
        SystemExit, match=r"Manifest must include top-level 'items' list"
    ):
        _load_workload(str(workload_path), manifest_format="json")


def test_load_workload_items_must_be_list(tmp_path):
    workload_path = tmp_path / "bad-items.json"
    workload_path.write_text('{"project":"AS","items":{}}')

    with pytest.raises(SystemExit, match=r"Manifest field 'items' must be a list"):
        _load_workload(str(workload_path), manifest_format="json")
