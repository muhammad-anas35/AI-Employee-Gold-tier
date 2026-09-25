# 🔧 Configuration Directory

This directory contains all configuration files for the Gold Tier AI Employee project.

---

## 📁 Configuration Files

### mcp_config.json
**Purpose:** MCP (Model Context Protocol) server configuration

**Content:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "AI_Employee_Vault"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    }
  }
}
```

**Usage:** Automatically loaded by Claude Code

---

### .env (not in git)
**Purpose:** Environment variables and credentials

**Required Variables:**
```bash
# Gmail API
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=admin

# Vault Configuration
VAULT_PATH=AI_Employee_Vault
DROP_FOLDER=~/AI_Employee_Drop

# Social Media APIs (to be added)
FACEBOOK_ACCESS_TOKEN=your_token
INSTAGRAM_ACCESS_TOKEN=your_token
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_secret
```

**Setup:**
```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
nano .env
```

**Security:** Never commit .env to git!

---

### credentials.json (not in git)
**Purpose:** Gmail API OAuth2 credentials

**Content:**
```json
{
  "installed": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

**How to get:**
1. Go to Google Cloud Console
2. Create OAuth2 credentials
3. Download as credentials.json
4. Place in config/ folder

**Security:** Never commit credentials.json to git!

---

## 🔒 Security Best Practices

### What to Commit
- ✅ `mcp_config.json` (no secrets)
- ✅ `.env.example` (template only)
- ✅ Configuration documentation

### What NOT to Commit
- ❌ `.env` (contains secrets)
- ❌ `credentials.json` (contains secrets)
- ❌ `token.json` (OAuth tokens)
- ❌ Any file with API keys or passwords

### .gitignore Rules
```gitignore
# Environment variables
.env
.env.local

# Credentials
credentials.json
token.json
*.key
*.pem

# API keys
*_api_key.txt
*_secret.txt
```

---

## 📝 Configuration Templates

### .env.example
```bash
# Gmail API
GMAIL_CLIENT_ID=your_client_id_here
GMAIL_CLIENT_SECRET=your_client_secret_here

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=admin

# Vault Configuration
VAULT_PATH=AI_Employee_Vault
DROP_FOLDER=~/AI_Employee_Drop

# Social Media APIs
FACEBOOK_ACCESS_TOKEN=your_token_here
INSTAGRAM_ACCESS_TOKEN=your_token_here
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_secret_here
TWITTER_ACCESS_TOKEN=your_token_here
TWITTER_ACCESS_SECRET=your_secret_here
```

---

## 🔧 Loading Configuration

### In Python
```python
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
config_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(config_path)

# Access variables
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'odoo')
VAULT_PATH = Path(os.getenv('VAULT_PATH', 'AI_Employee_Vault'))
```

### In Skills
```python
from pathlib import Path
import os
from dotenv import load_dotenv

# Load from project root
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / "config" / ".env")

# Use configuration
odoo_url = os.getenv('ODOO_URL')
```

---

## 🎯 Configuration by Environment

### Development
```bash
# .env.development
ODOO_URL=http://localhost:8069
DEBUG=true
LOG_LEVEL=debug
```

### Production
```bash
# .env.production
ODOO_URL=https://odoo.yourcompany.com
DEBUG=false
LOG_LEVEL=info
```

### Testing
```bash
# .env.test
ODOO_URL=http://localhost:8069
VAULT_PATH=test_vault
USE_MOCK_APIS=true
```

---

## 📊 Configuration Validation

### Validation Script
```python
import os
from pathlib import Path

def validate_config():
    """Validate all required configuration"""
    required_vars = [
        'GMAIL_CLIENT_ID',
        'GMAIL_CLIENT_SECRET',
        'ODOO_URL',
        'ODOO_DB',
        'VAULT_PATH'
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"❌ Missing configuration: {', '.join(missing)}")
        return False

    print("✅ All required configuration present")
    return True

if __name__ == '__main__':
    validate_config()
```

---

## 🚨 Troubleshooting

### Configuration Not Loading
```bash
# Check if .env exists
ls -la config/.env

# Check file permissions
chmod 600 config/.env

# Verify python-dotenv is installed
pip install python-dotenv
```

### Invalid Credentials
```bash
# Re-download credentials.json from Google Cloud Console
# Verify client_id and client_secret match

# Delete old tokens
rm config/token.json

# Re-authenticate
python .claude/skills/send-email/scripts/send_email.py --auth
```

### Odoo Connection Failed
```bash
# Check Odoo is running
docker ps | grep odoo

# Test connection
curl http://localhost:8069

# Verify credentials in .env
cat config/.env | grep ODOO
```

---

## 📚 Related Documentation

- **Setup Guide:** `docs/guides/SETUP_INSTRUCTIONS.md`
- **Security Guide:** `docs/guides/SECURITY.md` (to be created)
- **API Documentation:** `docs/reference/API.md` (to be created)

---

## 🔄 Configuration Updates

### When Adding New Services
1. Add variables to `.env.example`
2. Document in this README
3. Update validation script
4. Update setup guide

### When Changing Existing Config
1. Update `.env.example`
2. Update this README
3. Notify team members
4. Update dependent code

---

**Last Updated:** 2026-03-26
**Status:** Clean and organized
**Security:** Credentials excluded from git
