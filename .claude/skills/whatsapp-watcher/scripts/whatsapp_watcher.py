#!/usr/bin/env python3
"""
WhatsApp Watcher for AI Employee
Monitors WhatsApp Web for urgent messages using Playwright automation
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from base_watcher import BaseWatcher
from retry_handler import with_retry, TransientError

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: Playwright not installed.")
    print("Run: pip install playwright")
    print("Then: playwright install chromium")
    sys.exit(1)

# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent.parent.parent / "AI_Employee_Vault"
SESSION_PATH = Path(__file__).parent.parent.parent.parent.parent / "whatsapp_session"


class WhatsAppWatcher(BaseWatcher):
    """Monitors WhatsApp Web for urgent messages"""

    def __init__(self, vault_path: Path = VAULT_PATH, check_interval: int = 30):
        super().__init__(vault_path, check_interval, "WhatsAppWatcher")
        self.session_path = SESSION_PATH

        # Urgent keywords to monitor
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 'critical']

        # Track processed messages
        self.processed_messages = set()

        # Ensure session folder exists
        self.session_path.mkdir(parents=True, exist_ok=True)

    @with_retry(max_attempts=2, base_delay=2, max_delay=10)
    def check_for_updates(self, page=None) -> List[Any]:
        """Check WhatsApp Web for urgent messages"""
        if page is None:
            return []

        try:
            # Wait for chat list to load
            page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)

            # Find unread chats
            unread_chats = page.query_selector_all('[aria-label*="unread"]')

            urgent_messages = []

            for chat in unread_chats[:10]:  # Check max 10 unread chats
                try:
                    # Get chat name
                    chat_name_elem = chat.query_selector('[dir="auto"]')
                    chat_name = chat_name_elem.inner_text() if chat_name_elem else "Unknown"

                    # Click to open chat
                    chat.click()
                    time.sleep(1)

                    # Get last message
                    messages = page.query_selector_all('[data-testid="msg-container"]')
                    if messages:
                        last_message = messages[-1]
                        message_text_elem = last_message.query_selector('.copyable-text span')
                        message_text = message_text_elem.inner_text() if message_text_elem else ""

                        # Check for urgent keywords
                        message_lower = message_text.lower()
                        matched_keywords = [kw for kw in self.keywords if kw in message_lower]

                        if matched_keywords:
                            # Create unique ID for this message
                            msg_id = f"{chat_name}_{message_text[:20]}_{int(time.time())}"

                            if msg_id not in self.processed_messages:
                                urgent_messages.append({
                                    'contact': chat_name,
                                    'message': message_text,
                                    'keywords': matched_keywords,
                                    'timestamp': datetime.now().isoformat(),
                                    'id': msg_id
                                })
                                self.processed_messages.add(msg_id)
                                self.logger.info(f"Urgent message from {chat_name}: {matched_keywords}")

                    # Go back to chat list
                    page.keyboard.press('Escape')
                    time.sleep(0.5)

                except Exception as e:
                    self.logger.warning(f"Error processing chat: {e}")
                    continue

            if urgent_messages:
                self.logger.info(f"Found {len(urgent_messages)} urgent message(s)")

            return urgent_messages

        except PlaywrightTimeout:
            self.logger.error("Timeout waiting for WhatsApp Web to load")
            raise TransientError("Timeout waiting for WhatsApp Web")
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            raise TransientError(f"Error checking for updates: {e}")

    def create_action_file(self, item: Any) -> Optional[Path]:
        """Create action file for urgent WhatsApp message"""
        try:
            message = item
            contact = message['contact']
            text = message['message']
            keywords = message['keywords']
            timestamp = int(time.time())

            # Create safe filename
            safe_contact = "".join(c for c in contact if c.isalnum() or c in (' ', '-', '_'))[:30]
            filename = f"WHATSAPP_{safe_contact.replace(' ', '_')}_{timestamp}.md"
            filepath = self.needs_action / filename

            # Create markdown content
            content = f"""---
type: whatsapp
from: {contact}
received: {message['timestamp']}
priority: high
status: pending
keywords_matched: {', '.join(keywords)}
---

# WhatsApp Message Received

## Message Content

{text}

## Suggested Actions

- [ ] Reply to sender
- [ ] Process request
- [ ] Create invoice/payment if needed
- [ ] Archive after handling

## Contact Details

- **From:** {contact}
- **Time:** {message['timestamp']}
- **Keywords:** {', '.join(keywords)}
- **Priority:** high

## Notes

Add processing notes here.

## ⚠️ Important

WhatsApp replies must be sent manually. This watcher is read-only.
"""

            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f"Created action file: {filename}")

            return filepath

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None

    def _log_action(self, message: Dict, filepath: Path):
        """Log WhatsApp message detection to audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": "whatsapp_message_detected",
            "actor": "whatsapp_watcher",
            "contact": message['contact'],
            "keywords": message['keywords'],
            "action_file": str(filepath),
            "status": "pending"
        }
        self.log_to_audit(log_entry)

    def setup_session(self):
        """Initial setup - scan QR code"""
        self.logger.info("=" * 60)
        self.logger.info("WhatsApp Web Setup")
        self.logger.info("=" * 60)
        self.logger.info("Opening WhatsApp Web for QR code scan...")
        self.logger.info("Please scan the QR code with your phone")
        self.logger.info("=" * 60)

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False
            )
            page = browser.pages[0]
            page.goto('https://web.whatsapp.com')

            # Wait for user to scan QR code
            self.logger.info("Waiting for QR code scan...")
            try:
                page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                self.logger.info("✓ Successfully logged in!")
                self.logger.info("Session saved. You can now run the watcher.")
                time.sleep(3)
            except PlaywrightTimeout:
                self.logger.error("Timeout waiting for login. Please try again.")

            browser.close()

    def run(self, headless: bool = True):
        """Main watcher loop with Playwright"""
        self.logger.info("=" * 60)
        self.logger.info("WhatsApp Watcher Started")
        self.logger.info("=" * 60)
        self.logger.info(f"Vault: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        self.logger.info(f"Keywords: {', '.join(self.keywords)}")
        self.logger.info(f"Headless: {headless}")
        self.logger.info("=" * 60)

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=headless
                )
                page = browser.pages[0]
                page.goto('https://web.whatsapp.com')

                # Wait for initial load
                self.logger.info("Waiting for WhatsApp Web to load...")
                page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                self.logger.info("✓ WhatsApp Web loaded successfully")

                # Main monitoring loop
                while True:
                    self.logger.info("Checking for urgent messages...")

                    # Check for urgent messages
                    messages = self.check_for_updates(page)

                    # Create action files
                    for message in messages:
                        self.create_action_file(message)

                    # Wait before next check
                    time.sleep(self.check_interval)

            except KeyboardInterrupt:
                self.logger.info("Stopping WhatsApp watcher...")
            except PlaywrightTimeout:
                self.logger.error("WhatsApp Web session expired. Please run --setup again.")
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
            finally:
                try:
                    browser.close()
                except:
                    pass
                self.logger.info("WhatsApp Watcher Stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('--interval', type=int, default=30,
                        help='Check interval in seconds (default: 30)')
    parser.add_argument('--setup', action='store_true',
                        help='Initial setup: scan QR code')
    parser.add_argument('--test', action='store_true',
                        help='Test mode: check once and exit')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')

    args = parser.parse_args()

    watcher = WhatsAppWatcher(check_interval=args.interval)

    if args.setup:
        watcher.setup_session()
    elif args.test:
        watcher.logger.info("Running in test mode...")
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(watcher.session_path),
                headless=False
            )
            page = browser.pages[0]
            page.goto('https://web.whatsapp.com')
            page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
            messages = watcher.check_for_updates(page)
            watcher.logger.info(f"Found {len(messages)} urgent message(s)")
            for msg in messages:
                watcher.create_action_file(msg)
            browser.close()
        watcher.logger.info("Test complete")
    else:
        watcher.run(headless=args.headless)


if __name__ == "__main__":
    main()
