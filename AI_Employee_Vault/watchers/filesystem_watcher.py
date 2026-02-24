"""
File System Watcher for AI Employee

Monitors a drop folder for new files and creates action files in Needs_Action.
This is the Bronze Tier watcher - simple, reliable, and doesn't require API setup.

Usage:
    python filesystem_watcher.py /path/to/AI_Employee_Vault

Reference: Personal AI Employee Hackathon 0 - Section 2.A (Watcher Architecture)
"""

import time
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from base_watcher import BaseWatcher

# Try to import watchdog, fall back to polling if not available
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. Using polling mode instead.")
    print("Install with: pip install watchdog")


class DropFolderHandler(FileSystemEventHandler):
    """
    Handles file system events in the drop folder.
    
    When a new file is created, it triggers the watcher to process it.
    """
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        """
        Initialize the handler.
        
        Args:
            watcher: The FileSystemWatcher instance to notify
        """
        self.watcher = watcher
        
    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return
        
        self.watcher.logger.info(f'File created: {event.src_path}')
        self.watcher._process_file(Path(event.src_path))


class FileSystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files and creates action files.
    
    Two modes:
    1. Event-driven (watchdog): Real-time file system events
    2. Polling: Periodically scans the folder (fallback)
    
    Files dropped into the drop folder are:
    1. Copied to Needs_Action with metadata
    2. Logged in the watcher log
    3. Marked as processed
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None, 
                 check_interval: int = 5, use_polling: bool = False):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault directory
            drop_folder: Path to the drop folder (default: vault/Inbox)
            check_interval: Seconds between checks (default: 5 for responsive drops)
            use_polling: Force polling mode even if watchdog is available
        """
        super().__init__(vault_path, check_interval)
        
        # Set up drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.vault_path / 'Inbox'
        
        # Create drop folder if it doesn't exist
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        self.use_polling = use_polling or not WATCHDOG_AVAILABLE
        self.observer: Optional[Observer] = None
        
        # Track processed files by hash to avoid duplicates
        self.processed_hashes: set = set()
        
        self.logger.info(f'Drop folder: {self.drop_folder}')
        self.logger.info(f'Mode: {"polling" if self.use_polling else "event-driven"}')
    
    def check_for_updates(self) -> List[Path]:
        """
        Check for new files in the drop folder.
        
        In polling mode, scans the folder for new files.
        In event-driven mode, this is handled by the observer callback.
        
        Returns:
            List of new file paths to process
        """
        if self.use_polling:
            return self._scan_drop_folder()
        return []
    
    def _scan_drop_folder(self) -> List[Path]:
        """
        Scan the drop folder for files (polling mode).
        
        Returns:
            List of new file paths
        """
        new_files = []
        
        try:
            for file_path in self.drop_folder.iterdir():
                if file_path.is_file() and not file_path.name.endswith('.md'):
                    # Check if already processed
                    file_hash = self._get_file_hash(file_path)
                    if file_hash not in self.processed_hashes:
                        new_files.append(file_path)
                        self.processed_hashes.add(file_hash)
        except Exception as e:
            self.logger.error(f'Error scanning drop folder: {e}')
        
        return new_files
    
    def _wait_for_file_ready(self, file_path: Path, max_wait: float = 2.0) -> bool:
        """
        Wait for a file to be fully written before processing.
        
        Args:
            file_path: Path to the file
            max_wait: Maximum time to wait in seconds
            
        Returns:
            True if file is ready, False if timeout
        """
        try:
            initial_size = file_path.stat().st_size
            wait_time = 0.0
            step = 0.1  # Check every 100ms
            
            while wait_time < max_wait:
                time.sleep(step)
                wait_time += step
                try:
                    current_size = file_path.stat().st_size
                    if current_size == initial_size and current_size > 0:
                        # File size stable and non-zero
                        return True
                    initial_size = current_size
                except FileNotFoundError:
                    return False
            return True  # Timeout but proceed anyway
        except Exception as e:
            self.logger.warning(f'Error waiting for file {file_path}: {e}')
            return True  # Proceed anyway on error
    
    def _process_file(self, file_path: Path):
        """
        Process a single file from the drop folder.
        
        Args:
            file_path: Path to the file to process
        """
        try:
            # Skip markdown files (they're already action files)
            if file_path.suffix == '.md':
                self.logger.debug(f'Skipping markdown file: {file_path.name}')
                return
            
            # Wait for file to be fully written
            self.logger.debug(f'Waiting for file to be ready: {file_path.name}')
            self._wait_for_file_ready(file_path)
            
            # Check if already processed
            file_hash = self._get_file_hash(file_path)
            if file_hash in self.processed_hashes:
                self.logger.debug(f'File already processed: {file_path.name}')
                return
            
            # Create action file
            action_file = self.create_action_file(file_path)
            
            if action_file:
                self.logger.info(f'Processed file: {file_path.name} -> {action_file.name}')
                self.processed_hashes.add(file_hash)
                self.save_processed_state()
                
        except Exception as e:
            self.logger.error(f'Error processing file {file_path}: {e}')
    
    def create_action_file(self, file_path: Path) -> Optional[Path]:
        """
        Create a markdown action file for a dropped file.
        
        Args:
            file_path: Path to the dropped file
            
        Returns:
            Path to the created action file, or None if failed
        """
        try:
            # Get file metadata
            stat = file_path.stat()
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Calculate file hash for deduplication
            file_hash = self._get_file_hash(file_path)
            
            # Create unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = self.sanitize_filename(file_path.name)
            action_filename = f'FILEDROP_{safe_name}_{timestamp}.md'
            action_path = self.needs_action / action_filename
            
            # Copy the file to Needs_Action folder
            dest_path = self.needs_action / f'FILEDROP_{safe_name}_{timestamp}{file_path.suffix}'
            shutil.copy2(file_path, dest_path)
            
            # Create the markdown action file
            content = f'''---
type: file_drop
original_name: {file_path.name}
dropped_name: {dest_path.name}
size: {file_size}
size_human: {self._format_size(file_size)}
received: {self.get_timestamp()}
modified: {modified_time}
hash: {file_hash}
status: pending
priority: normal
---

# File Drop for Processing

## File Information

- **Original Name:** {file_path.name}
- **Stored As:** {dest_path.name}
- **Size:** {self._format_size(file_size)}
- **Received:** {self.get_timestamp()}

## Content Preview

<!-- AI Employee: Analyze this file and suggest actions -->

## Suggested Actions

- [ ] Review file content
- [ ] Categorize file type
- [ ] Take appropriate action
- [ ] Move to /Done when complete

## Notes

<!-- Add any additional context or instructions here -->

---
*Created by FileSystemWatcher v0.1.0*
'''
            
            action_path.write_text(content, encoding='utf-8')
            self.logger.info(f'Created action file: {action_path.name}')
            
            return action_path
            
        except Exception as e:
            self.logger.error(f'Failed to create action file: {e}')
            return None
    
    def _get_file_hash(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of a file for deduplication.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.warning(f'Could not hash file {file_path}: {e}')
            return str(file_path)  # Fallback to path as identifier
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Human-readable size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f'{size_bytes:.2f} {unit}'
            size_bytes /= 1024.0
        return f'{size_bytes:.2f} TB'
    
    def run_event_driven(self):
        """
        Run the watcher in event-driven mode using watchdog.
        
        This provides real-time file detection instead of polling.
        """
        if not WATCHDOG_AVAILABLE:
            self.logger.warning('watchdog not available, falling back to polling')
            self.run()
            return
        
        self.running = True
        self.logger.info(f'Starting {self.__class__.__name__} (event-driven mode)')
        self.logger.info(f'Drop folder: {self.drop_folder}')
        
        try:
            # Set up the observer
            event_handler = DropFolderHandler(self)
            self.observer = Observer()
            self.observer.schedule(event_handler, str(self.drop_folder), recursive=False)
            self.observer.start()
            self.logger.info(f'Watching: {self.drop_folder}')
            
            # Load previous state
            self.load_processed_state()
            
            # Keep running until stopped
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Error in event-driven watcher: {e}', exc_info=True)
            raise
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()
            self.running = False
            self.save_processed_state()
            self.logger.info(f'{self.__class__.__name__} shutdown complete')
    
    def stop(self):
        """Stop the watcher."""
        self.running = False
        if self.observer:
            self.observer.stop()


# CLI entry point
if __name__ == '__main__':
    import sys

    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Default to parent directory (AI_Employee_Vault)
        vault_path = str(Path(__file__).parent.parent)
    
    print(f"AI Employee FileSystemWatcher v0.1.0")
    print(f"Vault: {vault_path}")
    print(f"Drop folder: {vault_path}/Inbox")
    print(f"Mode: {'polling' if not WATCHDOG_AVAILABLE else 'event-driven'}")
    print()
    print("Drop files into the Inbox folder to create action items.")
    print("Press Ctrl+C to stop.")
    print()
    
    # Create and run watcher
    watcher = FileSystemWatcher(vault_path)
    
    try:
        if WATCHDOG_AVAILABLE and not watcher.use_polling:
            watcher.run_event_driven()
        else:
            watcher.run()
    except KeyboardInterrupt:
        print("\nWatcher stopped.")
