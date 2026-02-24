"""
Base Watcher Class for AI Employee

All watcher scripts (Gmail, WhatsApp, FileSystem, etc.) inherit from this base class.
Provides common functionality for monitoring, logging, and creating action files.

Reference: Personal AI Employee Hackathon 0 - Section 2.A (Watcher Architecture)
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional
import json


class BaseWatcher(ABC):
    """
    Abstract base class for all AI Employee watchers.
    
    Watchers are lightweight Python scripts that run continuously in the background,
    monitoring various inputs and creating actionable .md files for Claude to process.
    
    Attributes:
        vault_path: Path to the Obsidian vault root
        needs_action: Path to the /Needs_Action folder
        check_interval: Seconds between checks (default: 60)
        processed_ids: Set of already processed item IDs to avoid duplicates
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the base watcher.
        
        Args:
            vault_path: Path to the Obsidian vault directory
            check_interval: How often to check for new items (in seconds)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.processed_ids: set = set()
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        # Ensure Needs_Action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
    def _setup_logging(self):
        """Configure logging to file and console."""
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'watcher_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items to process.
        
        Returns:
            List of new items that need action files created
            
        Example:
            For Gmail watcher: List of message dicts
            For WhatsApp watcher: List of message dicts
            For FileSystem watcher: List of file paths
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created action file, or None if failed
            
        The action file should include:
            - YAML frontmatter with metadata
            - Content section
            - Suggested actions checklist
        """
        pass
    
    def run(self):
        """
        Main run loop for the watcher.
        
        Continuously checks for updates and creates action files.
        Runs until stopped or interrupted.
        """
        self.running = True
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while self.running:
                try:
                    items = self.check_for_updates()
                    self.logger.debug(f'Found {len(items)} new items')
                    
                    for item in items:
                        filepath = self.create_action_file(item)
                        if filepath:
                            self.logger.info(f'Created action file: {filepath.name}')
                            
                except Exception as e:
                    self.logger.error(f'Error processing items: {e}', exc_info=True)
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise
        finally:
            self.running = False
            self.logger.info(f'{self.__class__.__name__} shutdown complete')
    
    def stop(self):
        """Stop the watcher loop."""
        self.running = False
        self.logger.info(f'Stopping {self.__class__.__name__}')
    
    def mark_processed(self, item_id: str):
        """
        Mark an item as processed to avoid duplicate processing.
        
        Args:
            item_id: Unique identifier for the item
        """
        self.processed_ids.add(item_id)
        self.logger.debug(f'Marked {item_id} as processed')
    
    def is_processed(self, item_id: str) -> bool:
        """
        Check if an item has already been processed.
        
        Args:
            item_id: Unique identifier for the item
            
        Returns:
            True if already processed, False otherwise
        """
        return item_id in self.processed_ids
    
    def load_processed_state(self, state_file: str = 'processed_state.json'):
        """
        Load processed item state from file (for persistence across restarts).
        
        Args:
            state_file: Name of the state file in vault root
        """
        state_path = self.vault_path / state_file
        if state_path.exists():
            try:
                with open(state_path, 'r') as f:
                    data = json.load(f)
                    self.processed_ids = set(data.get('processed_ids', []))
                    self.logger.info(f'Loaded {len(self.processed_ids)} processed IDs from state')
            except Exception as e:
                self.logger.warning(f'Failed to load state: {e}')
    
    def save_processed_state(self, state_file: str = 'processed_state.json'):
        """
        Save processed item state to file (for persistence across restarts).
        
        Args:
            state_file: Name of the state file in vault root
        """
        state_path = self.vault_path / state_file
        try:
            with open(state_path, 'w') as f:
                json.dump({
                    'processed_ids': list(self.processed_ids),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
            self.logger.debug(f'Saved {len(self.processed_ids)} processed IDs to state')
        except Exception as e:
            self.logger.warning(f'Failed to save state: {e}')
    
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_date_string(self) -> str:
        """Get current date string for filenames."""
        return datetime.now().strftime('%Y-%m-%d')
    
    def sanitize_filename(self, name: str) -> str:
        """
        Sanitize a string for use in filenames.
        
        Args:
            name: The original name
            
        Returns:
            Sanitized filename-safe string
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|？*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip()


# Example usage and testing
if __name__ == '__main__':
    print("BaseWatcher is an abstract class and cannot be instantiated directly.")
    print("Inherit from it to create specific watchers:")
    print("  - GmailWatcher")
    print("  - WhatsAppWatcher")
    print("  - FileSystemWatcher")
