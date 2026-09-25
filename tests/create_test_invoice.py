#!/usr/bin/env python3
"""
Create Test Invoice in Odoo
Demonstrates invoice creation via XML-RPC API
"""

import xmlrpc.client
from datetime import datetime

# Connection details
url = 'http://localhost:8069'
db = 'Ai-Employee'
username = 'admin@nexus.local'
password = 'admin'

print("Creating test invoice in Odoo...")
print("=" * 60)

try:
    # Authenticate
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print("[ERROR] Authentication failed!")
        exit(1)

    print(f"[OK] Authenticated as UID: {uid}")

    # Connect to models
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Step 1: Create or find a customer
    print("\n1. Creating test customer...")

    # Check if customer already exists
    partner_id = models.execute_kw(
        db, uid, password,
        'res.partner', 'search',
        [[('name', '=', 'Test Customer')]]
    )

    if partner_id:
        partner_id = partner_id[0]
        print(f"   [OK] Using existing customer (ID: {partner_id})")
    else:
        # Create new customer
        partner_id = models.execute_kw(
            db, uid, password,
            'res.partner', 'create',
            [{
                'name': 'Test Customer',
                'email': 'customer@example.com',
                'phone': '+1-555-0123',
                'street': '123 Test Street',
                'city': 'Test City',
                'zip': '12345',
                'country_id': 233,  # United States
            }]
        )
        print(f"   [OK] Created new customer (ID: {partner_id})")

    # Step 2: Get product (or create one)
    print("\n2. Getting test product...")

    product_id = models.execute_kw(
        db, uid, password,
        'product.product', 'search',
        [[('name', '=', 'Consulting Service')]]
    )

    if product_id:
        product_id = product_id[0]
        print(f"   [OK] Using existing product (ID: {product_id})")
    else:
        # Create new product
        product_id = models.execute_kw(
            db, uid, password,
            'product.product', 'create',
            [{
                'name': 'Consulting Service',
                'type': 'service',
                'list_price': 150.00,
                'standard_price': 100.00,
            }]
        )
        print(f"   [OK] Created new product (ID: {product_id})")

    # Step 3: Create invoice
    print("\n3. Creating invoice...")

    invoice_id = models.execute_kw(
        db, uid, password,
        'account.move', 'create',
        [{
            'move_type': 'out_invoice',  # Customer invoice
            'partner_id': partner_id,
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': product_id,
                    'name': 'Consulting Service - 10 hours',
                    'quantity': 10,
                    'price_unit': 150.00,
                }),
                (0, 0, {
                    'product_id': product_id,
                    'name': 'Additional Support - 5 hours',
                    'quantity': 5,
                    'price_unit': 150.00,
                }),
            ]
        }]
    )

    print(f"   [OK] Invoice created (ID: {invoice_id})")

    # Step 4: Get invoice details
    print("\n4. Retrieving invoice details...")

    invoice = models.execute_kw(
        db, uid, password,
        'account.move', 'read',
        [invoice_id],
        {'fields': ['name', 'partner_id', 'amount_total', 'state']}
    )[0]

    print(f"   Invoice Number: {invoice['name']}")
    print(f"   Customer: {invoice['partner_id'][1]}")
    print(f"   Total Amount: ${invoice['amount_total']:.2f}")
    print(f"   Status: {invoice['state']}")

    print("\n" + "=" * 60)
    print("[SUCCESS] Test invoice created successfully!")
    print("=" * 60)
    print(f"\nView invoice in Odoo:")
    print(f"URL: {url}/web#id={invoice_id}&model=account.move&view_type=form")
    print(f"\nInvoice ID: {invoice_id}")
    print(f"Invoice Number: {invoice['name']}")
    print(f"Total: ${invoice['amount_total']:.2f}")

except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nTroubleshooting:")
    print("1. Make sure Odoo is running: docker ps")
    print("2. Check accounting module is installed")
    print("3. Verify credentials are correct")
    exit(1)
