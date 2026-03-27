# Odoo Setup Guide

**Status:** Containers running, database needs to be created

---

## Step 1: Access Odoo

Open your browser and go to: **http://localhost:8069**

You should see the Odoo database creation page.

---

## Step 2: Create Database

Fill in the form:

**Master Password:** `admin` (default, you can change it later)

**Database Name:** `odoo` (important - must match config/.env)

**Email:** Your email address (this will be the admin username)

**Password:** Choose a strong password

**Phone number:** Optional

**Language:** English

**Country:** Your country

**Demo data:** ❌ **UNCHECK THIS** (we don't need demo data)

Click **"Create database"**

---

## Step 3: Wait for Database Creation

- This takes 1-2 minutes
- You'll see a loading screen
- Odoo will install base modules

---

## Step 4: First Login

After database creation, you'll be logged in automatically and see the Odoo dashboard.

---

## Step 5: Install Accounting Module

1. Click **"Apps"** in the top menu
2. Remove the "Apps" filter (click the X on the search filter)
3. Search for **"Accounting"** or **"Invoicing"**
4. Find the **"Accounting"** app (has a calculator icon)
5. Click **"Install"**
6. Wait 1-2 minutes for installation

---

## Step 6: Configure Company (Optional)

1. Click the **gear icon** (Settings) in top right
2. Go to **"Companies"** → **"Update Info"**
3. Fill in:
   - Company Name
   - Address
   - Phone
   - Email
   - Website
   - Tax ID (optional)
4. Click **"Save"**

---

## Step 7: Update config/.env

After creating the database, update your credentials in `config/.env`:

```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=your-email@example.com  # The email you used
ODOO_PASSWORD=your-password           # The password you chose
```

---

## Step 8: Test API Connection

Once the database is created and accounting is installed, run:

```bash
python tests/test_odoo_api.py
```

This will verify:
- ✓ Connection to Odoo
- ✓ Authentication
- ✓ API access
- ✓ Accounting module installed
- ✓ Invoice access

---

## Troubleshooting

### "Database already exists" error
- Use a different database name
- Or delete the existing database from Odoo

### Can't access http://localhost:8069
- Check containers are running: `docker ps`
- Restart containers: `cd docker/odoo && docker-compose restart`

### Forgot master password
- Default is `admin`
- Check docker-compose.yml for ODOO_MASTER_PASSWORD

---

## What's Next

After successful setup:
1. Create a test customer
2. Create a test invoice
3. Use API to create invoices programmatically
4. Integrate with AI Employee workflows

---

**Current Status:** Waiting for you to create the database through web interface

**When done, type "continue" and I'll test the API connection!**
