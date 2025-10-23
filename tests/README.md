# Test Suite for Mergington High School Activities API

This directory contains comprehensive tests for the FastAPI application that manages student activity registrations.

## Test Structure

### `test_api.py`
Core functionality tests covering:
- **Activities API endpoints** (`/activities`, `/activities/{name}/signup`, `/activities/{name}/unregister`)
- **Static file serving** (HTML, CSS, JavaScript)
- **Data validation** and structure verification
- **Error handling** for various failure scenarios

### `test_edge_cases.py`
Advanced edge case and integration tests covering:
- **Input validation** (empty emails, missing parameters, special characters)
- **Concurrent operations** and race conditions
- **Data integrity** and state consistency
- **Unicode and internationalization** support

### `conftest.py`
Test configuration and shared fixtures:
- Test client setup
- Data isolation between tests
- Common test utilities

## Running Tests

### Quick Test Run
```bash
python -m pytest tests/
```

### Verbose Output
```bash
python -m pytest tests/ -v
```

### With Coverage Report
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Generate HTML Coverage Report
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Using the Test Runner Script
```bash
python run_tests.py
```

## Test Categories

### ✅ **API Functionality Tests**
- Root redirect to static files
- Retrieving all activities
- Student signup for activities
- Student unregistration from activities
- Duplicate signup prevention
- Activity and student validation

### ✅ **Static File Tests**
- HTML file accessibility
- CSS file serving
- JavaScript file serving

### ✅ **Error Handling Tests**
- Non-existent activity handling
- Unregistered student operations
- Invalid input parameters
- Missing required parameters

### ✅ **Edge Case Tests**
- Empty and malformed emails
- Special characters in activity names
- Concurrent operations
- Case sensitivity
- Unicode character support
- Long input handling

### ✅ **Data Integrity Tests**
- Participant count consistency
- State management across operations
- Data persistence verification

## Coverage Report

Current test coverage: **100%** of application code

```
Name         Stmts   Miss  Cover   Missing
------------------------------------------
src/app.py      33      0   100%
------------------------------------------
TOTAL           33      0   100%
```

## Test Dependencies

The following packages are required for testing:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for FastAPI testing

All dependencies are listed in `requirements.txt` and can be installed with:
```bash
pip install -r requirements.txt
```

## Test Design Philosophy

These tests follow best practices for API testing:
- **Isolation**: Each test is independent and doesn't affect others
- **Comprehensive**: Cover both happy paths and error scenarios
- **Maintainable**: Clear test names and documentation
- **Fast**: Use test client instead of real HTTP calls
- **Reliable**: Consistent results across different environments