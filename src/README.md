# 🐍 Source Code Directory

This directory contains all Python source code for the Nexus AI Employee project.

---

## 📁 Folder Structure

### 🔍 watchers/
Watcher scripts that monitor external systems for events.

**Files:**
- `base_watcher.py` - Base class for all watchers
- `filesystem_watcher.py` - Monitors file system for new files

**Purpose:** Perception layer - detects events from external sources

**Usage:**
```python
from src.watchers.base_watcher import BaseWatcher
from src.watchers.filesystem_watcher import FilesystemWatcher

# Create watcher instance
watcher = FilesystemWatcher(drop_folder="~/AI_Employee_Drop")
watcher.start()
```

---

### 🔗 integration/
Integration modules for connecting with external systems.

**Files:**
- `claude_integration.py` - VaultManager class for Obsidian vault operations

**Purpose:** Reasoning layer - manages vault operations and Claude integration

**Usage:**
```python
from src.integration.claude_integration import VaultManager

# Create vault manager
vault = VaultManager()

# Read pending tasks
tasks = vault.read_needs_action()

# Create plan
vault.create_plan("task_name", "objective", ["step1", "step2"])
```

---

### 🛠️ utils/
Utility modules for common functionality.

**Files:**
- (To be added: retry_handler.py, rate_limiter.py, etc.)

**Purpose:** Shared utilities used across the project

**Usage:**
```python
from src.utils.retry_handler import retry_with_backoff
from src.utils.rate_limiter import RateLimiter
```

---

## 🎯 Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│     Perception Layer (Watchers)     │
│  - Monitors external systems        │
│  - Creates action files             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Reasoning Layer (Integration)     │
│  - Reads action files               │
│  - Creates plans                    │
│  - Manages approvals                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Action Layer (Skills)          │
│  - Executes approved actions        │
│  - Logs results                     │
└─────────────────────────────────────┘
```

---

## 📝 Code Standards

### Python Style
- Follow PEP 8 style guide
- Use type hints for function parameters
- Add docstrings to all classes and functions
- Keep functions small and focused

### Example:
```python
from typing import List, Optional
from pathlib import Path

class MyWatcher(BaseWatcher):
    """Watches for specific events.

    Args:
        watch_path: Path to monitor
        interval: Check interval in seconds
    """

    def __init__(self, watch_path: Path, interval: int = 60):
        super().__init__(interval)
        self.watch_path = watch_path

    def check_for_updates(self) -> List[dict]:
        """Check for new events.

        Returns:
            List of event dictionaries
        """
        # Implementation
        pass
```

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_integration.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Writing Tests
```python
import pytest
from src.integration.claude_integration import VaultManager

def test_vault_manager():
    vault = VaultManager()
    tasks = vault.read_needs_action()
    assert isinstance(tasks, list)
```

---

## 🔧 Development Setup

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials
```

### Running Locally
```bash
# Start filesystem watcher
python src/watchers/filesystem_watcher.py

# Test vault integration
python src/integration/claude_integration.py
```

---

## 📊 Module Dependencies

```
src/
├── watchers/
│   ├── base_watcher.py (no dependencies)
│   └── filesystem_watcher.py (depends on: base_watcher)
│
├── integration/
│   └── claude_integration.py (depends on: pathlib, json)
│
└── utils/
    └── (utility modules - minimal dependencies)
```

---

## 🚀 Adding New Modules

### Adding a New Watcher
1. Create file in `src/watchers/`
2. Inherit from `BaseWatcher`
3. Implement `check_for_updates()` and `create_action_file()`
4. Add tests in `tests/`
5. Document in this README

### Adding a New Integration
1. Create file in `src/integration/`
2. Follow existing patterns
3. Add type hints and docstrings
4. Add tests in `tests/`
5. Document in this README

---

## 📚 Related Documentation

- **Setup Guide:** `docs/guides/SETUP_INSTRUCTIONS.md`
- **Architecture:** `docs/reference/ARCHITECTURE.md` (to be created)
- **API Reference:** `docs/reference/API.md` (to be created)

---

**Last Updated:** 2026-03-26
**Status:** Clean and organized
**Total Files:** 3 (more to be added)
