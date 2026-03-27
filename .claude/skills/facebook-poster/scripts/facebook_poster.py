#!/usr/bin/env python3
"""
Facebook Poster for AI Employee
Posts content to Facebook using Playwright automation with approval workflow
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent.parent.parent / "AI_Employee_Vault"
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
APPROVED = VAULT_PATH / "Approved"
DONE = VAULT_PATH / "Done"
BROWSER_DATA = Path(__file__).parent.parent / "browser_data"

# Ensure directories exist
PENDING_APPROVAL.mkdir(parents=True, exist_ok=True)
APPROVED.mkdir(parents=True, exist_ok=True)
DONE.mkdir(parents=True, exist_ok=True)
BROWSER_DATA.mkdir(parents=True, exist_ok=True)

def create_post_draft(content: str, image_path: str = None):
    """Create a post draft in Pending_Approval folder"""
    timestamp = int(datetime.now().timestamp())
    filename = f"POST_facebook_{timestamp}.md"
    filepath = PENDING_APPROVAL / filename

    post_data = {
        "platform": "facebook",
        "content": content,
        "image": image_path,
        "created_at": datetime.now().isoformat(),
        "status": "pending_approval"
    }

    # Create markdown file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Facebook Post Draft\n\n")
        f.write(f"**Created:** {post_data['created_at']}\n")
        f.write(f"**Status:** Pending Approval\n\n")
        f.write(f"## Content\n\n")
        f.write(f"{content}\n\n")
        if image_path:
            f.write(f"**Image:** {image_path}\n\n")
        f.write(f"---\n\n")
        f.write(f"**Instructions:**\n")
        f.write(f"1. Review the content above\n")
        f.write(f"2. If approved, move this file to: `Approved/`\n")
        f.write(f"3. If rejected, move to: `Rejected/`\n")
        f.write(f"4. Run: `python .claude/skills/facebook-poster/scripts/facebook_poster.py --publish`\n")

    print(f"[OK] Post draft created: {filepath}")
    print(f"[INFO] Review and move to Approved/ folder to publish")
    return filepath

def publish_approved_posts():
    """Publish all approved Facebook posts"""
    approved_posts = list(APPROVED.glob("POST_facebook_*.md"))

    if not approved_posts:
        print("[INFO] No approved Facebook posts found")
        return

    print(f"[INFO] Found {len(approved_posts)} approved post(s)")

    with sync_playwright() as p:
        # Launch browser with persistent context (saves login)
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA),
            headless=False,
            args=['--start-maximized']
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            # Go to Facebook
            print("[INFO] Opening Facebook...")
            page.goto("https://www.facebook.com", wait_until="networkidle")

            # Check if logged in
            if "login" in page.url.lower():
                print("\n" + "="*60)
                print("[ACTION REQUIRED] Please log in to Facebook")
                print("="*60)
                print("1. Log in to your Facebook account in the browser")
                print("2. Complete any 2FA if required")
                print("3. Press Enter here when logged in...")
                input()
                page.wait_for_load_state("networkidle")

            # Process each approved post
            for post_file in approved_posts:
                print(f"\n[INFO] Publishing: {post_file.name}")

                # Read post content
                with open(post_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract content between ## Content and ---
                start = content.find("## Content\n\n") + len("## Content\n\n")
                end = content.find("\n\n---")
                post_text = content[start:end].strip()

                # Click "What's on your mind?" or create post button
                try:
                    # Try different selectors for post creation
                    selectors = [
                        'div[role="button"][aria-label*="What\'s on your mind"]',
                        'div[role="button"][aria-label*="Create post"]',
                        'div[role="button"][aria-label*="Write something"]',
                        'span:has-text("What\'s on your mind")'
                    ]

                    clicked = False
                    for selector in selectors:
                        try:
                            page.click(selector, timeout=3000)
                            clicked = True
                            print("[OK] Opened post composer")
                            break
                        except:
                            continue

                    if not clicked:
                        print("[ERROR] Could not find post composer button")
                        continue

                    # Wait for composer to open
                    page.wait_for_timeout(2000)

                    # Type the post content
                    page.keyboard.type(post_text, delay=50)
                    print("[OK] Typed post content")

                    # Wait a moment
                    page.wait_for_timeout(1000)

                    # Click Post button
                    post_buttons = [
                        'div[role="button"][aria-label="Post"]',
                        'div[role="button"]:has-text("Post")',
                        'button:has-text("Post")'
                    ]

                    posted = False
                    for selector in post_buttons:
                        try:
                            page.click(selector, timeout=3000)
                            posted = True
                            print("[OK] Clicked Post button")
                            break
                        except:
                            continue

                    if not posted:
                        print("[ERROR] Could not find Post button")
                        print("[INFO] Please click Post manually, then press Enter...")
                        input()

                    # Wait for post to complete
                    page.wait_for_timeout(3000)

                    # Take screenshot as proof
                    screenshot_path = DONE / f"facebook_post_{int(datetime.now().timestamp())}.png"
                    page.screenshot(path=str(screenshot_path))
                    print(f"[OK] Screenshot saved: {screenshot_path}")

                    # Move to Done
                    done_path = DONE / post_file.name
                    post_file.rename(done_path)
                    print(f"[OK] Moved to Done: {done_path}")

                    # Update file with completion info
                    with open(done_path, 'a', encoding='utf-8') as f:
                        f.write(f"\n\n## Published\n\n")
                        f.write(f"**Published at:** {datetime.now().isoformat()}\n")
                        f.write(f"**Screenshot:** {screenshot_path.name}\n")

                    print(f"[SUCCESS] Post published successfully!")

                except Exception as e:
                    print(f"[ERROR] Failed to publish post: {e}")
                    print("[INFO] Post file remains in Approved/ folder")
                    continue

        finally:
            print("\n[INFO] Closing browser in 5 seconds...")
            page.wait_for_timeout(5000)
            browser.close()

def test_setup():
    """Test Facebook login and setup"""
    print("[INFO] Testing Facebook setup...")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA),
            headless=False
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            page.goto("https://www.facebook.com", wait_until="networkidle")

            if "login" in page.url.lower():
                print("\n[INFO] Not logged in. Please log in now...")
                print("[INFO] After logging in, press Enter...")
                input()
            else:
                print("[OK] Already logged in to Facebook!")

            # Try to find post composer
            try:
                page.wait_for_selector('div[role="button"][aria-label*="What\'s on your mind"]', timeout=5000)
                print("[OK] Post composer found - ready to post!")
            except:
                print("[WARNING] Could not find post composer")
                print("[INFO] You may need to navigate to your profile or feed")

            print("\n[SUCCESS] Setup test complete!")
            print("[INFO] You can now create and publish posts")

        finally:
            page.wait_for_timeout(3000)
            browser.close()

def main():
    parser = argparse.ArgumentParser(description="Facebook Poster for AI Employee")
    parser.add_argument('--create', type=str, help='Create a post draft')
    parser.add_argument('--image', type=str, help='Image path for post')
    parser.add_argument('--publish', action='store_true', help='Publish approved posts')
    parser.add_argument('--test', action='store_true', help='Test Facebook login setup')

    args = parser.parse_args()

    if args.test:
        test_setup()
    elif args.create:
        create_post_draft(args.create, args.image)
    elif args.publish:
        publish_approved_posts()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
