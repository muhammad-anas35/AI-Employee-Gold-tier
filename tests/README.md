# 🧪 Tests Directory

This directory contains all test files for the Nexus AI Employee project.

---

## 📁 Test Files

### test_odoo_api.py
**Purpose:** Test Odoo XML-RPC API connection and basic operations

**What it tests:**
- Authentication with Odoo
- Company information retrieval
- Partner count query
- Basic API functionality

**Usage:**
```bash
# Run the test
python tests/test_odoo_api.py

# Expected output:
# ✅ Authentication successful! UID: 2
# ✅ Company: My Company
# ✅ Partners in database: 3
# 🎉 Odoo API is working perfectly!
```

**Prerequisites:**
- Odoo running on localhost:8069
- Database created and configured
- Credentials in .env file

---

## 🧪 Running Tests

### Individual Tests
```bash
# Test Odoo API
python tests/test_odoo_api.py

# Test integration (when created)
python tests/test_integration.py
```

### All Tests (with pytest)
```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

---

## 📝 Writing Tests

### Test Structure
```python
import pytest
from src.integration.claude_integration import VaultManager

class TestVaultManager:
    """Test VaultManager functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.vault = VaultManager()

    def test_read_needs_action(self):
        """Test reading needs action folder"""
        tasks = self.vault.read_needs_action()
        assert isinstance(tasks, list)

    def test_create_plan(self):
        """Test plan creation"""
        result = self.vault.create_plan(
            "test_task",
            "Test objective",
            ["step1", "step2"]
        )
        assert result is not None
```

### Test Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

---

## 🎯 Test Coverage Goals

### Current Coverage
- Odoo API: ✅ Basic tests
- Integration: ⏳ To be added
- Watchers: ⏳ To be added
- Skills: ⏳ To be added

### Target Coverage
- **Unit Tests:** 80%+ coverage
- **Integration Tests:** All critical paths
- **End-to-End Tests:** Main workflows

---

## 🔧 Test Configuration

### pytest.ini (to be created)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=src --cov-report=html
```

### conftest.py (to be created)
```python
import pytest
from pathlib import Path

@pytest.fixture
def vault_path():
    """Provide test vault path"""
    return Path(__file__).parent.parent / "AI_Employee_Vault"

@pytest.fixture
def test_data_path():
    """Provide test data path"""
    return Path(__file__).parent / "test_data"
```

---

## 🚨 Test Best Practices

### Do's
- ✅ Test one thing per test
- ✅ Use descriptive test names
- ✅ Clean up after tests
- ✅ Use fixtures for common setup
- ✅ Mock external dependencies
- ✅ Test edge cases and errors

### Don'ts
- ❌ Don't test external services directly
- ❌ Don't depend on test execution order
- ❌ Don't use production data
- ❌ Don't skip cleanup
- ❌ Don't write flaky tests

---

## 📊 Test Types

### Unit Tests
Test individual functions and classes in isolation.

**Example:**
```python
def test_create_action_file():
    """Test action file creation"""
    watcher = FilesystemWatcher("/tmp/test")
    result = watcher.create_action_file({"type": "test"})
    assert result.exists()
```

### Integration Tests
Test multiple components working together.

**Example:**
```python
def test_vault_workflow():
    """Test complete vault workflow"""
    vault = VaultManager()
    # Create task
    vault.create_task("test")
    # Read task
    tasks = vault.read_needs_action()
    assert len(tasks) > 0
```

### End-to-End Tests
Test complete user workflows.

**Example:**
```python
def test_invoice_workflow():
    """Test complete invoice workflow"""
    # 1. Create invoice request
    # 2. Approve invoice
    # 3. Process invoice
    # 4. Verify in Odoo
    pass
```

---

## 🔍 Debugging Tests

### Running Single Test
```bash
# Run specific test file
pytest tests/test_odoo_api.py

# Run specific test function
pytest tests/test_odoo_api.py::test_authentication

# Run with print statements
pytest -s tests/test_odoo_api.py
```

### Using Debugger
```python
import pdb

def test_something():
    result = some_function()
    pdb.set_trace()  # Debugger will stop here
    assert result == expected
```

---

## 📚 Test Data

### Test Data Location
```
tests/
├── test_data/
│   ├── sample_email.json
│   ├── sample_invoice.json
│   └── sample_task.md
```

### Using Test Data
```python
import json
from pathlib import Path

def load_test_data(filename):
    """Load test data file"""
    path = Path(__file__).parent / "test_data" / filename
    with open(path) as f:
        return json.load(f)

def test_with_data():
    data = load_test_data("sample_email.json")
    # Use data in test
```

---

## 🎯 Future Tests to Add

### High Priority
- [ ] Test VaultManager operations
- [ ] Test BaseWatcher functionality
- [ ] Test FilesystemWatcher
- [ ] Test Odoo integration end-to-end

### Medium Priority
- [ ] Test email sending
- [ ] Test social media posting
- [ ] Test approval workflow
- [ ] Test error handling

### Low Priority
- [ ] Test performance
- [ ] Test concurrent operations
- [ ] Test edge cases
- [ ] Test error recovery

---

## 📞 Related Documentation

- **Setup Guide:** `docs/guides/SETUP_INSTRUCTIONS.md`
- **Source Code:** `src/README.md`
- **Contributing:** `CONTRIBUTING.md` (to be created)

---

**Last Updated:** 2026-03-26
**Status:** Basic tests in place, more to be added
**Coverage:** ~20% (target: 80%)
