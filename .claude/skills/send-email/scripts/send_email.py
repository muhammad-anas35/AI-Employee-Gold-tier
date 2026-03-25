#!/usr/bin/env python3
"""
Email Sender for AI Employee
Sends emails via Gmail API with approval workflow
"""

import os
import sys
import json
import base64
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from rate_limiter import RateLimiter

# Gmail API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Error: Gmail API libraries not installed.")
    print("Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent.parent.parent / "AI_Employee_Vault"
PLANS = VAULT_PATH / "Plans"
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
APPROVED = VAULT_PATH / "Approved"
DONE = VAULT_PATH / "Done"
LOGS = VAULT_PATH / "Logs"
CREDENTIALS_FILE = Path(__file__).parent.parent.parent.parent.parent / "client_secret_546836721365-jsqg49259347e8l9kghrq80o9j3htrql.apps.googleusercontent.com.json"
TOKEN_FILE = Path(__file__).parent.parent.parent.parent.parent / "token.json"
KNOWN_CONTACTS_FILE = VAULT_PATH / "known_contacts.json"

# Gmail API scopes (includes send permission)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS / "email_sender.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EmailSender")


class EmailSender:
    """Manages email sending with approval workflow"""

    def __init__(self, vault_path: Path = VAULT_PATH):
        self.vault_path = vault_path
        self.plans = vault_path / "Plans"
        self.pending_approval = vault_path / "Pending_Approval"
        self.approved = vault_path / "Approved"
        self.done = vault_path / "Done"
        self.service = None
        self.known_contacts = self._load_known_contacts()

        # Initialize rate limiter
        self.rate_limiter = RateLimiter()

        # Ensure folders exist
        for folder in [self.plans, self.pending_approval, self.approved, self.done, LOGS]:
            folder.mkdir(parents=True, exist_ok=True)

    def _load_known_contacts(self) -> Dict:
        """Load known contacts database"""
        if KNOWN_CONTACTS_FILE.exists():
            try:
                with open(KNOWN_CONTACTS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load known contacts: {e}")
        return {"contacts": []}

    def _save_known_contacts(self):
        """Save known contacts database"""
        try:
            with open(KNOWN_CONTACTS_FILE, 'w') as f:
                json.dump(self.known_contacts, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save known contacts: {e}")

    def is_known_contact(self, email: str) -> bool:
        """Check if email is a known contact"""
        return any(c['email'].lower() == email.lower()
                   for c in self.known_contacts.get('contacts', []))

    def add_known_contact(self, email: str, name: str = ""):
        """Add email to known contacts"""
        if not self.is_known_contact(email):
            self.known_contacts['contacts'].append({
                'email': email,
                'name': name,
                'added': datetime.now().isoformat(),
                'last_contact': datetime.now().isoformat(),
                'auto_approve': False
            })
            self._save_known_contacts()
            logger.info(f"Added known contact: {email}")

    def requires_approval(self, to_email: str, subject: str, body: str,
                         attachments: List[str] = None) -> bool:
        """Determine if email requires human approval"""

        # New contact always requires approval
        if not self.is_known_contact(to_email):
            logger.info(f"Approval required: New contact ({to_email})")
            return True

        # Bulk email requires approval
        if ',' in to_email or ';' in to_email:
            logger.info("Approval required: Bulk email")
            return True

        # Email with attachments requires approval
        if attachments:
            logger.info("Approval required: Has attachments")
            return True

        # Sensitive keywords require approval
        sensitive_keywords = ['payment', 'invoice', 'contract', 'legal', 'confidential']
        if any(kw in subject.lower() or kw in body.lower() for kw in sensitive_keywords):
            logger.info("Approval required: Sensitive content")
            return True

        # Known contact, no attachments, not sensitive = auto-approve
        return False

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            except Exception as e:
                logger.warning(f"Could not load token: {e}")

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Token refreshed successfully")
                except Exception as e:
                    logger.error(f"Token refresh failed: {e}")
                    creds = None

            if not creds:
                if not CREDENTIALS_FILE.exists():
                    logger.error(f"Credentials file not found: {CREDENTIALS_FILE}")
                    logger.error("Please download OAuth2 credentials from Google Cloud Console")
                    sys.exit(1)

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("New token obtained successfully")

            # Save credentials
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API authenticated successfully")
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            sys.exit(1)

    def create_email_request(self, to: str, subject: str, body: str,
                            attachments: List[str] = None) -> Path:
        """Create email send request (draft or approval)"""
        try:
            timestamp = int(datetime.now().timestamp())

            # Check if approval needed
            needs_approval = self.requires_approval(to, subject, body, attachments)

            if needs_approval:
                folder = self.pending_approval
                status = "pending_approval"
            else:
                folder = self.plans
                status = "ready_to_send"

            filename = f"EMAIL_{to.split('@')[0]}_{timestamp}.md"
            filepath = folder / filename

            # Create markdown content
            content = f"""---
type: email_send
to: {to}
subject: {subject}
status: {status}
created: {datetime.now().isoformat()}
priority: medium
attachments: {', '.join(attachments) if attachments else 'none'}
---

# Email Send Request

## Email Details

- **To:** {to}
- **Subject:** {subject}
- **Attachments:** {', '.join(attachments) if attachments else 'None'}
- **Status:** {status}

## Email Body

{body}

## Approval Status

{'**Approval Required:** This email requires human review.' if needs_approval else '**Auto-approved:** Known contact, routine communication.'}

{'**To Approve:** Move to `/Approved/`' if needs_approval else ''}
{'**To Reject:** Move to `/Rejected/`' if needs_approval else ''}

## Notes

Add any modifications or notes here.
"""

            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Created email request: {filename} (status: {status})")

            # Log to audit trail
            self._log_action("email_request_created", {
                "file": filename,
                "to": to,
                "subject": subject,
                "status": status
            })

            return filepath

        except Exception as e:
            logger.error(f"Error creating email request: {e}")
            raise

    def send_email(self, to: str, subject: str, body: str,
                   attachments: List[str] = None) -> bool:
        """Send email via Gmail API"""
        try:
            # Check rate limit before sending
            can_send, wait_time = self.rate_limiter.can_perform("email_send")
            if not can_send:
                logger.error(f"Rate limit exceeded. Wait {wait_time:.0f} seconds before sending.")
                return False

            # Create message
            message = MIMEMultipart() if attachments else MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            if attachments:
                message.attach(MIMEText(body, 'plain'))

                # Attach files
                for filepath in attachments:
                    if Path(filepath).exists():
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition',
                                          f'attachment; filename={Path(filepath).name}')
                            message.attach(part)

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send via Gmail API
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            logger.info(f"Email sent successfully to {to}")
            logger.info(f"Message ID: {send_message['id']}")

            # Record action in rate limiter
            self.rate_limiter.record_action("email_send")

            # Add to known contacts if new
            if not self.is_known_contact(to):
                self.add_known_contact(to)

            return True

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def process_approved_emails(self):
        """Process all approved emails"""
        logger.info("Checking for approved emails...")

        approved_emails = list(self.approved.glob("EMAIL_*.md"))

        if not approved_emails:
            logger.info("No approved emails to send")
            return

        for email_file in approved_emails:
            logger.info(f"Processing: {email_file.name}")

            try:
                # Parse email file
                content = email_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                # Extract metadata
                to_email = ""
                subject = ""
                body_lines = []
                in_body = False

                for line in lines:
                    if line.startswith('to:'):
                        to_email = line.split('to:')[1].strip()
                    elif line.startswith('subject:'):
                        subject = line.split('subject:')[1].strip()
                    elif line.strip() == "## Email Body":
                        in_body = True
                        continue
                    elif line.startswith("## ") and in_body:
                        break
                    elif in_body and line.strip():
                        body_lines.append(line)

                body = '\n'.join(body_lines).strip()

                # Send email
                success = self.send_email(to_email, subject, body)

                if success:
                    # Move to Done
                    done_file = self.done / email_file.name
                    email_file.rename(done_file)

                    # Add completion note
                    with open(done_file, 'a', encoding='utf-8') as f:
                        f.write(f"\n\n## Sent\n\n")
                        f.write(f"- **Sent at:** {datetime.now().isoformat()}\n")
                        f.write(f"- **Status:** Success\n")

                    logger.info(f"✓ Sent: {email_file.name}")

                    # Log to audit trail
                    self._log_action("email_sent", {
                        "file": email_file.name,
                        "to": to_email,
                        "subject": subject,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.error(f"✗ Failed: {email_file.name}")

            except Exception as e:
                logger.error(f"Error processing {email_file.name}: {e}")

    def _log_action(self, action_type: str, details: Dict):
        """Log action to audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": "email_sender",
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


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Email Sender for AI Employee')
    parser.add_argument('--to', type=str, help='Recipient email address')
    parser.add_argument('--subject', type=str, help='Email subject')
    parser.add_argument('--body', type=str, help='Email body')
    parser.add_argument('--attach', type=str, nargs='+', help='Attachment file paths')
    parser.add_argument('--send-approved', action='store_true',
                        help='Send all approved emails')
    parser.add_argument('--auth', action='store_true',
                        help='Authenticate with Gmail API')

    args = parser.parse_args()

    sender = EmailSender()

    if args.auth:
        sender.authenticate()
        logger.info("Authentication complete")
    elif args.send_approved:
        sender.authenticate()
        sender.process_approved_emails()
    elif args.to and args.subject and args.body:
        sender.authenticate()
        email_file = sender.create_email_request(
            to=args.to,
            subject=args.subject,
            body=args.body,
            attachments=args.attach
        )
        logger.info(f"Email request created: {email_file}")

        # If auto-approved, send immediately
        if email_file.parent == sender.plans:
            logger.info("Auto-approved, sending immediately...")
            success = sender.send_email(args.to, args.subject, args.body, args.attach)
            if success:
                logger.info("✓ Email sent successfully")
            else:
                logger.error("✗ Failed to send email")
        else:
            logger.info("Approval required. Move to /Approved/ to send.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
