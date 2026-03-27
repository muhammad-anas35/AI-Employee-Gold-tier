#!/usr/bin/env python3
"""
Audit Logger - Comprehensive audit trail for all AI Employee actions
Provides compliance-ready logging with structured data
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class AuditEventType(Enum):
    """Types of audit events"""
    EMAIL_SENT = "email_sent"
    EMAIL_RECEIVED = "email_received"
    FILE_PROCESSED = "file_processed"
    INVOICE_CREATED = "invoice_created"
    SOCIAL_POST = "social_post"
    TASK_EXECUTED = "task_executed"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    ERROR_OCCURRED = "error_occurred"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"


class AuditLogger:
    """Comprehensive audit logging system"""

    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup Python logger
        self.logger = logging.getLogger("AuditLogger")
        self.logger.setLevel(logging.INFO)

    def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        details: Dict[str, Any],
        user: Optional[str] = None,
        status: str = "success",
        metadata: Optional[Dict] = None
    ):
        """
        Log an audit event

        Args:
            event_type: Type of event (from AuditEventType enum)
            action: Description of action taken
            details: Detailed information about the event
            user: User or system that triggered the event
            status: Status of the event (success, failure, pending)
            metadata: Additional metadata
        """
        timestamp = datetime.now()

        # Create audit entry
        audit_entry = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type.value,
            "action": action,
            "status": status,
            "user": user or "system",
            "details": details,
            "metadata": metadata or {}
        }

        # Write to daily log file
        log_file = self.log_dir / f"{timestamp.strftime('%Y-%m-%d')}.json"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry) + "\n")

        # Also log to Python logger
        self.logger.info(
            f"[{event_type.value}] {action} - Status: {status}"
        )

    def log_email_sent(self, to: str, subject: str, approved_by: Optional[str] = None):
        """Log email sent event"""
        self.log_event(
            event_type=AuditEventType.EMAIL_SENT,
            action=f"Email sent to {to}",
            details={
                "recipient": to,
                "subject": subject,
                "approved_by": approved_by
            }
        )

    def log_email_received(self, from_addr: str, subject: str):
        """Log email received event"""
        self.log_event(
            event_type=AuditEventType.EMAIL_RECEIVED,
            action=f"Email received from {from_addr}",
            details={
                "sender": from_addr,
                "subject": subject
            }
        )

    def log_file_processed(self, file_path: str, action: str):
        """Log file processing event"""
        self.log_event(
            event_type=AuditEventType.FILE_PROCESSED,
            action=f"File processed: {action}",
            details={
                "file_path": file_path,
                "action": action
            }
        )

    def log_invoice_created(self, invoice_id: str, amount: float, customer: str):
        """Log invoice creation event"""
        self.log_event(
            event_type=AuditEventType.INVOICE_CREATED,
            action=f"Invoice created for {customer}",
            details={
                "invoice_id": invoice_id,
                "amount": amount,
                "customer": customer
            }
        )

    def log_social_post(self, platform: str, content: str, approved_by: Optional[str] = None):
        """Log social media post event"""
        self.log_event(
            event_type=AuditEventType.SOCIAL_POST,
            action=f"Posted to {platform}",
            details={
                "platform": platform,
                "content": content[:100],  # First 100 chars
                "approved_by": approved_by
            }
        )

    def log_task_executed(self, task_name: str, auto_executed: bool):
        """Log task execution event"""
        self.log_event(
            event_type=AuditEventType.TASK_EXECUTED,
            action=f"Task executed: {task_name}",
            details={
                "task_name": task_name,
                "auto_executed": auto_executed
            }
        )

    def log_approval_requested(self, action: str, reason: str):
        """Log approval request event"""
        self.log_event(
            event_type=AuditEventType.APPROVAL_REQUESTED,
            action=f"Approval requested: {action}",
            details={
                "action": action,
                "reason": reason
            },
            status="pending"
        )

    def log_approval_granted(self, action: str, approved_by: str):
        """Log approval granted event"""
        self.log_event(
            event_type=AuditEventType.APPROVAL_GRANTED,
            action=f"Approval granted: {action}",
            details={
                "action": action,
                "approved_by": approved_by
            }
        )

    def log_approval_denied(self, action: str, denied_by: str, reason: str):
        """Log approval denied event"""
        self.log_event(
            event_type=AuditEventType.APPROVAL_DENIED,
            action=f"Approval denied: {action}",
            details={
                "action": action,
                "denied_by": denied_by,
                "reason": reason
            }
        )

    def log_error(self, error_type: str, error_message: str, context: Dict):
        """Log error event"""
        self.log_event(
            event_type=AuditEventType.ERROR_OCCURRED,
            action=f"Error: {error_type}",
            details={
                "error_type": error_type,
                "error_message": error_message,
                "context": context
            },
            status="failure"
        )

    def log_workflow(self, workflow_name: str, status: str, steps: int):
        """Log workflow event"""
        event_type = (
            AuditEventType.WORKFLOW_STARTED if status == "started"
            else AuditEventType.WORKFLOW_COMPLETED
        )

        self.log_event(
            event_type=event_type,
            action=f"Workflow {status}: {workflow_name}",
            details={
                "workflow_name": workflow_name,
                "steps": steps
            },
            status=status
        )

    def get_events(
        self,
        date: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None
    ) -> list:
        """
        Retrieve audit events

        Args:
            date: Date to retrieve events for (default: today)
            event_type: Filter by event type

        Returns:
            List of audit events
        """
        if date is None:
            date = datetime.now()

        log_file = self.log_dir / f"{date.strftime('%Y-%m-%d')}.json"

        if not log_file.exists():
            return []

        events = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())

                    # Filter by event type if specified
                    if event_type and event['event_type'] != event_type.value:
                        continue

                    events.append(event)
                except json.JSONDecodeError:
                    continue

        return events

    def generate_audit_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        Generate audit report for date range

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Audit report with statistics
        """
        all_events = []
        current_date = start_date

        while current_date <= end_date:
            events = self.get_events(date=current_date)
            all_events.extend(events)
            current_date = current_date.replace(day=current_date.day + 1)

        # Calculate statistics
        stats = {
            "total_events": len(all_events),
            "by_type": {},
            "by_status": {},
            "errors": 0,
            "approvals_requested": 0,
            "approvals_granted": 0,
            "approvals_denied": 0
        }

        for event in all_events:
            # Count by type
            event_type = event['event_type']
            stats['by_type'][event_type] = stats['by_type'].get(event_type, 0) + 1

            # Count by status
            status = event['status']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

            # Count specific events
            if event_type == AuditEventType.ERROR_OCCURRED.value:
                stats['errors'] += 1
            elif event_type == AuditEventType.APPROVAL_REQUESTED.value:
                stats['approvals_requested'] += 1
            elif event_type == AuditEventType.APPROVAL_GRANTED.value:
                stats['approvals_granted'] += 1
            elif event_type == AuditEventType.APPROVAL_DENIED.value:
                stats['approvals_denied'] += 1

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "statistics": stats,
            "events": all_events
        }


# Example usage
if __name__ == "__main__":
    from pathlib import Path

    # Create audit logger
    audit = AuditLogger(Path("AI_Employee_Vault/Logs"))

    # Log various events
    audit.log_email_sent("client@example.com", "Invoice #123", approved_by="human")
    audit.log_invoice_created("INV-123", 1500.00, "Acme Corp")
    audit.log_social_post("linkedin", "Exciting business update!", approved_by="human")
    audit.log_task_executed("process_invoice", auto_executed=True)

    print("Audit events logged successfully!")

    # Retrieve today's events
    events = audit.get_events()
    print(f"\nToday's events: {len(events)}")

    for event in events:
        print(f"  - {event['timestamp']}: {event['action']}")
