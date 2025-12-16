class ExecutionContext:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.jira = []
        self.github = []

    def record_jira(self, payload):
        self.jira.append(payload)
        return "DRY-RUN-JIRA"

    def record_github(self, payload):
        self.github.append(payload)
        return "https://github.com/dry-run/issue"
