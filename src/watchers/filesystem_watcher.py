#!/usr/bin/env python3
"""
File System Watcher for AI Employee
Monitors a drop folder and creates action files in Needs_Action
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher
from retry_handler import with_retry

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
DROP_FOLDER = Path.home() / "AI_Employee_Drop"
PROCESSED_FILE = VAULT_PATH / ".processed_files"


class FileSystemWatcher(BaseWatcher):
    """Monitors drop folder for new files"""

    def __init__(self, vault_path: Path = VAULT_PATH, check_interval: int = 5):
        super().__init__(vault_path, check_interval, "FileSystemWatcher")
        self.drop_folder = DROP_FOLDER
        self.processed_files = self._load_processed_files()
        self.pending_files = []

        # Ensure drop folder exists
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Drop folder ready: {self.drop_folder}")

    def _load_processed_files(self) -> set:
        """Load set of already processed files"""
        if PROCESSED_FILE.exists():
            try:
                with open(PROCESSED_FILE, 'r') as f:
                    return set(json.load(f))
            except Exception as e:
                self.logger.warning(f"Could not load processed files: {e}")
        return set()

    def _save_processed_files(self):
        """Save processed files to avoid duplicates"""
        try:
            with open(PROCESSED_FILE, 'w') as f:
                json.dump(list(self.processed_files), f)
        except Exception as e:
            self.logger.error(f"Could not save processed files: {e}")

    @with_retry(max_attempts=2, base_delay=1, max_delay=5)
    def check_for_updates(self) -> List[Any]:
        """Check drop folder for new files"""
        try:
            new_files = []

            # Check all files in drop folder
            if not self.drop_folder.exists():
                return []

            for file_path in self.drop_folder.iterdir():
                # Skip directories and hidden files
                if file_path.is_dir() or file_path.name.startswith('.'):
                    continue

                # Skip if already processed
                if str(file_path) in self.processed_files:
                    continue

                # Check if file is fully written (size stable)
                try:
                    size1 = file_path.stat().st_size
                    time.sleep(0.5)
                    size2 = file_path.stat().st_size

                    if size1 == size2:  # File is stable
                        new_files.append(file_path)
                        self.logger.info(f"New file detected: {file_path.name}")
                except Exception as e:
                    self.logger.warning(f"Error checking file {file_path}: {e}")
                    continue

            return new_files

        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return []

    def create_action_file(self, item: Any) -> Optional[Path]:
        """Create a markdown action file for the dropped file"""
        try:
            source_path = item

            # Get file info
            file_size = source_path.stat().st_size
            file_ext = source_path.suffix
            timestamp = datetime.now().isoformat()

            # Create action file name
            action_filename = f"FILE_{source_path.stem}_{int(time.time())}.md"
            action_filepath = self.needs_action / action_filename

            # Create markdown content
            content = f"""---
type: file_drop
original_name: {source_path.name}
file_path: {source_path}
size_bytes: {file_size}
file_type: {file_ext if file_ext else 'unknown'}
detected_at: {timestamp}
status: pending
priority: medium
---

# File Drop Detected

A new file has been dropped for processing.

## File Details

- **Name:** {source_path.name}
- **Size:** {file_size:,} bytes
- **Type:** {file_ext if file_ext else 'Unknown'}
- **Path:** {source_path}
- **Detected:** {timestamp}

## Actions

- [ ] Review file contents
- [ ] Determine action needed
- [ ] Process or archive
- [ ] Move to /Done when complete

## Notes

Add any processing notes here.
"""

            # Write action file
            action_filepath.write_text(content)
            self.logger.info(f"Created action file: {action_filename}")

            # Mark as processed
            self.processed_files.add(str(source_path))
            self._save_processed_files()

            return action_filepath

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='File System Watcher for AI Employee')
    parser.add_argument('--interval', type=int, default=5,
                        help='Check interval in seconds (default: 5)')
    parser.add_argument('--test', action='store_true',
                        help='Test mode: check once and exit')

    args = parser.parse_args()

    watcher = FileSystemWatcher(check_interval=args.interval)

    if args.test:
        watcher.logger.info("Running in test mode...")
        files = watcher.check_for_updates()
        watcher.logger.info(f"Found {len(files)} new file(s)")
        for file in files:
            watcher.create_action_file(file)
        watcher.logger.info("Test complete")
    else:
        watcher.run()


if __name__ == "__main__":
    main()
