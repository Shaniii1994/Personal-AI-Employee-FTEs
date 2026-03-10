"""
LinkedIn Poster for AI Employee

Automatically creates and publishes LinkedIn posts to promote business and generate sales.
Uses Playwright for browser automation.

Usage:
    python linkedin_poster.py --action create     # Create post draft
    python linkedin_poster.py --action publish    # Publish scheduled posts
    python linkedin_poster.py --action list       # List all drafts

Reference: Personal AI Employee Hackathon 0 - Silver Tier
"""

import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Import base watcher from same directory
import sys
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Playwright imports (optional - only needed for publishing)
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: playwright not installed. Run: pip install playwright && playwright install chromium")


# Default configuration
DEFAULT_CONFIG = {
    'check_interval': 3600,  # 1 hour for checking scheduled posts
    'post_schedule_hours': [9, 12, 15],  # Best posting times
    'max_posts_per_day': 3,
    'session_path': 'linkedin_session',
}


class LinkedInPoster(BaseWatcher):
    """
    Creates and publishes LinkedIn posts for business promotion.
    
    Attributes:
        session_path: Path to store browser session
        posts_folder: Path to store post drafts
        content_calendar: Path to content calendar file
    """
    
    def __init__(self, vault_path: str,
                 check_interval: int = DEFAULT_CONFIG['check_interval'],
                 session_path: Optional[str] = None,
                 max_posts_per_day: int = DEFAULT_CONFIG['max_posts_per_day']):
        """
        Initialize the LinkedIn Poster.
        
        Args:
            vault_path: Path to the Obsidian vault directory
            check_interval: Seconds between checks (default: 3600)
            session_path: Path to store browser session
            max_posts_per_day: Maximum posts to publish per day
        """
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path) if session_path else self.vault_path / 'linkedin_session'
        self.posts_folder = self.vault_path / 'Posts'
        self.content_calendar = self.vault_path / 'Content_Calendar.md'
        self.max_posts_per_day = max_posts_per_day
        
        # Create posts folder
        self.posts_folder.mkdir(parents=True, exist_ok=True)
        
        # Load processed state
        self.load_processed_state('linkedin_processed_state.json')
        
        self.logger.info(f'Posts folder: {self.posts_folder}')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Max posts/day: {self.max_posts_per_day}')
    
    def create_post(self, topic: str, content: str, 
                    hashtags: List[str] = None,
                    scheduled_time: Optional[datetime] = None,
                    media_paths: List[str] = None) -> Optional[Path]:
        """
        Create a LinkedIn post draft.
        
        Args:
            topic: Post topic/category
            content: Main post content
            hashtags: List of hashtags
            scheduled_time: When to publish (default: next optimal time)
            media_paths: Paths to images/media to include
            
        Returns:
            Path to created post file, or None if failed
        """
        try:
            # Default hashtags if not provided
            if hashtags is None:
                hashtags = ['#Business', '#Professional', '#Growth']
            
            # Default scheduled time (next optimal slot)
            if scheduled_time is None:
                scheduled_time = self._get_next_optimal_time()
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_topic = self._sanitize_filename(topic)[:30]
            filename = f'LINKEDIN_POST_{safe_topic}_{timestamp}.md'
            filepath = self.posts_folder / filename
            
            # Create post content
            content_md = f'''---
type: linkedin_post
topic: {topic}
status: draft
created: {self.get_timestamp()}
scheduled: {scheduled_time.isoformat()}
hashtags: {', '.join(hashtags)}
media: {', '.join(media_paths) if media_paths else 'None'}
---

# LinkedIn Post: {topic}

## Content

{content}

## Hashtags

{' '.join(hashtags)}

## Media

{self._format_media_list(media_paths)}

## Engagement Goals

- Target impressions: 1000+
- Target engagements: 50+
- Target leads: 5+

## Publishing Status

- [ ] Review content
- [ ] Check media attachments
- [ ] Publish at scheduled time
- [ ] Monitor engagement

---
*Created by LinkedInPoster v0.1.0*
'''
            
            filepath.write_text(content_md, encoding='utf-8')
            
            self.logger.info(f'Created post draft: {filename}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Failed to create post: {e}')
            return None
    
    def _format_media_list(self, media_paths: Optional[List[str]]) -> str:
        """Format media paths for display."""
        if not media_paths:
            return 'No media attached'
        
        return '\n'.join([f'- {path}' for path in media_paths])
    
    def _get_next_optimal_time(self) -> datetime:
        """Get next optimal posting time."""
        now = datetime.now()
        
        # Check today's remaining slots
        for hour in DEFAULT_CONFIG['post_schedule_hours']:
            candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if candidate > now:
                return candidate
        
        # If no slots left today, get tomorrow's first slot
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=DEFAULT_CONFIG['post_schedule_hours'][0], 
                                minute=0, second=0, microsecond=0)
    
    def list_drafts(self) -> List[Path]:
        """List all draft posts."""
        drafts = []
        for filepath in self.posts_folder.glob('LINKEDIN_POST_*.md'):
            content = filepath.read_text()
            if 'status: draft' in content:
                drafts.append(filepath)
        return drafts
    
    def list_scheduled(self) -> List[Path]:
        """List all scheduled posts."""
        scheduled = []
        for filepath in self.posts_folder.glob('LINKEDIN_POST_*.md'):
            content = filepath.read_text()
            if 'status: scheduled' in content:
                scheduled.append(filepath)
        return scheduled
    
    def publish_post(self, post_path: Path) -> bool:
        """
        Publish a LinkedIn post using Playwright.
        
        Args:
            post_path: Path to post markdown file
            
        Returns:
            True if published successfully, False otherwise
        """
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error('Playwright not available. Install with: pip install playwright')
            return False
        
        try:
            # Read post content
            content = post_path.read_text(encoding='utf-8')
            
            # Parse frontmatter
            post_data = self._parse_frontmatter(content)
            
            # Extract post text (after frontmatter)
            post_text = self._extract_post_text(content)
            
            self.logger.info(f'Publishing post: {post_path.name}')
            self.logger.info(f'Topic: {post_data.get("topic", "Unknown")}')
            
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Show browser for debugging
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                self.logger.info('Navigating to LinkedIn...')
                page.goto('https://www.linkedin.com/feed/', timeout=60000)
                
                # Wait for page to load
                try:
                    page.wait_for_selector('[aria-label="Start a post"]', timeout=10000)
                except PlaywrightTimeout:
                    self.logger.warning('LinkedIn may require login. Please login manually.')
                    # Wait for user to login
                    page.wait_for_timeout(30000)
                
                # Click "Start a post"
                self.logger.info('Clicking "Start a post"...')
                post_button = page.query_selector('[aria-label="Start a post"]')
                if post_button:
                    post_button.click()
                    page.wait_for_timeout(2000)
                else:
                    self.logger.error('Could not find post button')
                    browser.close()
                    return False
                
                # Find and fill post text area
                self.logger.info('Entering post content...')
                text_area = page.query_selector('div[contenteditable="true"]')
                if text_area:
                    text_area.fill(post_text)
                    page.wait_for_timeout(1000)
                else:
                    self.logger.error('Could not find text area')
                    browser.close()
                    return False
                
                # Add media if specified
                media_paths = post_data.get('media', 'None')
                if media_paths and media_paths != 'None':
                    self.logger.info('Adding media...')
                    # Click media button
                    media_button = page.query_selector('input[type="file"]')
                    if media_button:
                        # Note: Actual media upload requires more complex handling
                        self.logger.warning('Media upload requires additional implementation')
                
                # Click "Post" button
                self.logger.info('Publishing post...')
                post_submit = page.query_selector('button:has-text("Post")')
                if post_submit:
                    post_submit.click()
                    page.wait_for_timeout(3000)
                    
                    # Verify post was published
                    self.logger.info('Post published successfully!')
                    
                    # Update post status
                    self._mark_post_published(post_path)
                    
                    browser.close()
                    return True
                else:
                    self.logger.error('Could not find Post button')
                    browser.close()
                    return False
                    
        except Exception as e:
            self.logger.error(f'Failed to publish post: {e}')
            return False
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from markdown."""
        import re
        match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        if match:
            frontmatter = match.group(1)
            data = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip()
            return data
        return {}
    
    def _extract_post_text(self, content: str) -> str:
        """Extract post text from markdown (after frontmatter and headers)."""
        import re
        # Remove frontmatter
        content = re.sub(r'---\n.*?\n---\n', '', content, flags=re.DOTALL)
        
        # Remove headers
        lines = content.split('\n')
        text_lines = []
        in_content = False
        
        for line in lines:
            if line.startswith('## Content'):
                in_content = True
                continue
            elif line.startswith('##'):
                in_content = False
                continue
            elif in_content and not line.startswith('#'):
                text_lines.append(line)
        
        return '\n'.join(text_lines).strip()
    
    def _mark_post_published(self, post_path: Path):
        """Update post status to published."""
        content = post_path.read_text(encoding='utf-8')
        content = content.replace('status: draft', 'status: published')
        content = content.replace(f'published: {self.get_timestamp()}', f'published: {self.get_timestamp()}')
        
        # Add published date if not present
        if 'published:' not in content:
            content = content.replace(
                f'created: {self.get_timestamp()}',
                f'created: {self.get_timestamp()}\npublished: {self.get_timestamp()}'
            )
        
        post_path.write_text(content, encoding='utf-8')
        
        # Move to published folder
        published_folder = self.vault_path / 'Posts' / 'Published'
        published_folder.mkdir(parents=True, exist_ok=True)
        
        dest = published_folder / post_path.name
        post_path.rename(dest)
        
        self.logger.info(f'Moved published post to: {dest}')
    
    def check_for_updates(self) -> List[Path]:
        """Check for posts ready to publish."""
        scheduled = self.list_scheduled()
        now = datetime.now()
        
        ready_to_publish = []
        for post_path in scheduled:
            content = post_path.read_text()
            data = self._parse_frontmatter(content)
            
            scheduled_str = data.get('scheduled', '')
            if scheduled_str:
                try:
                    scheduled_time = datetime.fromisoformat(scheduled_str)
                    if scheduled_time <= now:
                        ready_to_publish.append(post_path)
                except ValueError:
                    pass
        
        return ready_to_publish
    
    def create_action_file(self, item: Path) -> Optional[Path]:
        """Create action file for post that needs attention."""
        # For LinkedIn, we just track in the post file itself
        return None
    
    def generate_content_calendar(self) -> Path:
        """Generate/update content calendar."""
        drafts = self.list_drafts()
        scheduled = self.list_scheduled()
        
        content = f'''# LinkedIn Content Calendar

Generated: {self.get_timestamp()}

## Draft Posts ({len(drafts)})

| File | Topic | Created |
|------|-------|---------|
'''
        
        for draft in drafts:
            data = self._parse_frontmatter(draft.read_text())
            topic = data.get('topic', 'Unknown')
            created = data.get('created', 'Unknown')
            content += f'| {draft.name} | {topic} | {created} |\n'
        
        content += f'''
## Scheduled Posts ({len(scheduled)})

| File | Topic | Scheduled |
|------|-------|-----------|
'''
        
        for post in scheduled:
            data = self._parse_frontmatter(post.read_text())
            topic = data.get('topic', 'Unknown')
            scheduled = data.get('scheduled', 'Unknown')
            content += f'| {post.name} | {topic} | {scheduled} |\n'
        
        calendar_path = self.vault_path / 'Content_Calendar.md'
        calendar_path.write_text(content, encoding='utf-8')
        
        self.logger.info(f'Generated content calendar: {calendar_path}')
        return calendar_path


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument(
        '--action',
        choices=['create', 'publish', 'list', 'schedule', 'calendar'],
        default='list',
        help='Action to perform'
    )
    parser.add_argument(
        '--vault-path',
        default=str(Path(__file__).parent.parent),
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--topic',
        default='Business Update',
        help='Post topic'
    )
    parser.add_argument(
        '--content',
        default='',
        help='Post content'
    )
    parser.add_argument(
        '--hashtags',
        nargs='+',
        default=['#Business', '#Professional', '#Growth'],
        help='Hashtags'
    )
    
    args = parser.parse_args()
    
    # Create poster
    poster = LinkedInPoster(vault_path=args.vault_path)
    
    if args.action == 'create':
        # Create new post draft
        if not args.content:
            print("Error: --content required for create action")
            sys.exit(1)
        
        result = poster.create_post(
            topic=args.topic,
            content=args.content,
            hashtags=args.hashtags
        )
        
        if result:
            print(f'\n✅ Post created: {result}')
            print('Review and schedule with: python linkedin_poster.py --action schedule')
        else:
            print('\n❌ Failed to create post')
            sys.exit(1)
    
    elif args.action == 'publish':
        # Publish scheduled posts
        print('Checking for posts to publish...')
        ready = poster.check_for_updates()
        
        if ready:
            print(f'Found {len(ready)} post(s) ready to publish')
            for post in ready:
                print(f'Publishing: {post.name}')
                success = poster.publish_post(post)
                if success:
                    print(f'✅ Published: {post.name}')
                else:
                    print(f'❌ Failed: {post.name}')
        else:
            print('No posts ready to publish')
            print('Create drafts with: python linkedin_poster.py --action create')
    
    elif args.action == 'list':
        # List all drafts and scheduled
        drafts = poster.list_drafts()
        scheduled = poster.list_scheduled()
        
        print(f'\n📝 Draft Posts ({len(drafts)}):')
        for draft in drafts:
            data = poster._parse_frontmatter(draft.read_text())
            topic = data.get('topic', 'Unknown')
            print(f'  - {draft.name} ({topic})')
        
        print(f'\n📅 Scheduled Posts ({len(scheduled)}):')
        for post in scheduled:
            data = poster._parse_frontmatter(post.read_text())
            topic = data.get('topic', 'Unknown')
            scheduled_time = data.get('scheduled', 'Unknown')
            print(f'  - {post.name} ({topic}) - {scheduled_time}')
    
    elif args.action == 'calendar':
        # Generate content calendar
        calendar = poster.generate_content_calendar()
        print(f'\n📅 Content calendar generated: {calendar}')
    
    elif args.action == 'schedule':
        print('Scheduling requires interactive selection. Use Qwen Code to update post status.')


if __name__ == '__main__':
    main()
