#!/usr/bin/env python3
"""
Base Watcher Class for AI Employee
Abstract base class that all watchers should inherit from
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Any, Optional
from datetime import datetime


class BaseWatcher(ABC):
    """
    Abstract base class for all watchers in the AI Employee system.

    All watchers should inherit from this class and implement:
    - check_for_updates(): Check external source for new items
    - create_action_file(): Create markdown file in Needs_Action
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize base watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

        # Ensure required folders exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for this watcher"""
        log_file = self.logs / f"{self.__class__.__name__.lower()}.log"

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check external source for new items to process.

        Returns:
            List of new items to process (format depends on watcher type)
        """
        pass

    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a markdown action file in Needs_Action folder.

        Args:
            item: Item to create action file for

        Returns:
            Path to created file, or None if failed
        """
        pass

    def run(self):
        """
        Main watcher loop.
        Continuously checks for updates and creates action files.
        """
        self.logger.info("=" * 60)
        self.logger.info(f"{self.__class__.__name__} Started")
        self.logger.info("=" * 60)
        self.logger.info(f"Vault: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        self.logger.info("=" * 60)

        try:
            while True:
                try:
                    # Check for updates
                    items = self.check_for_updates()

                    # Process each item
                    for item in items:
                        try:
                            self.create_action_file(item)
                        except Exception as e:
                            self.logger.error(f"Error processing item: {e}")

                    # Log status
                    if items:
                        self.logger.info(f"Processed {len(items)} item(s)")

                except Exception as e:
                    self.logger.error(f"Error in check cycle: {e}")

                # Wait before next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("Stopping watcher...")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.logger.info(f"{self.__class__.__name__} Stopped")

    def log_action(self, action_type: str, details: dict):
        """
        Log an action to the daily audit log.

        Args:
            action_type: Type of action (e.g., "file_detected", "email_detected")
            details: Dictionary of action details
        """
        import json

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": self.__class__.__name__.lower(),
            "details": details,
            "status": "success"
        }

        # Append to daily log
        log_date = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs / f"{log_date}.json"

        try:
            # Read existing logs
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            # Append new entry
            logs.append(log_entry)

            # Write back
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            self.logger.error(f"Could not write log: {e}")

    def get_status(self) -> dict:
        """
        Get current status of this watcher.

        Returns:
            Dictionary with status information
        """
        return {
            "name": self.__class__.__name__,
            "vault_path": str(self.vault_path),
            "check_interval": self.check_interval,
            "needs_action_folder": str(self.needs_action),
            "running": True
        }
