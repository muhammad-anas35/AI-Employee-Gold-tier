#!/bin/bash
# Setup script for AI Employee Bronze Tier
# Initializes the vault and installs dependencies

set -e

echo "=========================================="
echo "AI Employee - Bronze Tier Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install dependencies
echo ""
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create drop folder
echo ""
echo -e "${BLUE}Creating drop folder...${NC}"
mkdir -p ~/AI_Employee_Drop
echo -e "${GREEN}✓ Drop folder created at ~/AI_Employee_Drop${NC}"

# Verify vault structure
echo ""
echo -e "${BLUE}Verifying vault structure...${NC}"
required_folders=(
    "AI_Employee_Vault"
    "AI_Employee_Vault/Inbox"
    "AI_Employee_Vault/Needs_Action"
    "AI_Employee_Vault/Plans"
    "AI_Employee_Vault/Pending_Approval"
    "AI_Employee_Vault/Approved"
    "AI_Employee_Vault/Rejected"
    "AI_Employee_Vault/Done"
    "AI_Employee_Vault/Accounting"
    "AI_Employee_Vault/Logs"
)

for folder in "${required_folders[@]}"; do
    if [ -d "$folder" ]; then
        echo -e "${GREEN}✓${NC} $folder"
    else
        echo -e "${YELLOW}✗${NC} $folder (missing)"
    fi
done

# Verify core files
echo ""
echo -e "${BLUE}Verifying core files...${NC}"
required_files=(
    "AI_Employee_Vault/Dashboard.md"
    "AI_Employee_Vault/Company_Handbook.md"
    "filesystem_watcher.py"
    "claude_integration.py"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${YELLOW}✗${NC} $file (missing)"
    fi
done

# Test Claude integration
echo ""
echo -e "${BLUE}Testing Claude integration...${NC}"
python3 claude_integration.py > /dev/null 2>&1 && echo -e "${GREEN}✓ Claude integration working${NC}" || echo -e "${YELLOW}✗ Claude integration test failed${NC}"

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open Obsidian and add vault: AI_Employee_Vault"
echo "2. Start the watcher: python filesystem_watcher.py"
echo "3. Drop a file in: ~/AI_Employee_Drop/"
echo "4. Process tasks: claude /process-vault-tasks"
echo ""
echo "Documentation: README.md"
echo "Rules: AI_Employee_Vault/Company_Handbook.md"
echo "Status: AI_Employee_Vault/Dashboard.md"
echo ""
