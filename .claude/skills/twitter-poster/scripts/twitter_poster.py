#!/usr/bin/env python3
"""
Twitter Poster for AI Employee
Posts tweets to Twitter/X using Playwright automation with approval workflow
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

def create_tweet_draft(content: str, image_path: str = None):
    """Create a tweet draft in Pending_Approval folder"""
    timestamp = int(datetime.now().timestamp())
    filename = f"TWEET_{timestamp}.md"
    filepath = PENDING_APPROVAL / filename

    tweet_data = {
        "platform": "twitter",
        "content": content,
        "image": image_path,
        "created_at": datetime.now().isoformat(),
        "status": "pending_approval"
    }

    # Create markdown file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Twitter/X Tweet Draft\n\n")
        f.write(f"**Created:** {tweet_data['created_at']}\n")
        f.write(f"**Status:** Pending Approval\n")
        f.write(f"**Character Count:** {len(content)}/280\n\n")
        f.write(f"## Content\n\n")
        f.write(f"{content}\n\n")
        if image_path:
            f.write(f"**Image:** {image_path}\n\n")
        f.write(f"---\n\n")
        f.write(f"**Instructions:**\n")
        f.write(f"1. Review the content above\n")
        f.write(f"2. If approved, move this file to: `Approved/`\n")
        f.write(f"3. If rejected, move to: `Rejected/`\n")
        f.write(f"4. Run: `python .claude/skills/twitter-poster/scripts/twitter_poster.py --publish`\n")

    print(f"[OK] Tweet draft created: {filepath}")
    print(f"[INFO] Character count: {len(content)}/280")
    print(f"[INFO] Review and move to Approved/ folder to publish")
    return filepath

def publish_approved_tweets():
    """Publish all approved tweets"""
    approved_tweets = list(APPROVED.glob("TWEET_*.md"))

    if not approved_tweets:
        print("[INFO] No approved tweets found")
        return

    print(f"[INFO] Found {len(approved_tweets)} approved tweet(s)")

    with sync_playwright() as p:
        # Launch browser with persistent context (saves login)
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA),
            headless=False,
            args=['--start-maximized']
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            # Go to Twitter
            print("[INFO] Opening Twitter/X...")
            page.goto("https://twitter.com", wait_until="networkidle")

            # Check if logged in
            if "login" in page.url.lower() or page.locator('a[href="/login"]').count() > 0:
                print("\n" + "="*60)
                print("[ACTION REQUIRED] Please log in to Twitter/X")
                print("="*60)
                print("1. Log in to your Twitter/X account in the browser")
                print("2. Complete any 2FA if required")
                print("3. Press Enter here when logged in...")
                input()
                page.wait_for_load_state("networkidle")

            # Process each approved tweet
            for tweet_file in approved_tweets:
                print(f"\n[INFO] Publishing: {tweet_file.name}")

                # Read tweet content
                with open(tweet_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract content between ## Content and ---
                start = content.find("## Content\n\n") + len("## Content\n\n")
                end = content.find("\n\n---")
                tweet_text = content[start:end].strip()

                try:
                    # Click tweet compose button
                    selectors = [
                        'a[data-testid="SideNav_NewTweet_Button"]',
                        'a[aria-label="Post"]',
                        'div[data-testid="SideNav_NewTweet_Button"]',
                        'a[href="/compose/tweet"]'
                    ]

                    clicked = False
                    for selector in selectors:
                        try:
                            page.click(selector, timeout=3000)
                            clicked = True
                            print("[OK] Opened tweet composer")
                            break
                        except:
                            continue

                    if not clicked:
                        print("[ERROR] Could not find tweet compose button")
                        continue

                    # Wait for composer to open
                    page.wait_for_timeout(2000)

                    # Find and click the text area
                    text_selectors = [
                        'div[data-testid="tweetTextarea_0"]',
                        'div[role="textbox"][aria-label*="Post"]',
                        'div[role="textbox"][contenteditable="true"]'
                    ]

                    typed = False
                    for selector in text_selectors:
                        try:
                            page.click(selector, timeout=3000)
                            page.keyboard.type(tweet_text, delay=50)
                            typed = True
                            print("[OK] Typed tweet content")
                            break
                        except:
                            continue

                    if not typed:
                        print("[ERROR] Could not find tweet text area")
                        continue

                    # Wait a moment
                    page.wait_for_timeout(1000)

                    # Click Post button
                    post_buttons = [
                        'button[data-testid="tweetButtonInline"]',
                        'button[data-testid="tweetButton"]',
                        'div[data-testid="tweetButton"]',
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

                    # Wait for tweet to post
                    page.wait_for_timeout(3000)

                    # Take screenshot as proof
                    screenshot_path = DONE / f"twitter_post_{int(datetime.now().timestamp())}.png"
                    page.screenshot(path=str(screenshot_path))
                    print(f"[OK] Screenshot saved: {screenshot_path}")

                    # Move to Done
                    done_path = DONE / tweet_file.name
                    tweet_file.rename(done_path)
                    print(f"[OK] Moved to Done: {done_path}")

                    # Update file with completion info
                    with open(done_path, 'a', encoding='utf-8') as f:
                        f.write(f"\n\n## Published\n\n")
                        f.write(f"**Published at:** {datetime.now().isoformat()}\n")
                        f.write(f"**Screenshot:** {screenshot_path.name}\n")

                    print(f"[SUCCESS] Tweet published successfully!")

                except Exception as e:
                    print(f"[ERROR] Failed to publish tweet: {e}")
                    print("[INFO] Tweet file remains in Approved/ folder")
                    continue

        finally:
            print("\n[INFO] Closing browser in 5 seconds...")
            page.wait_for_timeout(5000)
            browser.close()

def test_setup():
    """Test Twitter login and setup"""
    print("[INFO] Testing Twitter/X setup...")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA),
            headless=False
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            page.goto("https://twitter.com", wait_until="networkidle")

            if "login" in page.url.lower() or page.locator('a[href="/login"]').count() > 0:
                print("\n[INFO] Not logged in. Please log in now...")
                print("[INFO] After logging in, press Enter...")
                input()
            else:
                print("[OK] Already logged in to Twitter/X!")

            # Try to find tweet compose button
            try:
                page.wait_for_selector('a[data-testid="SideNav_NewTweet_Button"]', timeout=5000)
                print("[OK] Tweet composer found - ready to post!")
            except:
                print("[WARNING] Could not find tweet composer")
                print("[INFO] You may need to navigate to your home feed")

            print("\n[SUCCESS] Setup test complete!")
            print("[INFO] You can now create and publish tweets")

        finally:
            page.wait_for_timeout(3000)
            browser.close()

def main():
    parser = argparse.ArgumentParser(description="Twitter Poster for AI Employee")
    parser.add_argument('--create', type=str, help='Create a tweet draft')
    parser.add_argument('--image', type=str, help='Image path for tweet')
    parser.add_argument('--publish', action='store_true', help='Publish approved tweets')
    parser.add_argument('--test', action='store_true', help='Test Twitter login setup')

    args = parser.parse_args()

    if args.test:
        test_setup()
    elif args.create:
        create_tweet_draft(args.create, args.image)
    elif args.publish:
        publish_approved_tweets()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
