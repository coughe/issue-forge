import os

import requests


class ExecutionContext:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.jira = []
        self.github = []
        self.jira_base_url = os.getenv("JIRA_BASE_URL", "").rstrip("/")
        self.jira_email = os.getenv("JIRA_EMAIL", "")
        self.jira_api_token = os.getenv("JIRA_API_TOKEN", "")

    @staticmethod
    def _description_to_adf(text: str) -> dict:
        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": text}],
                }
            ],
        }

    def record_jira(self, payload):
        self.jira.append(payload)
        if self.dry_run:
            return "DRY-RUN-JIRA"

        if not (self.jira_base_url and self.jira_email and self.jira_api_token):
            raise SystemExit(
                "Missing Jira credentials: set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN"
            )

        issue_type = payload.get("type")
        summary = payload.get("summary")
        project_key = payload.get("project")
        parent_key = payload.get("parent")

        if not issue_type or not summary:
            raise SystemExit("Invalid Jira payload: missing required 'type' or 'summary'")

        if not project_key and not parent_key:
            raise SystemExit(
                "Invalid Jira payload: top-level issues must include a project key"
            )

        fields = {
            "issuetype": {"name": str(issue_type)},
            "summary": str(summary),
        }

        if project_key:
            fields["project"] = {"key": str(project_key)}
        if parent_key:
            fields["parent"] = {"key": str(parent_key)}

        description = payload.get("description")
        if isinstance(description, str) and description:
            fields["description"] = self._description_to_adf(description)

        labels = payload.get("labels")
        if isinstance(labels, list):
            fields["labels"] = labels

        url = f"{self.jira_base_url}/rest/api/3/issue"
        response = requests.post(
            url,
            auth=(self.jira_email, self.jira_api_token),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={"fields": fields},
            timeout=30,
        )

        if response.status_code >= 400:
            raise SystemExit(
                f"Jira create failed ({response.status_code}): {response.text.strip()}"
            )

        data = response.json()
        issue_key = data.get("key")
        if not issue_key:
            raise SystemExit("Jira create succeeded but no issue key was returned")

        return issue_key

    def record_github(self, payload):
        self.github.append(payload)
        return "https://github.com/dry-run/issue"
