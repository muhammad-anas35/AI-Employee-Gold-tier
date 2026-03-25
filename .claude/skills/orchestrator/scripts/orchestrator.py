#!/usr/bin/env python3
"""
Orchestrator for AI Employee
Master process that coordinates all watchers and manages workflow
"""

import os
import sys
import time
import json
import logging
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import psutil

# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent.parent.parent / "AI_Employee_Vault"
LOGS = VAULT_PATH / "Logs"
CONFIG_FILE = Path(__file__).parent.parent.parent.parent.parent / "orchestrator_config.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS / "orchestrator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")


class Orchestrator:
    """Master orchestrator for AI Employee system"""

    def __init__(self, vault_path: Path = VAULT_PATH):
        self.vault_path = vault_path
        self.config = self._load_config()
        self.processes = {}
        self.start_time = datetime.now()
        self.running = False
        self.restart_counts = {}

        # Ensure folders exist
        LOGS.mkdir(parents=True, exist_ok=True)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_config(self) -> Dict:
        """Load orchestrator configuration"""
        default_config = {
            "watchers": {
                "gmail": {
                    "enabled": True,
                    "script": "gmail_watcher.py",
                    "check_interval": 120,
                    "auto_restart": True
                },
                "whatsapp": {
                    "enabled": False,  # Disabled by default (requires setup)
                    "script": "whatsapp_watcher.py",
                    "check_interval": 30,
                    "auto_restart": True
                },
                "filesystem": {
                    "enabled": True,
                    "script": "filesystem_watcher.py",
                    "check_interval": 5,
                    "auto_restart": True
                }
            },
            "scheduler": {
                "process_tasks_interval": 300,  # 5 minutes
                "update_dashboard_interval": 1800,  # 30 minutes
                "check_approvals_interval": 60,  # 1 minute
            },
            "health_monitor": {
                "check_interval": 60,
                "restart_delay": 5,
                "max_restarts": 3
            }
        }

        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Could not load config: {e}, using defaults")

        return default_config

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)

    def start_watcher(self, name: str) -> bool:
        """Start a watcher process"""
        try:
            watcher_config = self.config['watchers'].get(name)
            if not watcher_config or not watcher_config.get('enabled'):
                logger.info(f"Watcher {name} is disabled")
                return False

            script = watcher_config['script']
            script_path = Path(__file__).parent / script

            if not script_path.exists():
                logger.error(f"Watcher script not found: {script_path}")
                return False

            # Start process
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(Path(__file__).parent)
            )

            self.processes[name] = {
                'process': process,
                'pid': process.pid,
                'started': datetime.now(),
                'script': script
            }

            logger.info(f"Started {name} watcher (PID: {process.pid})")
            return True

        except Exception as e:
            logger.error(f"Error starting {name} watcher: {e}")
            return False

    def stop_watcher(self, name: str) -> bool:
        """Stop a watcher process"""
        try:
            if name not in self.processes:
                logger.warning(f"Watcher {name} not running")
                return False

            process_info = self.processes[name]
            process = process_info['process']

            # Try graceful shutdown first
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if not responding
                process.kill()
                process.wait()

            logger.info(f"Stopped {name} watcher (PID: {process_info['pid']})")
            del self.processes[name]
            return True

        except Exception as e:
            logger.error(f"Error stopping {name} watcher: {e}")
            return False

    def is_watcher_running(self, name: str) -> bool:
        """Check if watcher is running"""
        if name not in self.processes:
            return False

        process = self.processes[name]['process']
        return process.poll() is None

    def restart_watcher(self, name: str) -> bool:
        """Restart a watcher"""
        logger.info(f"Restarting {name} watcher...")

        # Track restart count
        self.restart_counts[name] = self.restart_counts.get(name, 0) + 1

        # Check max restarts
        max_restarts = self.config['health_monitor']['max_restarts']
        if self.restart_counts[name] > max_restarts:
            logger.error(f"{name} watcher failed {max_restarts} times, disabling")
            self.config['watchers'][name]['enabled'] = False
            return False

        # Stop if running
        if name in self.processes:
            self.stop_watcher(name)

        # Wait before restart
        restart_delay = self.config['health_monitor']['restart_delay']
        time.sleep(restart_delay)

        # Start again
        return self.start_watcher(name)

    def check_health(self):
        """Check health of all watchers"""
        for name, watcher_config in self.config['watchers'].items():
            if not watcher_config.get('enabled'):
                continue

            if not self.is_watcher_running(name):
                logger.warning(f"{name} watcher is not running")

                if watcher_config.get('auto_restart'):
                    self.restart_watcher(name)
                else:
                    logger.info(f"Auto-restart disabled for {name}")

    def check_approvals(self):
        """Check for approved items and process them"""
        try:
            approved_folder = self.vault_path / "Approved"
            if not approved_folder.exists():
                return

            approved_files = list(approved_folder.glob("*.md"))

            if not approved_files:
                return

            logger.info(f"Found {len(approved_files)} approved item(s)")

            for file in approved_files:
                try:
                    # Read file to determine type
                    content = file.read_text(encoding='utf-8')

                    if 'type: email_send' in content:
                        logger.info(f"Processing approved email: {file.name}")
                        self._process_approved_email(file)
                    elif 'type: linkedin_post' in content:
                        logger.info(f"Processing approved LinkedIn post: {file.name}")
                        self._process_approved_post(file)
                    else:
                        logger.warning(f"Unknown approval type: {file.name}")

                except Exception as e:
                    logger.error(f"Error processing {file.name}: {e}")

        except Exception as e:
            logger.error(f"Error checking approvals: {e}")

    def _process_approved_email(self, file: Path):
        """Process approved email"""
        try:
            # Call email sender
            result = subprocess.run(
                [sys.executable, "send_email.py", "--send-approved"],
                cwd=str(Path(__file__).parent),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"Email processed successfully: {file.name}")
            else:
                logger.error(f"Email processing failed: {result.stderr}")

        except Exception as e:
            logger.error(f"Error processing email: {e}")

    def _process_approved_post(self, file: Path):
        """Process approved LinkedIn post"""
        try:
            # Call LinkedIn poster
            result = subprocess.run(
                [sys.executable, "linkedin_poster.py", "--publish"],
                cwd=str(Path(__file__).parent),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info(f"Post published successfully: {file.name}")
            else:
                logger.error(f"Post publishing failed: {result.stderr}")

        except Exception as e:
            logger.error(f"Error publishing post: {e}")

    def process_vault_tasks(self):
        """Trigger Claude to process vault tasks"""
        try:
            logger.info("Processing vault tasks...")

            # Check if there are tasks to process
            needs_action = self.vault_path / "Needs_Action"
            if not needs_action.exists():
                return

            task_files = list(needs_action.glob("*.md"))
            if not task_files:
                logger.info("No tasks to process")
                return

            logger.info(f"Found {len(task_files)} task(s) to process")

            # Trigger Claude Code to process tasks
            try:
                result = subprocess.run(
                    ["claude", "/process-vault-tasks", "--vault-path", str(self.vault_path)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                if result.returncode == 0:
                    logger.info("✓ Claude Code processed vault tasks successfully")
                else:
                    logger.warning(f"Claude Code returned non-zero exit code: {result.returncode}")
                    if result.stderr:
                        logger.warning(f"Error output: {result.stderr}")

            except subprocess.TimeoutExpired:
                logger.error("Claude Code processing timed out after 5 minutes")
            except FileNotFoundError:
                logger.error("Claude Code CLI not found. Is it installed and in PATH?")
            except Exception as e:
                logger.error(f"Error calling Claude Code: {e}")

        except Exception as e:
            logger.error(f"Error processing vault tasks: {e}")

    def update_dashboard(self):
        """Update dashboard metrics"""
        try:
            logger.info("Updating dashboard...")

            # Count items in each folder
            metrics = {
                "pending_tasks": len(list((self.vault_path / "Needs_Action").glob("*.md"))),
                "pending_approval": len(list((self.vault_path / "Pending_Approval").glob("*.md"))),
                "completed_today": self._count_completed_today(),
                "activity": f"Orchestrator health check at {datetime.now().strftime('%H:%M')}"
            }

            # Call update-dashboard skill
            try:
                result = subprocess.run(
                    ["claude", "/update-dashboard", "--vault-path", str(self.vault_path)],
                    capture_output=True,
                    text=True,
                    timeout=60  # 1 minute timeout
                )

                if result.returncode == 0:
                    logger.info("✓ Dashboard updated successfully")
                else:
                    logger.warning(f"Dashboard update returned non-zero exit code: {result.returncode}")

            except subprocess.TimeoutExpired:
                logger.error("Dashboard update timed out")
            except FileNotFoundError:
                logger.warning("Claude Code CLI not found, logging metrics instead")
                logger.info(f"Dashboard metrics: {metrics}")
            except Exception as e:
                logger.error(f"Error calling update-dashboard: {e}")
                logger.info(f"Dashboard metrics: {metrics}")

        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")

    def _count_completed_today(self) -> int:
        """Count tasks completed today"""
        try:
            done_folder = self.vault_path / "Done"
            if not done_folder.exists():
                return 0

            today = datetime.now().date()
            count = 0

            for file in done_folder.glob("*.md"):
                file_date = datetime.fromtimestamp(file.stat().st_mtime).date()
                if file_date == today:
                    count += 1

            return count

        except Exception as e:
            logger.error(f"Error counting completed tasks: {e}")
            return 0

    def get_status(self) -> Dict:
        """Get orchestrator status"""
        uptime = datetime.now() - self.start_time

        status = {
            "running": self.running,
            "uptime_seconds": int(uptime.total_seconds()),
            "watchers": {},
            "metrics": {
                "pending_tasks": len(list((self.vault_path / "Needs_Action").glob("*.md"))),
                "pending_approval": len(list((self.vault_path / "Pending_Approval").glob("*.md"))),
                "completed_today": self._count_completed_today()
            }
        }

        for name in self.config['watchers'].keys():
            status['watchers'][name] = {
                "enabled": self.config['watchers'][name].get('enabled', False),
                "running": self.is_watcher_running(name),
                "pid": self.processes.get(name, {}).get('pid'),
                "restart_count": self.restart_counts.get(name, 0)
            }

        return status

    def run(self):
        """Main orchestration loop"""
        logger.info("=" * 60)
        logger.info("AI Employee Orchestrator Started")
        logger.info("=" * 60)
        logger.info(f"Vault: {self.vault_path}")
        logger.info("=" * 60)

        self.running = True

        # Start all enabled watchers
        for name, config in self.config['watchers'].items():
            if config.get('enabled'):
                self.start_watcher(name)

        # Main loop
        last_health_check = time.time()
        last_approval_check = time.time()
        last_task_process = time.time()
        last_dashboard_update = time.time()

        try:
            while self.running:
                current_time = time.time()

                # Health check
                if current_time - last_health_check >= self.config['health_monitor']['check_interval']:
                    self.check_health()
                    last_health_check = current_time

                # Approval check
                if current_time - last_approval_check >= self.config['scheduler']['check_approvals_interval']:
                    self.check_approvals()
                    last_approval_check = current_time

                # Process tasks
                if current_time - last_task_process >= self.config['scheduler']['process_tasks_interval']:
                    self.process_vault_tasks()
                    last_task_process = current_time

                # Update dashboard
                if current_time - last_dashboard_update >= self.config['scheduler']['update_dashboard_interval']:
                    self.update_dashboard()
                    last_dashboard_update = current_time

                # Sleep to avoid busy loop
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown orchestrator and all watchers"""
        logger.info("Shutting down orchestrator...")
        self.running = False

        # Stop all watchers
        for name in list(self.processes.keys()):
            self.stop_watcher(name)

        logger.info("Orchestrator stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--status', action='store_true',
                        help='Show orchestrator status')
    parser.add_argument('--daemon', action='store_true',
                        help='Run in daemon mode (background)')

    args = parser.parse_args()

    orchestrator = Orchestrator()

    if args.status:
        status = orchestrator.get_status()
        print("\nOrchestrator Status")
        print("=" * 60)
        print(f"Running: {status['running']}")
        print(f"Uptime: {status['uptime_seconds']} seconds")
        print("\nWatchers:")
        for name, info in status['watchers'].items():
            status_str = "Running" if info['running'] else "Stopped"
            print(f"  - {name}: {status_str} (PID: {info.get('pid', 'N/A')})")
        print("\nMetrics:")
        print(f"  - Pending tasks: {status['metrics']['pending_tasks']}")
        print(f"  - Pending approval: {status['metrics']['pending_approval']}")
        print(f"  - Completed today: {status['metrics']['completed_today']}")
        print()
    else:
        orchestrator.run()


if __name__ == "__main__":
    main()
