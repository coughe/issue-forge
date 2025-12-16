#!/usr/bin/env python3
import json, os, requests
from requests.auth import HTTPBasicAuth

PROJECT_TO_REPO = {
    "AS": "arca-platforms/arca-software",
    "TI": "arca-platforms/time-integration"
}

BASE_LABEL = "Refinement-required"

def jira_headers():
    return {"Content-Type": "application/json"}

def gh_headers():
    return {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json"
    }

def create_jira(project, item, parent=None):
    payload = {
        "fields": {
            "project": {"key": project},
            "summary": item["summary"],
            "issuetype": {"name": item["type"]},
            "description": item.get("description", ""),
            "labels": list(set(item.get("labels", []) + [BASE_LABEL]))
        }
    }
    if parent:
        payload["fields"]["parent"] = {"key": parent}

    r = requests.post(
        f"{os.environ['JIRA_BASE_URL']}/rest/api/3/issue",
        headers=jira_headers(),
        auth=HTTPBasicAuth(os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"]),
        json=payload
    )
    r.raise_for_status()
    return r.json()["key"]

def create_github(repo, title, body):
    r = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers=gh_headers(),
        json={"title": title, "body": body}
    )
    r.raise_for_status()
    return r.json()["html_url"]

work = json.load(open(sys.argv[1]))
project = work["project"]

for epic in work["items"]:
    epic_key = create_jira(project, epic)

    if project in PROJECT_TO_REPO:
        create_github(
            PROJECT_TO_REPO[project],
            f"Feature: {epic['summary']}",
            f"Source Jira: {epic_key}"
        )

    for item in epic.get("children", []):
        key = create_jira(project, item, epic_key)

        if item["type"] == "Bug" and project in PROJECT_TO_REPO:
            create_github(
                PROJECT_TO_REPO[project],
                f"Bug: {item['summary']}",
                f"Source Jira: {key}"
            )

        for st in item.get("subtasks", []):
            create_jira(
                project,
                {"type": "Sub-task", "summary": st["summary"], "labels": item["labels"]},
                key
            )
