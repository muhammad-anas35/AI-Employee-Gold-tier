#!/usr/bin/env python3
"""
LinkedIn Poster for AI Employee
Automatically posts business content to LinkedIn with approval workflow
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from rate_limiter import RateLimiter

# Playwright imports for automation approach
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Install with: pip install playwright")

# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent.parent.parent / "AI_Employee_Vault"
PLANS = VAULT_PATH / "Plans"
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
APPROVED = VAULT_PATH / "Approved"
DONE = VAULT_PATH / "Done"
LOGS = VAULT_PATH / "Logs"
SESSION_PATH = Path(__file__).parent.parent.parent.parent / "linkedin_session"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS / "linkedin_poster.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LinkedInPoster")


class LinkedInPoster:
    """Manages LinkedIn posting with approval workflow"""

    def __init__(self, vault_path: Path = VAULT_PATH):
        self.vault_path = vault_path
        self.plans = vault_path / "Plans"
        self.pending_approval = vault_path / "Pending_Approval"
        self.approved = vault_path / "Approved"
        self.done = vault_path / "Done"
        self.session_path = SESSION_PATH

        # Initialize rate limiter
        self.rate_limiter = RateLimiter()

        # Ensure folders exist
        for folder in [self.plans, self.pending_approval, self.approved, self.done, LOGS]:
            folder.mkdir(parents=True, exist_ok=True)

    def create_post_draft(self, content: str, category: str = "business_update",
                          scheduled_for: Optional[str] = None) -> Path:
        """Create a LinkedIn post draft for approval"""
        try:
            timestamp = int(time.time())
            filename = f"POST_linkedin_{category}_{timestamp}.md"
            filepath = self.pending_approval / filename

            # Default schedule to next business day at 9 AM if not specified
            if not scheduled_for:
                now = datetime.now()
                # Find next weekday
                days_ahead = 1
                if now.weekday() >= 4:  # Friday or later
                    days_ahead = 7 - now.weekday() + 1  # Next Monday
                next_day = now + timedelta(days=days_ahead)
                scheduled_for = next_day.replace(hour=9, minute=0, second=0).isoformat()

            # Extract hashtags from content
            hashtags = [word for word in content.split() if word.startswith('#')]

            # Create markdown content
            draft_content = f"""---
type: linkedin_post
status: pending_approval
created: {datetime.now().isoformat()}
scheduled_for: {scheduled_for}
category: {category}
---

# LinkedIn Post Draft

## Post Content

{content}

## Hashtags

{' '.join(hashtags) if hashtags else '#Business #Innovation'}

## Target Audience

- Business owners
- Industry professionals
- Potential clients

## Expected Engagement

- Estimated reach: 500-1000
- Expected engagement rate: 3-5%

## To Approve

Move this file to `/Approved/` folder to publish.

## To Reject

Move this file to `/Rejected/` folder or edit and re-submit.

## Notes

Add any notes or modifications here before approval.
"""

            filepath.write_text(draft_content, encoding='utf-8')
            logger.info(f"Created post draft: {filename}")

            # Log to audit trail
            self._log_action("post_draft_created", {
                "file": filename,
                "category": category,
                "scheduled_for": scheduled_for
            })

            return filepath

        except Exception as e:
            logger.error(f"Error creating post draft: {e}")
            raise

    def check_approved_posts(self) -> List[Path]:
        """Check for approved posts ready to publish"""
        try:
            approved_posts = list(self.approved.glob("POST_*.md"))

            if approved_posts:
                logger.info(f"Found {len(approved_posts)} approved post(s)")

            return approved_posts

        except Exception as e:
            logger.error(f"Error checking approved posts: {e}")
            return []

    def publish_post(self, post_file: Path, use_api: bool = False) -> bool:
        """Publish approved post to LinkedIn"""
        try:
            # Check rate limit before posting
            can_post, wait_time = self.rate_limiter.can_perform("linkedin_post")
            if not can_post:
                logger.error(f"Rate limit exceeded. Wait {wait_time:.0f} seconds before posting.")
                return False

            # Read post content
            content = post_file.read_text(encoding='utf-8')

            # Extract post content from markdown
            lines = content.split('\n')
            post_content = []
            in_content_section = False

            for line in lines:
                if line.strip() == "## Post Content":
                    in_content_section = True
                    continue
                elif line.startswith("## ") and in_content_section:
                    break
                elif in_content_section and line.strip():
                    post_content.append(line)

            post_text = '\n'.join(post_content).strip()

            if use_api:
                # Use LinkedIn API (requires credentials)
                success = self._publish_via_api(post_text)
            else:
                # Use Playwright automation
                success = self._publish_via_playwright(post_text)

            if success:
                # Record action in rate limiter
                self.rate_limiter.record_action("linkedin_post")

                # Move to Done
                done_file = self.done / post_file.name
                post_file.rename(done_file)

                # Add completion note
                with open(done_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n## Published\n\n")
                    f.write(f"- **Published at:** {datetime.now().isoformat()}\n")
                    f.write(f"- **Status:** Success\n")

                logger.info(f"Published post: {post_file.name}")

                # Log to audit trail
                self._log_action("post_published", {
                    "file": post_file.name,
                    "timestamp": datetime.now().isoformat()
                })

                return True
            else:
                logger.error(f"Failed to publish post: {post_file.name}")
                return False

        except Exception as e:
            logger.error(f"Error publishing post: {e}")
            return False

    def _publish_via_api(self, content: str) -> bool:
        """Publish via LinkedIn API (requires credentials)"""
        logger.warning("LinkedIn API publishing not implemented yet")
        logger.info("Please use Playwright automation or implement API integration")
        return False

    def _publish_via_playwright(self, content: str) -> bool:
        """Publish via Playwright automation"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available. Install with: pip install playwright")
            return False

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False
                )
                page = browser.pages[0]
                page.goto('https://www.linkedin.com/feed/')

                # Wait for feed to load
                page.wait_for_selector('[data-test-id="share-box-open"]', timeout=10000)

                # Click "Start a post" button
                page.click('[data-test-id="share-box-open"]')
                time.sleep(1)

                # Type content
                editor = page.wait_for_selector('.ql-editor', timeout=5000)
                editor.fill(content)
                time.sleep(1)

                # Click Post button
                page.click('button[data-test-id="share-actions__primary-action"]')

                # Wait for post to be published
                time.sleep(3)

                browser.close()
                logger.info("Post published successfully via Playwright")
                return True

        except PlaywrightTimeout:
            logger.error("Timeout waiting for LinkedIn to load")
            return False
        except Exception as e:
            logger.error(f"Error publishing via Playwright: {e}")
            return False

    def setup_session(self):
        """Initial setup - login to LinkedIn"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available. Install with: pip install playwright")
            return

        logger.info("=" * 60)
        logger.info("LinkedIn Setup")
        logger.info("=" * 60)
        logger.info("Opening LinkedIn for login...")
        logger.info("Please login manually")
        logger.info("=" * 60)

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False
            )
            page = browser.pages[0]
            page.goto('https://www.linkedin.com/login')

            # Wait for user to login
            logger.info("Waiting for login...")
            try:
                page.wait_for_selector('[data-test-id="share-box-open"]', timeout=120000)
                logger.info("✓ Successfully logged in!")
                logger.info("Session saved. You can now use the poster.")
                time.sleep(3)
            except PlaywrightTimeout:
                logger.error("Timeout waiting for login. Please try again.")

            browser.close()

    def _log_action(self, action_type: str, details: Dict):
        """Log action to audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": "linkedin_poster",
            "details": details,
            "status": "success"
        }

        log_date = datetime.now().strftime("%Y-%m-%d")
        log_file = LOGS / f"{log_date}.json"

        try:
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(log_entry)

            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.error(f"Could not write log: {e}")

    def process_approved_posts(self):
        """Process all approved posts"""
        logger.info("Checking for approved posts...")

        approved_posts = self.check_approved_posts()

        if not approved_posts:
            logger.info("No approved posts to publish")
            return

        for post_file in approved_posts:
            logger.info(f"Publishing: {post_file.name}")
            success = self.publish_post(post_file)

            if success:
                logger.info(f"✓ Published: {post_file.name}")
            else:
                logger.error(f"✗ Failed: {post_file.name}")

            # Wait between posts to avoid rate limiting
            time.sleep(5)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument('--setup', action='store_true',
                        help='Initial setup: login to LinkedIn')
    parser.add_argument('--create', type=str,
                        help='Create post draft with content')
    parser.add_argument('--category', type=str, default='business_update',
                        help='Post category (default: business_update)')
    parser.add_argument('--schedule', type=str,
                        help='Schedule post for specific time (ISO format)')
    parser.add_argument('--publish', action='store_true',
                        help='Publish all approved posts')
    parser.add_argument('--test', action='store_true',
                        help='Test mode: create draft only')

    args = parser.parse_args()

    poster = LinkedInPoster()

    if args.setup:
        poster.setup_session()
    elif args.create:
        draft_file = poster.create_post_draft(
            content=args.create,
            category=args.category,
            scheduled_for=args.schedule
        )
        logger.info(f"Draft created: {draft_file}")
        logger.info("Review and move to /Approved/ to publish")
    elif args.publish:
        poster.process_approved_posts()
    elif args.test:
        test_content = """🚀 Exciting update from our team!

We've been working on something amazing that will transform how businesses operate.

Key highlights:
✅ Increased efficiency by 85%
✅ 24/7 autonomous operation
✅ Seamless integration

What are your thoughts on AI automation? Drop a comment! 👇

#AI #Automation #BusinessInnovation #DigitalTransformation"""

        draft_file = poster.create_post_draft(test_content, category="test")
        logger.info(f"Test draft created: {draft_file}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
