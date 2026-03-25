#!/usr/bin/env python3
"""
Claude Code Integration for AI Employee
Handles reading from and writing to the Obsidian vault
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
PLANS = VAULT_PATH / "Plans"
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
APPROVED = VAULT_PATH / "Approved"
DONE = VAULT_PATH / "Done"
LOGS = VAULT_PATH / "Logs"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS / "claude_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ClaudeIntegration")


class VaultManager:
    """Manages reading and writing to the Obsidian vault"""

    def __init__(self, vault_path: Path = VAULT_PATH):
        self.vault_path = vault_path
        self.ensure_structure()

    def ensure_structure(self):
        """Ensure all required folders exist"""
        folders = [
            NEEDS_ACTION, PLANS, PENDING_APPROVAL, APPROVED, DONE, LOGS
        ]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)

    def read_needs_action(self) -> List[Dict]:
        """Read all files from Needs_Action folder"""
        tasks = []
        if not NEEDS_ACTION.exists():
            return tasks

        for file_path in NEEDS_ACTION.glob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                tasks.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content,
                    "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                })
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")

        return sorted(tasks, key=lambda x: x['created_at'])

    def create_plan(self, task_name: str, objective: str, steps: List[str]) -> str:
        """Create a plan file for a task"""
        timestamp = datetime.now().isoformat()
        plan_filename = f"PLAN_{task_name}_{int(datetime.now().timestamp())}.md"
        plan_path = PLANS / plan_filename

        # Create checklist from steps
        steps_md = "\n".join([f"- [ ] {step}" for step in steps])

        content = f"""---
created: {timestamp}
status: pending
task_name: {task_name}
---

# Plan: {objective}

## Objective

{objective}

## Steps

{steps_md}

## Notes

Add any notes or observations here.

## Status

- Created: {timestamp}
- Last Updated: {timestamp}
- Completion: 0%
"""

        plan_path.write_text(content, encoding='utf-8')
        logger.info(f"Created plan: {plan_filename}")
        return str(plan_path)

    def create_approval_request(self, action_type: str, details: Dict, reason: str = "") -> str:
        """Create an approval request file"""
        timestamp = datetime.now().isoformat()
        approval_filename = f"{action_type.upper()}_{int(datetime.now().timestamp())}.md"
        approval_path = PENDING_APPROVAL / approval_filename

        # Format details as markdown table
        details_md = "\n".join([f"- **{k}:** {v}" for k, v in details.items()])

        content = f"""---
type: approval_request
action: {action_type}
created: {timestamp}
expires: {timestamp}
status: pending
---

# Approval Required: {action_type.title()}

## Action Details

{details_md}

## Reason

{reason if reason else "No reason provided"}

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder.

## Notes

Add any comments or questions here.
"""

        approval_path.write_text(content, encoding='utf-8')
        logger.info(f"Created approval request: {approval_filename}")
        return str(approval_path)

    def move_to_done(self, file_path: str, notes: str = "") -> bool:
        """Move a task file to Done folder"""
        try:
            source = Path(file_path)
            if not source.exists():
                logger.warning(f"File not found: {file_path}")
                return False

            dest = DONE / source.name
            source.rename(dest)

            # Add completion note
            if notes:
                content = dest.read_text(encoding='utf-8')
                content += f"\n\n## Completion Notes\n\n{notes}\n\n**Completed:** {datetime.now().isoformat()}"
                dest.write_text(content, encoding='utf-8')

            logger.info(f"Moved to Done: {source.name}")
            self._log_action("task_completed", {"file": source.name, "notes": notes})
            return True
        except Exception as e:
            logger.error(f"Error moving file to Done: {e}")
            return False

    def update_dashboard(self, updates: Dict) -> bool:
        """Update the Dashboard.md file"""
        try:
            dashboard_path = self.vault_path / "Dashboard.md"
            content = dashboard_path.read_text(encoding='utf-8')

            # Update last updated timestamp
            content = content.replace(
                "**Last Updated:**",
                f"**Last Updated:** {datetime.now().isoformat()}"
            )

            # Update metrics if provided
            if "pending_tasks" in updates:
                content = content.replace(
                    "| Tasks Pending | 0 |",
                    f"| Tasks Pending | {updates['pending_tasks']} |"
                )

            if "needs_action" in updates:
                content = content.replace(
                    "| Needs Action | 0 |",
                    f"| Needs Action | {updates['needs_action']} |"
                )

            if "completed_today" in updates:
                content = content.replace(
                    "| Tasks Completed Today | 0 |",
                    f"| Tasks Completed Today | {updates['completed_today']} |"
                )

            # Add recent activity
            if "activity" in updates:
                activity_line = f"- **[{datetime.now().strftime('%Y-%m-%d %H:%M')}]** {updates['activity']}"
                # Insert after "## 📋 Recent Activity"
                content = content.replace(
                    "## 📋 Recent Activity\n\n-",
                    f"## 📋 Recent Activity\n\n{activity_line}\n-"
                )

            dashboard_path.write_text(content, encoding='utf-8')
            logger.info("Dashboard updated")
            return True
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            return False

    def get_approved_actions(self) -> List[Dict]:
        """Get all approved actions waiting for execution"""
        actions = []
        if not APPROVED.exists():
            return actions

        for file_path in APPROVED.glob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                actions.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content
                })
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")

        return actions

    def _log_action(self, action_type: str, details: Dict):
        """Log an action to the daily log"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": "claude_integration",
            "details": details,
            "status": "success"
        }

        log_date = datetime.now().strftime("%Y-%m-%d")
        log_file = LOGS / f"{log_date}.json"

        try:
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(log_entry)

            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.error(f"Could not write log: {e}")


def main():
    """Main entry point for Claude Code integration"""
    logger.info("=" * 60)
    logger.info("Claude Code Integration Started")
    logger.info("=" * 60)

    vault = VaultManager()

    # Example: Read needs action
    tasks = vault.read_needs_action()
    logger.info(f"Found {len(tasks)} tasks in Needs_Action")

    for task in tasks:
        logger.info(f"Task: {task['filename']}")

    # Example: Create a plan
    if tasks:
        vault.create_plan(
            "example_task",
            "Process first task",
            [
                "Read task details",
                "Analyze requirements",
                "Create action plan",
                "Execute plan",
                "Log results"
            ]
        )

    # Example: Update dashboard
    vault.update_dashboard({
        "pending_tasks": len(tasks),
        "needs_action": len(tasks),
        "completed_today": 0,
        "activity": "Claude integration initialized"
    })

    logger.info("=" * 60)
    logger.info("Claude Code Integration Complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
