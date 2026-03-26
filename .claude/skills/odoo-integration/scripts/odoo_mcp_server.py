#!/usr/bin/env python3
"""
Odoo MCP Server for AI Employee
Provides accounting integration via Odoo XML-RPC API
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

# Import OdooClient
from odoo_client import OdooClient

# Vault path
VAULT_PATH = Path(__file__).parent.parent.parent.parent.parent / "AI_Employee_Vault"


class OdooMCPServer:
    """MCP Server for Odoo integration"""

    def __init__(self):
        self.url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.db = os.getenv('ODOO_DB', 'odoo')
        self.username = os.getenv('ODOO_USERNAME', 'admin@example.com')
        self.password = os.getenv('ODOO_PASSWORD', 'admin')
        self.client = OdooClient(self.url, self.db, self.username, self.password)

    def create_invoice_request(
        self,
        client_name: str,
        client_email: str,
        amount: float,
        description: str
    ) -> Path:
        """Create invoice request in Pending_Approval"""
        timestamp = int(datetime.now().timestamp())
        filename = f"INVOICE_{client_name.replace(' ', '_')}_{timestamp}.md"
        filepath = VAULT_PATH / "Pending_Approval" / filename

        content = f"""---
type: invoice
client_name: {client_name}
client_email: {client_email}
amount: ${amount}
status: pending_approval
created: {datetime.now().isoformat()}
---

# Invoice Request

## Client Information
- **Name:** {client_name}
- **Email:** {client_email}

## Invoice Details
- **Amount:** ${amount}
- **Description:** {description}

## Action Required
Please review and approve this invoice request.

**To approve:** Move this file to `/Approved/`
**To reject:** Move this file to `/Rejected/`

## Next Steps (After Approval)
1. Create invoice in Odoo
2. Generate PDF
3. Send via email to client
4. Log to accounting system
"""

        filepath.write_text(content, encoding='utf-8')
        print(f"✅ Invoice request created: {filepath}")
        return filepath

    def process_approved_invoices(self) -> List[Dict]:
        """Process all approved invoice requests"""
        approved_folder = VAULT_PATH / "Approved"
        results = []

        for file in approved_folder.glob("INVOICE_*.md"):
            try:
                # Parse invoice request
                content = file.read_text(encoding='utf-8')
                lines = content.split('\n')

                # Extract metadata
                metadata = {}
                in_frontmatter = False
                for line in lines:
                    if line.strip() == '---':
                        in_frontmatter = not in_frontmatter
                        continue
                    if in_frontmatter and ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()

                # Authenticate with Odoo
                if not self.client.authenticate():
                    print(f"❌ Failed to authenticate with Odoo")
                    continue

                # Find or create customer
                client_email = metadata.get('client_email', '').strip()
                client_name = metadata.get('client_name', '').strip()

                partner_id = self.client.find_customer(client_email)
                if not partner_id:
                    partner_id = self.client.create_customer(client_name, client_email)

                if not partner_id:
                    print(f"❌ Failed to create customer: {client_name}")
                    continue

                # Create invoice
                amount_str = metadata.get('amount', '$0').replace('$', '').strip()
                amount = float(amount_str)

                # Extract description from content
                description = "Services rendered"
                for line in lines:
                    if line.startswith('- **Description:**'):
                        description = line.split(':', 1)[1].strip()
                        break

                invoice_lines = [{
                    'description': description,
                    'quantity': 1,
                    'price': amount
                }]

                invoice_id = self.client.create_invoice(partner_id, invoice_lines)

                if invoice_id:
                    # Get invoice details
                    invoice_details = self.client.get_invoice_details(invoice_id)

                    # Move to Done
                    done_file = VAULT_PATH / "Done" / file.name
                    file.rename(done_file)

                    # Update file with result
                    result_content = content + f"""

---

## Result
✅ Invoice created successfully in Odoo

- **Invoice ID:** {invoice_id}
- **Invoice Number:** {invoice_details.get('name', 'N/A')}
- **Status:** {invoice_details.get('state', 'draft')}
- **Total:** ${invoice_details.get('amount_total', 0)}
- **Processed:** {datetime.now().isoformat()}
"""
                    done_file.write_text(result_content, encoding='utf-8')

                    results.append({
                        'file': file.name,
                        'status': 'success',
                        'invoice_id': invoice_id,
                        'invoice_number': invoice_details.get('name', 'N/A')
                    })

                    print(f"✅ Invoice created: {invoice_details.get('name', 'N/A')}")

            except Exception as e:
                print(f"❌ Error processing {file.name}: {e}")
                results.append({
                    'file': file.name,
                    'status': 'error',
                    'error': str(e)
                })

        return results

    def record_expense_request(
        self,
        amount: float,
        category: str,
        description: str
    ) -> Path:
        """Create expense record request in Pending_Approval"""
        timestamp = int(datetime.now().timestamp())
        filename = f"EXPENSE_{category.replace(' ', '_')}_{timestamp}.md"
        filepath = VAULT_PATH / "Pending_Approval" / filename

        content = f"""---
type: expense
category: {category}
amount: ${amount}
status: pending_approval
created: {datetime.now().isoformat()}
---

# Expense Record Request

## Expense Details
- **Category:** {category}
- **Amount:** ${amount}
- **Description:** {description}

## Action Required
Please review and approve this expense record.

**To approve:** Move this file to `/Approved/`
**To reject:** Move this file to `/Rejected/`

## Next Steps (After Approval)
1. Record expense in Odoo
2. Update financial reports
3. Log to accounting system
"""

        filepath.write_text(content, encoding='utf-8')
        print(f"✅ Expense request created: {filepath}")
        return filepath

    def get_financial_summary(self, period: str = "this-month") -> Dict[str, Any]:
        """Get financial summary for period"""
        # Authenticate
        if not self.client.authenticate():
            return {"error": "Authentication failed"}

        # Calculate date range
        now = datetime.now()
        if period == "this-week":
            start_date = (now - timedelta(days=7)).strftime('%Y-%m-%d')
        elif period == "this-month":
            start_date = now.replace(day=1).strftime('%Y-%m-%d')
        elif period == "this-year":
            start_date = now.replace(month=1, day=1).strftime('%Y-%m-%d')
        else:
            start_date = now.replace(day=1).strftime('%Y-%m-%d')

        end_date = now.strftime('%Y-%m-%d')

        # Get summary
        summary = self.client.get_financial_summary(start_date, end_date)
        summary['period'] = period
        summary['start_date'] = start_date
        summary['end_date'] = end_date

        return summary


def main():
    parser = argparse.ArgumentParser(description='Odoo MCP Server')
    parser.add_argument('--create-invoice', action='store_true', help='Create invoice request')
    parser.add_argument('--client', type=str, help='Client name')
    parser.add_argument('--email', type=str, help='Client email')
    parser.add_argument('--amount', type=float, help='Invoice amount')
    parser.add_argument('--description', type=str, help='Invoice description')

    parser.add_argument('--record-expense', action='store_true', help='Record expense')
    parser.add_argument('--category', type=str, help='Expense category')

    parser.add_argument('--process-approved', action='store_true', help='Process approved invoices')
    parser.add_argument('--financial-summary', action='store_true', help='Get financial summary')
    parser.add_argument('--period', type=str, default='this-month', help='Period for summary')

    args = parser.parse_args()

    server = OdooMCPServer()

    if args.create_invoice:
        if not all([args.client, args.email, args.amount, args.description]):
            print("❌ Missing required arguments: --client, --email, --amount, --description")
            return

        filepath = server.create_invoice_request(
            args.client,
            args.email,
            args.amount,
            args.description
        )
        print(f"\n📋 Next steps:")
        print(f"1. Review the invoice request: {filepath}")
        print(f"2. Move to /Approved/ to process")
        print(f"3. Run: python odoo_mcp_server.py --process-approved")

    elif args.record_expense:
        if not all([args.amount, args.category, args.description]):
            print("❌ Missing required arguments: --amount, --category, --description")
            return

        filepath = server.record_expense_request(
            args.amount,
            args.category,
            args.description
        )
        print(f"\n📋 Expense request created: {filepath}")

    elif args.process_approved:
        print("Processing approved invoices...")
        results = server.process_approved_invoices()
        print(f"\n✅ Processed {len(results)} invoices")
        for result in results:
            print(f"  - {result['file']}: {result['status']}")

    elif args.financial_summary:
        print(f"Getting financial summary for {args.period}...")
        summary = server.get_financial_summary(args.period)
        print(f"\n📊 Financial Summary ({args.period})")
        print(f"  Revenue: ${summary.get('revenue', 0):.2f}")
        print(f"  Expenses: ${summary.get('expenses', 0):.2f}")
        print(f"  Profit: ${summary.get('profit', 0):.2f}")
        print(f"  Invoices: {summary.get('invoice_count', 0)}")
        print(f"  Expenses: {summary.get('expense_count', 0)}")

    else:
        parser.print_help()


if __name__ == '__main__':
    from datetime import timedelta
    main()
