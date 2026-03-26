# Gold Tier Setup Instructions

**Date:** 2026-03-25
**Status:** Starting Gold Tier Implementation

---

## Step 1: Install Docker Desktop (30 minutes)

### Windows Installation

1. **Download Docker Desktop:**
   - Go to: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - File size: ~500MB

2. **Install Docker Desktop:**
   - Run the installer (Docker Desktop Installer.exe)
   - Enable WSL 2 during installation (recommended)
   - Restart computer when prompted

3. **Verify Installation:**
   ```bash
   docker --version
   docker-compose --version
   ```

4. **Start Docker Desktop:**
   - Launch Docker Desktop from Start menu
   - Wait for "Docker Desktop is running" message
   - Check system tray for Docker icon

---

## Step 2: Install Odoo Community Edition (1 hour)

### Create Odoo Project Directory

```bash
# Navigate to your project
cd "D:\Coding world\Hackathone_0\Gold"

# Create Odoo directory
mkdir odoo-docker
cd odoo-docker
```

### Create docker-compose.yml

Create file: `odoo-docker/docker-compose.yml`

```yaml
version: '3.1'
services:
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
    restart: always

  odoo:
    image: odoo:19
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - odoo-web-data:/var/lib/odoo
    restart: always

volumes:
  odoo-web-data:
  odoo-db-data:
```

### Start Odoo

```bash
# Start Odoo (first time takes 2-3 minutes)
docker-compose up -d

# Check if running
docker-compose ps

# View logs
docker-compose logs -f odoo
```

### Access Odoo

1. Open browser: http://localhost:8069
2. Wait for Odoo setup page (2-3 minutes)
3. Create database:
   - Master Password: admin
   - Database Name: odoo
   - Email: your-email@example.com
   - Password: admin
   - Phone: (optional)
   - Language: English
   - Country: Your country
   - Demo data: No (uncheck)

4. Click "Create Database"

---

## Step 3: Configure Odoo Accounting (30 minutes)

### Install Accounting Module

1. Go to Apps menu (top left)
2. Search for "Accounting"
3. Click "Install" on Accounting app
4. Wait for installation (1-2 minutes)

### Configure Company

1. Go to Settings → General Settings
2. Click "Companies" → Your company name
3. Fill in:
   - Company Name
   - Address
   - Phone
   - Email
   - Website
   - Tax ID (if applicable)

### Configure Fiscal Year

1. Settings → Accounting
2. Fiscal Periods → Fiscal Years
3. Verify current year is set up

### Create Chart of Accounts

1. Accounting → Configuration → Chart of Accounts
2. Odoo will auto-create based on your country
3. Review and customize if needed

---

## Step 4: Test Odoo API (30 minutes)

### Create Test Script

Create file: `test_odoo_api.py`

```python
import xmlrpc.client

# Connection details
url = 'http://localhost:8069'
db = 'odoo'
username = 'your-email@example.com'  # Use your email
password = 'admin'

print("Testing Odoo API connection...")

try:
    # Authenticate
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if uid:
        print(f"✅ Authentication successful! UID: {uid}")

        # Test API access
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Get company info
        company = models.execute_kw(
            db, uid, password,
            'res.company', 'search_read',
            [[]],
            {'fields': ['name'], 'limit': 1}
        )
        print(f"✅ Company: {company[0]['name']}")

        # Get partner count
        partner_count = models.execute_kw(
            db, uid, password,
            'res.partner', 'search_count',
            [[]]
        )
        print(f"✅ Partners in database: {partner_count}")

        print("\n🎉 Odoo API is working perfectly!")

    else:
        print("❌ Authentication failed!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Is Odoo running? Check: docker-compose ps")
    print("2. Is the database created? Go to http://localhost:8069")
    print("3. Are credentials correct? Check username and password")
```

### Run Test

```bash
python test_odoo_api.py
```

Expected output:
```
Testing Odoo API connection...
✅ Authentication successful! UID: 2
✅ Company: My Company
✅ Partners in database: 3

🎉 Odoo API is working perfectly!
```

---

## Step 5: Update Environment Variables

Add to `.env` file:

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=your-email@example.com
ODOO_PASSWORD=admin
```

---

## Troubleshooting

### Docker won't start
- Restart computer
- Check Docker Desktop is running
- Check Windows features: Hyper-V, WSL 2

### Odoo won't load
- Wait 2-3 minutes after starting
- Check logs: `docker-compose logs odoo`
- Restart: `docker-compose restart`

### Port 8069 already in use
- Check what's using it: `netstat -ano | findstr :8069`
- Kill the process or change Odoo port in docker-compose.yml

### Authentication fails
- Verify database name is "odoo"
- Verify email and password are correct
- Try resetting password in Odoo UI

---

## Next Steps

After completing setup:
1. ✅ Docker installed and running
2. ✅ Odoo running on localhost:8069
3. ✅ Accounting module installed
4. ✅ API test successful
5. ✅ Environment variables configured

**Then proceed to:** Creating the Odoo MCP Server (Day 1 afternoon)

---

**Setup Instructions Complete**
**Estimated Time:** 2-3 hours
**Status:** Ready to begin
