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

from nexus.config import (
    WORKSPACE, NEEDS_ACTION, PLANS, PENDING_APPROVAL, APPROVED, DONE, LOGS
)

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

    def __init__(self, vault_path: Path = WORKSPACE):
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
"""
        plan_path.write_text(content)
        return str(plan_path)

    def create_approval_request(self, action_type: str, parameters: Dict, reason: str) -> str:
        """Create an approval request file"""
        timestamp = datetime.now().isoformat()
        approval_filename = f"APPROVAL_{action_type}_{int(datetime.now().timestamp())}.md"
        approval_path = PENDING_APPROVAL / approval_filename

        content = f"""---
action_type: {action_type}
status: pending_approval
created: {timestamp}
reason: {reason}
---

# Approval Request

## Action: {action_type}

## Parameters

{json.dumps(parameters, indent=2)}

## Reason

{reason}

## Instructions

Move this file to `approved/` to approve, or `rejected/` to reject.
"""
        approval_path.write_text(content)
        return str(approval_path)

    def move_to_approved(self, file_path: str) -> str:
        """Move file from pending to approved"""
        src = Path(file_path)
        if not src.exists():
            return ""
        dst = APPROVED / src.name
        src.rename(dst)
        return str(dst)

    def move_to_rejected(self, file_path: str) -> str:
        """Move file from pending to rejected"""
        src = Path(file_path)
        if not src.exists():
            return ""
        rejected_dir = WORKSPACE / "rejected"
        rejected_dir.mkdir(parents=True, exist_ok=True)
        dst = rejected_dir / src.name
        src.rename(dst)
        return str(dst)

    def move_to_done(self, file_path: str, completion_notes: str = "") -> str:
        """Move file to done/archive"""
        src = Path(file_path)
        if not src.exists():
            return ""
        dst = DONE / src.name
        src.rename(dst)
        
        # Add completion notes
        if completion_notes:
            with open(dst, 'a') as f:
                f.write(f"\n\n## Completed\n\n{completion_notes}\n\nCompleted at: {datetime.now().isoformat()}\n")
        return str(dst)

    def update_dashboard(self, metrics: Dict):
        """Update dashboard with metrics"""
        dashboard_path = WORKSPACE / "dashboard.md"
        content = f"""# Nexus Dashboard

**Last Updated:** {datetime.now().isoformat()}

## Metrics

{json.dumps(metrics, indent=2)}

## Quick Stats

- **Pending Tasks:** {metrics.get('pending_tasks', 0)}
- **Pending Approvals:** {metrics.get('pending_approvals', 0)}
- **Completed Today:** {metrics.get('completed_today', 0)}
- **Activity:** {metrics.get('activity', 'No recent activity')}

## System Status

- **Workspace:** {WORKSPACE}
- **Last Sync:** {datetime.now().isoformat()}
"""
        dashboard_path.write_text(content)
        logger.info("Dashboard updated")
