import xmlrpc.client
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

class OdooClient:
    """Client for interacting with Odoo via XML-RPC"""

    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None
        self.logger = logging.getLogger(__name__)

    def authenticate(self) -> bool:
        """Authenticate with Odoo"""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
                self.logger.info(f"Authenticated with Odoo (UID: {self.uid})")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False

    def create_customer(self, name: str, email: str) -> Optional[int]:
        """Create a customer in Odoo"""
        try:
            partner_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'create',
                [{
                    'name': name,
                    'email': email,
                    'customer_rank': 1
                }]
            )
            self.logger.info(f"Created customer: {name} (ID: {partner_id})")
            return partner_id
        except Exception as e:
            self.logger.error(f"Failed to create customer: {e}")
            return None

    def find_customer(self, email: str) -> Optional[int]:
        """Find customer by email"""
        try:
            partner_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'search',
                [[['email', '=', email]]]
            )
            return partner_ids[0] if partner_ids else None
        except Exception as e:
            self.logger.error(f"Failed to find customer: {e}")
            return None

    def create_invoice(
        self,
        partner_id: int,
        invoice_lines: List[Dict[str, Any]],
        invoice_date: Optional[str] = None
    ) -> Optional[int]:
        """Create an invoice in Odoo"""
        try:
            # Prepare invoice data
            invoice_data = {
                'partner_id': partner_id,
                'move_type': 'out_invoice',  # Customer invoice
                'invoice_date': invoice_date or datetime.now().strftime('%Y-%m-%d'),
                'invoice_line_ids': [
                    (0, 0, {
                        'name': line['description'],
                        'quantity': line.get('quantity', 1),
                        'price_unit': line['price']
                    })
                    for line in invoice_lines
                ]
            }

            # Create invoice
            invoice_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'create',
                [invoice_data]
            )

            self.logger.info(f"Created invoice ID: {invoice_id}")
            return invoice_id

        except Exception as e:
            self.logger.error(f"Failed to create invoice: {e}")
            return None

    def get_invoice_details(self, invoice_id: int) -> Optional[Dict]:
        """Get invoice details"""
        try:
            invoice = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'read',
                [invoice_id],
                {'fields': ['name', 'partner_id', 'amount_total', 'state', 'invoice_date']}
            )
            return invoice[0] if invoice else None
        except Exception as e:
            self.logger.error(f"Failed to get invoice details: {e}")
            return None

    def record_expense(
        self,
        amount: float,
        category: str,
        description: str,
        expense_date: Optional[str] = None
    ) -> Optional[int]:
        """Record an expense in Odoo"""
        try:
            # Find or create expense category
            category_id = self._get_or_create_category(category)

            # Create expense
            expense_data = {
                'name': description,
                'unit_amount': amount,
                'date': expense_date or datetime.now().strftime('%Y-%m-%d'),
                'product_id': category_id
            }

            expense_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.expense', 'create',
                [expense_data]
            )

            self.logger.info(f"Recorded expense ID: {expense_id}")
            return expense_id

        except Exception as e:
            self.logger.error(f"Failed to record expense: {e}")
            return None

    def get_financial_summary(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get financial summary for period"""
        try:
            # Get invoices
            invoices = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'search_read',
                [[
                    ['move_type', '=', 'out_invoice'],
                    ['invoice_date', '>=', start_date],
                    ['invoice_date', '<=', end_date]
                ]],
                {'fields': ['amount_total', 'state']}
            )

            # Calculate revenue
            total_revenue = sum(
                inv['amount_total']
                for inv in invoices
                if inv['state'] == 'posted'
            )

            # Get expenses
            expenses = self.models.execute_kw(
                self.db, self.uid, self.password,
                'hr.expense', 'search_read',
                [[
                    ['date', '>=', start_date],
                    ['date', '<=', end_date]
                ]],
                {'fields': ['unit_amount', 'state']}
            )

            # Calculate expenses
            total_expenses = sum(
                exp['unit_amount']
                for exp in expenses
                if exp['state'] in ['approved', 'done']
            )

            return {
                'revenue': total_revenue,
                'expenses': total_expenses,
                'profit': total_revenue - total_expenses,
                'invoice_count': len(invoices),
                'expense_count': len(expenses)
            }

        except Exception as e:
            self.logger.error(f"Failed to get financial summary: {e}")
            return {}

    def _get_or_create_category(self, category_name: str) -> int:
        """Get or create expense category"""
        # Search for existing category
        category_ids = self.models.execute_kw(
            self.db, self.uid, self.password,
            'product.product', 'search',
            [[['name', '=', category_name]]]
        )

        if category_ids:
            return category_ids[0]

        # Create new category
        category_id = self.models.execute_kw(
            self.db, self.uid, self.password,
            'product.product', 'create',
            [{
                'name': category_name,
                'type': 'service',
                'can_be_expensed': True
            }]
        )

        return category_id
