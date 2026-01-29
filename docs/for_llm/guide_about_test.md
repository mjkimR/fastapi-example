# FastAPI Testing Guide for LLMs

This document outlines the testing structure and conventions of the project, providing a step-by-step guide for adding new tests. The goal is to enable an LLM to understand the patterns and conventions, and then autonomously create new, similar tests.

## 1. Overview of the Testing Structure

The `tests/` directory is organized into the following subdirectories:

- **`e2e/`**: Contains end-to-end tests that simulate real-world user interactions with the application. These tests ensure that the entire system works as expected.
  - Example: `test_health.py` verifies the health check endpoint.
- **`unit/`**: Contains unit tests for individual components, such as utility functions and isolated business logic.
- **`integrate/`**: Contains integration tests that verify the interaction between multiple components, such as services and repositories.
- **`fixtures/`**: Provides reusable test data and setup/teardown logic for tests. This includes:
  - `auth.py`: Authentication-related fixtures.
  - `clients.py`: Fixtures for mocking external clients.
  - `db.py`: Database-related fixtures for setting up and tearing down test databases.
  - `data/`: Contains predefined test data for various features (e.g., `memos.py`, `tags.py`).
- **`utils/`**: Contains utility functions for assertions and helpers used across tests.

## 2. Testing Framework

The project uses **pytest** as the testing framework. The configuration for pytest is defined in the `pytest.ini` file located in the `tests/` directory. This file includes settings such as test discovery patterns and custom markers.

### Key pytest Features Used
- **Fixtures**: Reusable setup and teardown logic for tests.
- **Markers**: Custom markers for categorizing tests (e.g., `@pytest.mark.e2e`).
- **Parametrization**: Running the same test with different inputs.

## 3. Types of Tests

### Unit Tests
Unit tests focus on individual components, such as utility functions or isolated methods. They are located in the `tests/unit/` directory.

Example:
- `tests/unit/test_utils/test_some_utility.py`: Tests for utility functions in `utils/helpers.py`.

### Integration Tests
Integration tests verify the interaction between multiple components, such as services and repositories. They are located in the `tests/integrate/` directory.

Example:
- `tests/integrate/test_features/memos/test_memo_service.py`: Tests the interaction between the Memo service and its repository.

### End-to-End (E2E) Tests
E2E tests simulate real-world user interactions with the application. They are located in the `tests/e2e/` directory.

Example:
- `tests/e2e/test_health.py`: Tests the health check endpoint to ensure the application is running.

## 4. Test Utilities and Fixtures

### Fixtures
Fixtures are reusable components that help set up the test environment. They are located in the `tests/fixtures/` directory.

- **`auth.py`**: Provides authentication-related fixtures, such as mock users and tokens.
- **`clients.py`**: Contains fixtures for mocking external API clients.
- **`db.py`**: Manages test database setup and teardown.
- **`data/`**: Contains predefined test data for various features, such as `memos.py` and `tags.py`.

### Utilities
Utility functions for assertions and helpers are located in the `tests/utils/` directory.

- **`assertions.py`**: Provides custom assertion functions for tests.
- **`helpers.py`**: Contains helper functions for common test operations.

## 5. Adding New Tests

Follow these steps to add new tests to the project:

### Step 1: Determine the Test Type
Decide whether the new test is a unit test, integration test, or end-to-end test. Place the test file in the appropriate directory (`unit/`, `integrate/`, or `e2e/`).

### Step 2: Create the Test File
Create a new test file in the appropriate directory. Use the following naming convention:

```
test_<feature>_<functionality>.py
```

For example, to test the `create_memo` functionality in the `memos` feature, create the file:

```
tests/e2e/test_features/memos/test_create_memo.py
```

### Step 3: Write the Test Case
Use pytest to write the test case. Import the necessary fixtures and utilities to set up the test environment.

Example:
```python
import pytest
from app.features.memos.models import Memo
from app.features.memos.schemas import MemoCreate
from tests.fixtures.auth import mock_user
from tests.fixtures.db import test_db_session

def test_create_memo(mock_user, test_db_session):
    # Arrange
    memo_data = MemoCreate(title="Test Memo", content="This is a test.")

    # Act
    new_memo = Memo.create(test_db_session, memo_data, user=mock_user)

    # Assert
    assert new_memo.title == "Test Memo"
    assert new_memo.content == "This is a test."
    assert new_memo.user_id == mock_user.id
```

### Step 4: Run the Tests
Run the tests using the `pytest` command:

```shell
pytest
```

To run a specific test file:

```shell
pytest tests/e2e/test_features/memos/test_create_memo.py
```

To run tests with a specific marker:

```shell
pytest -m e2e
```

### Step 5: Debug and Fix Issues
If a test fails, use the error message and stack trace to identify and fix the issue. Rerun the tests to ensure the issue is resolved.

## 6. Best Practices

- Write clear and concise test cases with descriptive names.
- Use fixtures and utilities to avoid code duplication.
- Test both positive and negative scenarios.
- Keep tests isolated and independent.
- Regularly run all tests to ensure the application remains stable.

---

This guide provides a comprehensive overview of the testing structure and conventions in the FastAPI project. By following these guidelines, you can create new tests that integrate seamlessly with the existing test suite.
