import xmlrpc.client

# Connection details
url = 'http://localhost:8069'
db = 'Ai-Employee'
username = 'ranabro353570@gmail.com'
password = 'admin'

print("Testing Odoo API connection...")

try:
    # Authenticate
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if uid:
        print(f"[OK] Authentication successful! UID: {uid}")

        # Test API access
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Get company info
        company = models.execute_kw(
            db, uid, password,
            'res.company', 'search_read',
            [[]],
            {'fields': ['name'], 'limit': 1}
        )
        print(f"[OK] Company: {company[0]['name']}")

        # Get partner count
        partner_count = models.execute_kw(
            db, uid, password,
            'res.partner', 'search_count',
            [[]]
        )
        print(f"[OK] Partners in database: {partner_count}")

        print("\n[SUCCESS] Odoo API is working perfectly!")

    else:
        print("[FAIL] Authentication failed!")

except Exception as e:
    print(f"[ERROR] {e}")
    print("\nTroubleshooting:")
    print("1. Is Odoo running? Check: docker-compose ps")
    print("2. Is the database created? Go to http://localhost:8069")
    print("3. Are credentials correct? Check username and password")
