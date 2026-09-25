"""Nexus Configuration - Centralized paths and settings"""
from pathlib import Path
import os

# Project root (where this config.py lives)
ROOT = Path(__file__).parent.parent

# Workspace (vault) directory
WORKSPACE = ROOT / "workspace"

# Config directory
CONFIG_DIR = ROOT / "config"

# Ensure workspace directories exist
def ensure_workspace():
    """Create all workspace directories"""
    dirs = [
        WORKSPACE / "inbox",
        WORKSPACE / "pending",
        WORKSPACE / "approved",
        WORKSPACE / "archive",
        WORKSPACE / "reports",
        WORKSPACE / "logs",
        WORKSPACE / "plans",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

# Common paths
NEEDS_ACTION = WORKSPACE / "inbox"
PENDING_APPROVAL = WORKSPACE / "pending"
APPROVED = WORKSPACE / "approved"
DONE = WORKSPACE / "archive"
REPORTS = WORKSPACE / "reports"
LOGS = WORKSPACE / "logs"
PLANS = WORKSPACE / "plans"

# Config files
CREDENTIALS_FILE = CONFIG_DIR / "client_secret_546836721365-jsqg49259347e8l9kghrq80o9j3htrql.apps.googleusercontent.com.json"
TOKEN_FILE = CONFIG_DIR / "token.json"

# Known contacts
KNOWN_CONTACTS_FILE = WORKSPACE / "known_contacts.json"

# Browser data
BROWSER_DATA = ROOT / "browser_data"

# Drop folder
DROP_FOLDER = Path.home() / "Nexus_Drop"

# Odoo defaults
ODOO_URL = "http://localhost:8069"
ODOO_DB = "AiEmployee"
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin@nexus.local")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "changeme123")

# Initialize on import
ensure_workspace()
