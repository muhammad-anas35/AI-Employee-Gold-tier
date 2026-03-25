#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bronze Tier Verification Script
Verifies that all Bronze tier components are properly set up
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
REQUIRED_FOLDERS = [
    "Inbox", "Needs_Action", "Plans", "Pending_Approval",
    "Approved", "Rejected", "Done", "Accounting", "Logs"
]
REQUIRED_FILES = [
    "Dashboard.md", "Company_Handbook.md"
]
REQUIRED_SCRIPTS = [
    "filesystem_watcher.py", "claude_integration.py"
]
REQUIRED_DOCS = [
    "README.md", "QUICKSTART.md", "CHECKLIST.md", "SUMMARY.md"
]

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_folder(folder_name):
    """Check if a folder exists"""
    folder_path = VAULT_PATH / folder_name
    if folder_path.exists() and folder_path.is_dir():
        print(f"{Colors.GREEN}✓{Colors.END} {folder_name}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {folder_name}")
        return False

def check_file(file_name):
    """Check if a file exists"""
    file_path = VAULT_PATH / file_name
    if file_path.exists() and file_path.is_file():
        size = file_path.stat().st_size
        print(f"{Colors.GREEN}✓{Colors.END} {file_name} ({size:,} bytes)")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {file_name}")
        return False

def check_script(script_name):
    """Check if a script exists"""
    script_path = Path(__file__).parent / script_name
    if script_path.exists() and script_path.is_file():
        size = script_path.stat().st_size
        print(f"{Colors.GREEN}✓{Colors.END} {script_name} ({size:,} bytes)")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {script_name}")
        return False

def check_doc(doc_name):
    """Check if a documentation file exists"""
    doc_path = Path(__file__).parent / doc_name
    if doc_path.exists() and doc_path.is_file():
        size = doc_path.stat().st_size
        print(f"{Colors.GREEN}✓{Colors.END} {doc_name} ({size:,} bytes)")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {doc_name}")
        return False

def check_drop_folder():
    """Check if drop folder exists"""
    drop_path = Path.home() / "AI_Employee_Drop"
    if drop_path.exists() and drop_path.is_dir():
        print(f"{Colors.GREEN}✓{Colors.END} Drop folder: {drop_path}")
        return True
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END} Drop folder not found: {drop_path}")
        return False

def check_logs():
    """Check if logs exist"""
    logs_path = VAULT_PATH / "Logs"
    if logs_path.exists():
        log_files = list(logs_path.glob("*.log")) + list(logs_path.glob("*.json"))
        if log_files:
            print(f"{Colors.GREEN}✓{Colors.END} Logs found ({len(log_files)} files)")
            return True
        else:
            print(f"{Colors.YELLOW}⚠{Colors.END} Logs folder empty (no logs yet)")
            return True
    return False

def main():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print(f"{Colors.BLUE}Bronze Tier Verification{Colors.END}")
    print("=" * 60 + "\n")

    passed = 0
    total = 0

    # Check vault structure
    print(f"{Colors.BLUE}Vault Structure:{Colors.END}")
    print(f"Vault path: {VAULT_PATH}\n")

    print("Folders:")
    for folder in REQUIRED_FOLDERS:
        total += 1
        if check_folder(folder):
            passed += 1

    print("\nCore Files:")
    for file in REQUIRED_FILES:
        total += 1
        if check_file(file):
            passed += 1

    # Check scripts
    print(f"\n{Colors.BLUE}Python Scripts:{Colors.END}")
    for script in REQUIRED_SCRIPTS:
        total += 1
        if check_script(script):
            passed += 1

    # Check documentation
    print(f"\n{Colors.BLUE}Documentation:{Colors.END}")
    for doc in REQUIRED_DOCS:
        total += 1
        if check_doc(doc):
            passed += 1

    # Check drop folder
    print(f"\n{Colors.BLUE}Drop Folder:{Colors.END}")
    check_drop_folder()

    # Check logs
    print(f"\n{Colors.BLUE}Audit Logs:{Colors.END}")
    check_logs()

    # Summary
    print("\n" + "=" * 60)
    print(f"{Colors.BLUE}Summary:{Colors.END}")
    print(f"Passed: {Colors.GREEN}{passed}/{total}{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}✓ All checks passed! Bronze tier is ready.{Colors.END}")
        print("\nNext steps:")
        print("1. python filesystem_watcher.py")
        print("2. Drop a file in ~/AI_Employee_Drop/")
        print("3. claude /process-vault-tasks --vault-path AI_Employee_Vault")
        return 0
    else:
        print(f"\n{Colors.YELLOW}⚠ Some checks failed. Please review above.{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
