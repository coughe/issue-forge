import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.execution_context import ExecutionContext


def test_record_jira_dry_run_returns_placeholder():
    ctx = ExecutionContext(dry_run=True)

    issue_key = ctx.record_jira(
        {
            "project": "AS",
            "type": "Story",
            "summary": "Dry-run item",
        }
    )

    assert issue_key == "DRY-RUN-JIRA"


def test_record_jira_live_posts_to_jira(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token-123")

    captured = {}

    class FakeResponse:
        status_code = 201
        text = ""

        @staticmethod
        def json():
            return {"key": "AS-999"}

    def fake_post(url, auth, headers, json, timeout):
        captured["url"] = url
        captured["auth"] = auth
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("scripts.execution_context.requests.post", fake_post)

    ctx = ExecutionContext(dry_run=False)
    issue_key = ctx.record_jira(
        {
            "project": "AS",
            "type": "Story",
            "summary": "Live item",
            "description": "Hello Jira",
            "labels": ["Idea"],
            "parent": "AS-211",
        }
    )

    assert issue_key == "AS-999"
    assert captured["url"] == "https://example.atlassian.net/rest/api/3/issue"
    assert captured["auth"] == ("user@example.com", "token-123")
    assert captured["timeout"] == 30
    assert captured["json"]["fields"]["project"]["key"] == "AS"
    assert captured["json"]["fields"]["issuetype"]["name"] == "Story"
    assert captured["json"]["fields"]["summary"] == "Live item"
    assert captured["json"]["fields"]["parent"]["key"] == "AS-211"
    assert captured["json"]["fields"]["description"]["type"] == "doc"


def test_record_jira_live_requires_credentials(monkeypatch):
    monkeypatch.delenv("JIRA_BASE_URL", raising=False)
    monkeypatch.delenv("JIRA_EMAIL", raising=False)
    monkeypatch.delenv("JIRA_API_TOKEN", raising=False)

    ctx = ExecutionContext(dry_run=False)

    with pytest.raises(SystemExit, match=r"Missing Jira credentials"):
        ctx.record_jira(
            {
                "project": "AS",
                "type": "Story",
                "summary": "Missing creds",
            }
        )
