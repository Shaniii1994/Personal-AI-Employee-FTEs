"""
Gmail Watcher for AI Employee

Monitors Gmail for unread/important emails and creates action files in Needs_Action.
Uses Gmail API with OAuth 2.0 authentication.

Usage:
    python gmail_watcher.py  # Start watching
    python gmail_watcher.py --authenticate  # First-time authentication

Reference: Personal AI Employee Hackathon 0 - Section 2.A (Watcher Architecture)
"""

import os
import json
import pickle
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import base watcher from same directory
import sys
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail_readonly',
    'https://www.googleapis.com/auth/gmail_labels',
    'https://www.googleapis.com/auth/gmail_modify'
]

# Default configuration
DEFAULT_CONFIG = {
    'check_interval': 120,  # seconds
    'gmail_query': 'is:unread is:important',
    'max_results': 50,
}


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new important/unread emails and creates action files.
    
    Attributes:
        credentials_path: Path to credentials.json
        token_path: Path to stored OAuth token
        gmail_query: Gmail search query for filtering emails
        max_results: Maximum emails to fetch per check
    """
    
    def __init__(self, vault_path: str, credentials_path: str,
                 token_path: Optional[str] = None,
                 check_interval: int = 120,
                 gmail_query: str = 'is:unread is:important',
                 max_results: int = 50):
        """
        Initialize the Gmail Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault directory
            credentials_path: Path to credentials.json from Google Cloud
            token_path: Path to store/load OAuth token (default: token.json in same dir)
            check_interval: Seconds between checks (default: 120)
            gmail_query: Gmail search query (default: is:unread is:important)
            max_results: Maximum emails to fetch (default: 50)
        """
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path) if token_path else self.credentials_path.parent / 'token.json'
        self.gmail_query = gmail_query
        self.max_results = max_results
        self.service = None
        
        # Load processed state
        self.load_processed_state('gmail_processed_state.json')
        
        self.logger.info(f'Credentials: {self.credentials_path}')
        self.logger.info(f'Token: {self.token_path}')
        self.logger.info(f'Query: {self.gmail_query}')
    
    def authenticate(self) -> bool:
        """
        Perform OAuth 2.0 authentication.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            if not self.credentials_path.exists():
                self.logger.error(f'Credentials file not found: {self.credentials_path}')
                return False
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, SCOPES
            )
            
            # Run local server for authentication
            creds = flow.run_local_server(port=0, open_browser=True)
            
            # Save token for future use
            self._save_token(creds)
            
            self.logger.info('Authentication successful!')
            return True
            
        except Exception as e:
            self.logger.error(f'Authentication failed: {e}')
            return False
    
    def _load_credentials(self) -> Optional[Credentials]:
        """Load credentials from token file."""
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_path, SCOPES
                )
                
                # Check if credentials are still valid
                if creds and creds.valid:
                    return creds
                elif creds and creds.expired and creds.refresh_token:
                    # Refresh expired credentials
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                    self._save_token(creds)
                    return creds
                    
            except Exception as e:
                self.logger.warning(f'Failed to load credentials: {e}')
        
        return None
    
    def _save_token(self, creds: Credentials):
        """Save credentials to token file."""
        try:
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'w') as f:
                json.dump({
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }, f, indent=2)
            self.logger.info(f'Token saved to {self.token_path}')
        except Exception as e:
            self.logger.error(f'Failed to save token: {e}')
    
    def connect(self) -> bool:
        """
        Connect to Gmail API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            creds = self._load_credentials()
            
            if not creds:
                self.logger.warning('No valid credentials. Please authenticate first.')
                self.logger.info('Run: python gmail_watcher.py --authenticate')
                return False
            
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Connected to Gmail API')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to connect to Gmail API: {e}')
            return False
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new unread/important emails.
        
        Returns:
            List of email message dicts
        """
        if not self.service:
            return []
        
        try:
            # Fetch messages matching query
            results = self.service.users().messages().list(
                userId='me',
                q=self.gmail_query,
                maxResults=self.max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = [
                m for m in messages
                if m['id'] not in self.processed_ids
            ]
            
            self.logger.debug(f'Found {len(messages)} messages, {len(new_messages)} new')
            
            return new_messages
            
        except HttpError as e:
            self.logger.error(f'Gmail API error: {e}')
            if e.resp.status == 401:
                self.logger.warning('Credentials expired, please re-authenticate')
            return []
        except Exception as e:
            self.logger.error(f'Error checking for updates: {e}')
            return []
    
    def create_action_file(self, message: Dict[str, Any]) -> Optional[Path]:
        """
        Create a markdown action file for an email.
        
        Args:
            message: Gmail message dict with 'id' key
            
        Returns:
            Path to created action file, or None if failed
        """
        try:
            # Fetch full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date', 'Cc']
            ).execute()
            
            # Extract headers
            headers = msg.get('payload', {}).get('headers', [])
            email_data = {h['name']: h['value'] for h in headers}
            
            # Get snippet
            snippet = msg.get('snippet', '')
            
            # Get labels
            labels = [l['name'] for l in msg.get('labelIds', [])]
            
            # Parse date
            date_str = email_data.get('Date', '')
            
            # Create filename
            safe_subject = self._sanitize_filename(email_data.get('Subject', 'No Subject')[:50])
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'EMAIL_{safe_subject}_{timestamp}.md'
            filepath = self.needs_action / filename
            
            # Create action file content
            content = f'''---
type: email
from: {email_data.get('From', 'Unknown')}
to: {email_data.get('To', 'me')}
subject: {email_data.get('Subject', 'No Subject')}
received: {date_str}
processed: {self.get_timestamp()}
priority: high
status: pending
gmail_id: {message['id']}
labels: {', '.join(labels)}
---

# Email for Processing

## Sender Information
- **From:** {email_data.get('From', 'Unknown')}
- **To:** {email_data.get('To', 'me')}
- **Subject:** {email_data.get('Subject', 'No Subject')}
- **Received:** {date_str}
- **Labels:** {', '.join(labels)}

## Email Content

{snippet}

## Suggested Actions

- [ ] Read full email content
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Mark as read in Gmail

## Notes

<!-- Add any additional context or instructions here -->

---
*Created by GmailWatcher v0.1.0*
'''
            
            filepath.write_text(content, encoding='utf-8')
            
            # Mark as processed
            self.mark_processed(message['id'])
            self.save_processed_state('gmail_processed_state.json')
            
            self.logger.info(f'Created action file: {filename}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Failed to create action file: {e}')
            return None
    
    def mark_as_read(self, gmail_id: str) -> bool:
        """
        Mark an email as read in Gmail.
        
        Args:
            gmail_id: Gmail message ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.service:
                return False
            
            self.service.users().messages().modify(
                userId='me',
                id=gmail_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            self.logger.info(f'Marked email {gmail_id} as read')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to mark email as read: {e}')
            return False
    
    def run(self):
        """Main run loop for the Gmail watcher."""
        self.logger.info('Starting GmailWatcher')
        
        # Connect to Gmail API
        if not self.connect():
            self.logger.error('Failed to connect to Gmail API')
            return
        
        # Run the watcher loop
        super().run()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument(
        '--authenticate',
        action='store_true',
        help='Perform OAuth authentication'
    )
    parser.add_argument(
        '--vault-path',
        default=str(Path(__file__).parent.parent),
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--credentials',
        default=str(Path(__file__).parent.parent.parent / 'credentials.json'),
        help='Path to credentials.json'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=DEFAULT_CONFIG['check_interval'],
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--query',
        default=DEFAULT_CONFIG['gmail_query'],
        help='Gmail search query'
    )
    
    args = parser.parse_args()
    
    # Create watcher
    watcher = GmailWatcher(
        vault_path=args.vault_path,
        credentials_path=args.credentials,
        check_interval=args.interval,
        gmail_query=args.query
    )
    
    if args.authenticate:
        # Run authentication
        success = watcher.authenticate()
        if success:
            print('\n✅ Authentication successful!')
            print('You can now run the watcher: python gmail_watcher.py')
        else:
            print('\n❌ Authentication failed!')
            sys.exit(1)
    else:
        # Run watcher
        print(f"Gmail Watcher v0.1.0")
        print(f"Vault: {args.vault_path}")
        print(f"Credentials: {args.credentials}")
        print(f"Query: {args.query}")
        print(f"Interval: {args.interval}s")
        print()
        print("Monitoring Gmail for unread/important emails...")
        print("Press Ctrl+C to stop.")
        print()
        
        watcher.run()


if __name__ == '__main__':
    main()
