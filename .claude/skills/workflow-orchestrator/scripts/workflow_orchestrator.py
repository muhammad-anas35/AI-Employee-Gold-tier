#!/usr/bin/env python3
"""
Workflow Orchestrator - Cross-domain workflow automation
Connects email, social media, accounting, and file systems
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from src.integration.claude_integration import VaultManager

# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent.parent.parent / "AI_Employee_Vault"
WORKFLOWS_DIR = Path(__file__).parent.parent / "workflows"

# Ensure directories exist
WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WorkflowOrchestrator")

# Workflow Templates
WORKFLOW_TEMPLATES = {
    "client_invoice": {
        "name": "Client Invoice Workflow",
        "description": "Email → Invoice → Notification",
        "trigger": "email_received",
        "steps": [
            {
                "action": "create_invoice",
                "domain": "odoo",
                "description": "Create invoice in Odoo"
            },
            {
                "action": "send_email",
                "domain": "gmail",
                "description": "Send invoice to client"
            },
            {
                "action": "post_update",
                "domain": "linkedin",
                "description": "Post business update"
            },
            {
                "action": "update_dashboard",
                "domain": "vault",
                "description": "Update dashboard metrics"
            }
        ]
    },
    "content_publish": {
        "name": "Content Publishing Workflow",
        "description": "File → Multi-platform posting",
        "trigger": "file_dropped",
        "steps": [
            {
                "action": "post_linkedin",
                "domain": "linkedin",
                "description": "Post to LinkedIn"
            },
            {
                "action": "post_twitter",
                "domain": "twitter",
                "description": "Post to Twitter"
            },
            {
                "action": "post_facebook",
                "domain": "facebook",
                "description": "Post to Facebook"
            },
            {
                "action": "send_notification",
                "domain": "gmail",
                "description": "Send email notification"
            },
            {
                "action": "update_dashboard",
                "domain": "vault",
                "description": "Update dashboard metrics"
            }
        ]
    },
    "payment_received": {
        "name": "Payment Received Workflow",
        "description": "Odoo → Email → Social",
        "trigger": "invoice_paid",
        "steps": [
            {
                "action": "send_thank_you",
                "domain": "gmail",
                "description": "Send thank you email"
            },
            {
                "action": "request_testimonial",
                "domain": "gmail",
                "description": "Request testimonial"
            },
            {
                "action": "update_dashboard",
                "domain": "vault",
                "description": "Update dashboard metrics"
            }
        ]
    },
    "weekly_report": {
        "name": "Weekly Report Distribution",
        "description": "Generate and distribute weekly report",
        "trigger": "scheduled_monday",
        "steps": [
            {
                "action": "generate_audit",
                "domain": "vault",
                "description": "Generate business audit"
            },
            {
                "action": "send_report",
                "domain": "gmail",
                "description": "Email report to stakeholders"
            },
            {
                "action": "post_summary",
                "domain": "linkedin",
                "description": "Post summary on LinkedIn"
            }
        ]
    }
}


class WorkflowOrchestrator:
    """Orchestrate cross-domain workflows"""

    def __init__(self):
        self.vault = VaultManager(VAULT_PATH)
        self.execution_log = []

    def execute_step(self, step: Dict, context: Dict) -> Dict:
        """Execute a single workflow step"""
        logger.info(f"Executing: {step['description']}")

        result = {
            "step": step["action"],
            "domain": step["domain"],
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Route to appropriate domain handler
            if step["domain"] == "odoo":
                result["status"] = "success"
                result["message"] = "Invoice created (simulated)"

            elif step["domain"] == "gmail":
                result["status"] = "approval_required"
                result["message"] = "Email draft created, awaiting approval"

            elif step["domain"] == "linkedin":
                result["status"] = "approval_required"
                result["message"] = "LinkedIn post draft created, awaiting approval"

            elif step["domain"] == "twitter":
                result["status"] = "approval_required"
                result["message"] = "Twitter post draft created, awaiting approval"

            elif step["domain"] == "facebook":
                result["status"] = "approval_required"
                result["message"] = "Facebook post draft created, awaiting approval"

            elif step["domain"] == "vault":
                result["status"] = "success"
                result["message"] = "Dashboard updated"

            else:
                result["status"] = "error"
                result["message"] = f"Unknown domain: {step['domain']}"

            logger.info(f"  → {result['status']}: {result['message']}")

        except Exception as e:
            result["status"] = "error"
            result["message"] = str(e)
            logger.error(f"  → Error: {e}")

        self.execution_log.append(result)
        return result

    def execute_workflow(self, workflow_name: str, context: Dict = None) -> Dict:
        """Execute a complete workflow"""
        if workflow_name not in WORKFLOW_TEMPLATES:
            logger.error(f"Unknown workflow: {workflow_name}")
            return {"status": "error", "message": "Unknown workflow"}

        workflow = WORKFLOW_TEMPLATES[workflow_name]
        context = context or {}

        logger.info("=" * 60)
        logger.info(f"Executing Workflow: {workflow['name']}")
        logger.info(f"Description: {workflow['description']}")
        logger.info("=" * 60)

        results = {
            "workflow": workflow_name,
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "status": "in_progress"
        }

        # Execute each step
        for i, step in enumerate(workflow["steps"], 1):
            logger.info(f"\nStep {i}/{len(workflow['steps'])}: {step['description']}")

            step_result = self.execute_step(step, context)
            results["steps"].append(step_result)

            # Stop on error
            if step_result["status"] == "error":
                results["status"] = "failed"
                logger.error(f"Workflow failed at step {i}")
                break

        # Determine final status
        if results["status"] != "failed":
            approval_count = sum(1 for s in results["steps"] if s["status"] == "approval_required")
            success_count = sum(1 for s in results["steps"] if s["status"] == "success")

            if approval_count > 0:
                results["status"] = "awaiting_approval"
            elif success_count == len(workflow["steps"]):
                results["status"] = "completed"

        results["completed_at"] = datetime.now().isoformat()

        # Save execution log
        self.save_execution_log(results)

        # Update dashboard
        self.vault.update_dashboard({
            "last_workflow": workflow_name,
            "workflow_status": results["status"],
            "workflow_time": results["completed_at"]
        })

        logger.info("\n" + "=" * 60)
        logger.info(f"Workflow Status: {results['status']}")
        logger.info("=" * 60)

        return results

    def save_execution_log(self, results: Dict):
        """Save workflow execution log"""
        log_file = WORKFLOWS_DIR / f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        logger.info(f"\nExecution log saved: {log_file}")

    def list_workflows(self):
        """List available workflow templates"""
        logger.info("\nAvailable Workflows:")
        logger.info("=" * 60)

        for name, workflow in WORKFLOW_TEMPLATES.items():
            logger.info(f"\n{name}:")
            logger.info(f"  Name: {workflow['name']}")
            logger.info(f"  Description: {workflow['description']}")
            logger.info(f"  Steps: {len(workflow['steps'])}")
            logger.info(f"  Trigger: {workflow['trigger']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Workflow Orchestrator")
    parser.add_argument('--workflow', type=str, help='Workflow name to execute')
    parser.add_argument('--list', action='store_true', help='List available workflows')

    args = parser.parse_args()

    orchestrator = WorkflowOrchestrator()

    if args.list:
        orchestrator.list_workflows()
    elif args.workflow:
        results = orchestrator.execute_workflow(args.workflow)
        print(f"\n[{results['status'].upper()}] Workflow execution complete")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
