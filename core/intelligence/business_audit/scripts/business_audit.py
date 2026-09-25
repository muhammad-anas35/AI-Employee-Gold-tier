#!/usr/bin/env python3
"""
Business Audit - Weekly automated business intelligence reports
Analyzes all activities across domains and generates actionable insights
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.integration.claude_integration import VaultManager

# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent / "workspace"
REPORTS_DIR = VAULT_PATH / "reports"
LOGS_DIR = VAULT_PATH / "Logs"
DONE_DIR = VAULT_PATH / "archive"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BusinessAudit")


class BusinessAudit:
    """Generate comprehensive business audit reports"""

    def __init__(self):
        self.vault = VaultManager(VAULT_PATH)
        self.metrics = {
            "emails_processed": 0,
            "tasks_completed": 0,
            "social_posts": 0,
            "invoices_generated": 0,
            "files_organized": 0,
            "auto_executed": 0,
            "approval_requested": 0,
            "errors": 0
        }

    def analyze_logs(self, from_date: datetime, to_date: datetime) -> Dict:
        """Analyze log files for the date range"""
        logger.info(f"Analyzing logs from {from_date.date()} to {to_date.date()}")

        activities = []
        current_date = from_date

        while current_date <= to_date:
            log_file = LOGS_DIR / f"{current_date.strftime('%Y-%m-%d')}.json"

            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                activities.append(entry)
                            except json.JSONDecodeError:
                                continue
                except Exception as e:
                    logger.warning(f"Error reading log {log_file}: {e}")

            current_date += timedelta(days=1)

        logger.info(f"Found {len(activities)} log entries")
        return activities

    def analyze_done_folder(self) -> Dict:
        """Analyze completed tasks in Done folder"""
        logger.info("Analyzing Done folder")

        done_files = list(DONE_DIR.glob("*.md"))

        for file in done_files:
            filename = file.name.upper()

            if "EMAIL" in filename:
                self.metrics["emails_processed"] += 1
            elif "TWEET" in filename or "POST_FACEBOOK" in filename or "POST_LINKEDIN" in filename:
                self.metrics["social_posts"] += 1
            elif "FILE" in filename:
                self.metrics["files_organized"] += 1
            elif "INVOICE" in filename:
                self.metrics["invoices_generated"] += 1

            self.metrics["tasks_completed"] += 1

        logger.info(f"Analyzed {len(done_files)} completed tasks")
        return self.metrics

    def get_financial_summary(self) -> Dict:
        """Get financial summary from Odoo (if available)"""
        # Placeholder for Odoo integration
        return {
            "total_revenue": 0,
            "total_expenses": 0,
            "outstanding_invoices": 0,
            "invoices_paid": 0
        }

    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if self.metrics["errors"] > 10:
            recommendations.append("⚠️ High error rate detected. Review error logs and improve error handling.")

        if self.metrics["approval_requested"] > self.metrics["auto_executed"]:
            recommendations.append("💡 Many tasks require approval. Consider expanding safe action list.")

        if self.metrics["emails_processed"] > 50:
            recommendations.append("📧 High email volume. Consider email filtering or auto-responses.")

        if self.metrics["social_posts"] < 5:
            recommendations.append("📱 Low social media activity. Increase posting frequency for better engagement.")

        if not recommendations:
            recommendations.append("✅ All systems operating normally. No immediate actions required.")

        return recommendations

    def generate_report(self, from_date: datetime, to_date: datetime) -> str:
        """Generate comprehensive audit report"""
        logger.info("Generating business audit report")

        # Analyze data
        activities = self.analyze_logs(from_date, to_date)
        self.analyze_done_folder()
        financial = self.get_financial_summary()
        recommendations = self.generate_recommendations()

        # Calculate date range
        days = (to_date - from_date).days + 1

        # Generate report
        report = f"""# Business Audit Report

**Period:** {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')} ({days} days)
**Generated:** {datetime.now().isoformat()}

---

## Executive Summary

### Key Highlights

- **Tasks Completed:** {self.metrics['tasks_completed']}
- **Auto-Executed:** {self.metrics['auto_executed']}
- **Approval Requested:** {self.metrics['approval_requested']}
- **Error Rate:** {self.metrics['errors']} errors

### Activity Breakdown

| Category | Count |
|----------|-------|
| Emails Processed | {self.metrics['emails_processed']} |
| Social Media Posts | {self.metrics['social_posts']} |
| Invoices Generated | {self.metrics['invoices_generated']} |
| Files Organized | {self.metrics['files_organized']} |

---

## Performance Metrics

### Automation Efficiency

- **Automation Rate:** {(self.metrics['auto_executed'] / max(self.metrics['tasks_completed'], 1) * 100):.1f}%
- **Approval Rate:** {(self.metrics['approval_requested'] / max(self.metrics['tasks_completed'], 1) * 100):.1f}%
- **Success Rate:** {((self.metrics['tasks_completed'] - self.metrics['errors']) / max(self.metrics['tasks_completed'], 1) * 100):.1f}%

### Daily Averages

- **Tasks per Day:** {self.metrics['tasks_completed'] / days:.1f}
- **Emails per Day:** {self.metrics['emails_processed'] / days:.1f}
- **Posts per Day:** {self.metrics['social_posts'] / days:.1f}

---

## Financial Summary

| Metric | Amount |
|--------|--------|
| Total Revenue | ${financial['total_revenue']:,.2f} |
| Total Expenses | ${financial['total_expenses']:,.2f} |
| Outstanding Invoices | {financial['outstanding_invoices']} |
| Invoices Paid | {financial['invoices_paid']} |

---

## Recommendations

"""

        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"

        report += f"""
---

## Next Steps

1. Review recommendations above
2. Address any high-priority issues
3. Monitor metrics for next week
4. Adjust automation rules if needed

---

**Report Generated by:** AI Employee Business Audit
**Next Audit:** {(to_date + timedelta(days=7)).strftime('%Y-%m-%d')}
"""

        return report

    def save_report(self, report: str, from_date: datetime) -> Path:
        """Save report to Reports folder"""
        timestamp = from_date.strftime('%Y-%m-%d')

        # Save markdown
        md_path = REPORTS_DIR / f"AUDIT_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"Report saved: {md_path}")

        # Save JSON metrics
        json_path = REPORTS_DIR / f"AUDIT_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "period_start": from_date.isoformat(),
                "period_end": (from_date + timedelta(days=6)).isoformat(),
                "generated_at": datetime.now().isoformat(),
                "metrics": self.metrics
            }, f, indent=2)

        logger.info(f"Metrics saved: {json_path}")

        return md_path


def main():
    """Generate weekly business audit"""
    logger.info("Starting Business Audit")

    # Calculate last week (Monday to Sunday)
    today = datetime.now()
    days_since_monday = today.weekday()
    last_monday = today - timedelta(days=days_since_monday + 7)
    last_sunday = last_monday + timedelta(days=6)

    # Generate report
    audit = BusinessAudit()
    report = audit.generate_report(last_monday, last_sunday)
    report_path = audit.save_report(report, last_monday)

    logger.info(f"✓ Business audit complete: {report_path}")
    print(f"\n[SUCCESS] Business audit report generated: {report_path}")


if __name__ == "__main__":
    main()
