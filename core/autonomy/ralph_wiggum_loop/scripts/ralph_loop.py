#!/usr/bin/env python3
"""
Ralph Wiggum Loop - Autonomous Task Completion
The heart of Gold tier autonomy - continuously processes tasks without human intervention
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.integration.claude_integration import VaultManager

# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent / "workspace"
NEEDS_ACTION = VAULT_PATH / "inbox"
APPROVED = VAULT_PATH / "approved"
PENDING_APPROVAL = VAULT_PATH / "pending"
DONE = VAULT_PATH / "archive"
LOGS = VAULT_PATH / "logs"

# Ensure directories exist
for directory in [NEEDS_ACTION, APPROVED, PENDING_APPROVAL, DONE, LOGS]:
    directory.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS / "ralph_loop.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RalphWiggumLoop")

# Configuration
CONFIG = {
    "interval_minutes": 10,
    "max_actions_per_cycle": 10,
    "auto_approve_safe_actions": True,
    "enable_self_healing": True,
    "max_retries": 3,
    "safe_actions": [
        "read_email",
        "create_draft",
        "organize_files",
        "update_dashboard",
        "generate_report",
        "create_invoice_draft"
    ],
    "sensitive_actions": [
        "send_email",
        "post_social_media",
        "make_payment",
        "delete_file",
        "finalize_invoice"
    ]
}

class RalphWiggumLoop:
    """Autonomous task completion loop"""

    def __init__(self):
        self.vault = VaultManager(VAULT_PATH)
        self.stats = {
            "cycles": 0,
            "tasks_processed": 0,
            "auto_executed": 0,
            "approval_requested": 0,
            "errors": 0
        }

    def is_safe_action(self, task_content: str) -> bool:
        """Determine if task is safe to auto-execute"""
        task_lower = task_content.lower()

        # Check for safe action keywords
        for safe_action in CONFIG["safe_actions"]:
            if safe_action.replace("_", " ") in task_lower:
                return True

        # Check for sensitive action keywords
        for sensitive_action in CONFIG["sensitive_actions"]:
            if sensitive_action.replace("_", " ") in task_lower:
                return False

        # Default to requiring approval for unknown actions
        return False

    def analyze_task(self, task_file: Path) -> Dict:
        """Analyze task and determine action"""
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract task type and details
            task_type = "unknown"
            if "EMAIL" in task_file.name:
                task_type = "email"
            elif "FILE" in task_file.name:
                task_type = "file"
            elif "WHATSAPP" in task_file.name:
                task_type = "whatsapp"

            is_safe = self.is_safe_action(content)

            return {
                "file": task_file,
                "type": task_type,
                "content": content,
                "is_safe": is_safe,
                "requires_approval": not is_safe
            }

        except Exception as e:
            logger.error(f"Error analyzing task {task_file}: {e}")
            return None

    def execute_safe_action(self, task: Dict) -> bool:
        """Execute a safe action automatically"""
        try:
            logger.info(f"Auto-executing safe action: {task['file'].name}")

            # Simulate action execution
            # In real implementation, this would call appropriate handlers
            task_type = task['type']

            if task_type == "email":
                logger.info("  → Reading email and creating draft response")
            elif task_type == "file":
                logger.info("  → Organizing file")
            else:
                logger.info(f"  → Processing {task_type} task")

            # Move to Done
            done_path = DONE / task['file'].name
            task['file'].rename(done_path)

            # Add completion note
            with open(done_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## Auto-Executed by Ralph Wiggum Loop\n\n")
                f.write(f"**Executed at:** {datetime.now().isoformat()}\n")
                f.write(f"**Status:** Completed automatically\n")

            self.stats["auto_executed"] += 1
            logger.info(f"  ✓ Completed and moved to Done")
            return True

        except Exception as e:
            logger.error(f"Error executing action: {e}")
            self.stats["errors"] += 1
            return False

    def request_approval(self, task: Dict) -> bool:
        """Create approval request for sensitive action"""
        try:
            logger.info(f"Requesting approval for: {task['file'].name}")

            # Move to Pending_Approval
            approval_path = PENDING_APPROVAL / task['file'].name
            task['file'].rename(approval_path)

            # Add approval note
            with open(approval_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## Approval Required\n\n")
                f.write(f"**Requested at:** {datetime.now().isoformat()}\n")
                f.write(f"**Reason:** Sensitive action detected\n")
                f.write(f"**Instructions:**\n")
                f.write(f"1. Review the action above\n")
                f.write(f"2. If approved, move to: `Approved/`\n")
                f.write(f"3. If rejected, move to: `Rejected/`\n")

            self.stats["approval_requested"] += 1
            logger.info(f"  → Moved to Pending_Approval")
            return True

        except Exception as e:
            logger.error(f"Error requesting approval: {e}")
            self.stats["errors"] += 1
            return False

    def process_approved_actions(self):
        """Execute approved actions"""
        approved_files = list(APPROVED.glob("*.md"))

        if not approved_files:
            return

        logger.info(f"Processing {len(approved_files)} approved action(s)")

        for approved_file in approved_files:
            try:
                logger.info(f"Executing approved action: {approved_file.name}")

                # Execute the approved action
                # In real implementation, this would call appropriate handlers

                # Move to Done
                done_path = DONE / approved_file.name
                approved_file.rename(done_path)

                # Add completion note
                with open(done_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n## Executed After Approval\n\n")
                    f.write(f"**Executed at:** {datetime.now().isoformat()}\n")
                    f.write(f"**Status:** Completed after human approval\n")

                logger.info(f"  ✓ Completed and moved to Done")

            except Exception as e:
                logger.error(f"Error executing approved action: {e}")
                self.stats["errors"] += 1

    def run_cycle(self):
        """Run one cycle of the loop"""
        self.stats["cycles"] += 1
        logger.info("=" * 60)
        logger.info(f"Ralph Wiggum Loop - Cycle #{self.stats['cycles']}")
        logger.info("=" * 60)

        # Step 1: Process tasks in Needs_Action
        task_files = list(NEEDS_ACTION.glob("*.md"))
        logger.info(f"Found {len(task_files)} task(s) in Needs_Action")

        if task_files:
            # Limit to max actions per cycle
            task_files = task_files[:CONFIG["max_actions_per_cycle"]]

            for task_file in task_files:
                self.stats["tasks_processed"] += 1

                # Analyze task
                task = self.analyze_task(task_file)
                if not task:
                    continue

                # Execute or request approval
                if task["is_safe"] and CONFIG["auto_approve_safe_actions"]:
                    self.execute_safe_action(task)
                else:
                    self.request_approval(task)

        # Step 2: Process approved actions
        self.process_approved_actions()

        # Step 3: Update dashboard
        try:
            self.vault.update_dashboard({
                "ralph_cycles": self.stats["cycles"],
                "tasks_processed": self.stats["tasks_processed"],
                "auto_executed": self.stats["auto_executed"],
                "approval_requested": self.stats["approval_requested"],
                "last_run": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")

        # Print stats
        logger.info("")
        logger.info("Cycle Statistics:")
        logger.info(f"  Total Cycles: {self.stats['cycles']}")
        logger.info(f"  Tasks Processed: {self.stats['tasks_processed']}")
        logger.info(f"  Auto-Executed: {self.stats['auto_executed']}")
        logger.info(f"  Approval Requested: {self.stats['approval_requested']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info("")

def main():
    """Run one cycle - designed to work with /loop command"""
    loop = RalphWiggumLoop()
    loop.run_cycle()

if __name__ == "__main__":
    main()
