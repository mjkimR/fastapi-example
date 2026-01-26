# Testing Strategy

This document outlines the testing strategy, directory structure, and database management approach for this project.

## Directory Structure

The `tests/` directory is organized by test type to ensure a clear and scalable testing structure.

-   **/unit**: Contains unit tests. These tests focus on a single "unit" of code (e.g., a function, a class) in complete isolation from external dependencies.
-   **/integrate**: Contains integration tests. These tests verify the interaction between two or more internal components of the application (e.g., a service and a repository).
-   **/e2e**: Contains end-to-end tests. These tests validate the entire application stack by simulating real user scenarios through API requests.
-   **/fixtures**: Contains shared `pytest` fixtures used across different test suites (e.g., database connections, API clients).
-   **/utils**: Contains helper functions and utilities that can be reused in tests.

## Test Types and Strategies

Each test type employs a different strategy, particularly concerning database management, to balance test speed, reliability, and isolation.

### Unit Tests (`unit/`)

-   **Goal**: To test a single component in isolation.
-   **Dependencies**: All external dependencies, especially database connections or other services, **must be mocked or stubbed**.
-   **Database Strategy**: **No real database connection.** Tests should not interact with a database.

### Integration Tests (`integrate/`)

-   **Goal**: To test the interaction between internal application components (e.g., use cases, services, repositories).
-   **Dependencies**: These tests connect to a real test database (an in-memory SQLite instance by default) but should mock any external, third-party services.
-   **Database Strategy**: **Transaction Rollback**. Each test function is wrapped in a single database transaction. After the test completes, the transaction is rolled back, discarding all changes. This is a very fast method for ensuring test isolation. This is managed by the `session` fixture in `fixtures/db.py`.

### End-to-End (E2E) Tests (`e2e/`)

-   **Goal**: To test the full application stack from an external perspective by making HTTP requests to the API endpoints.
-   **Dependencies**: Runs against the entire live application with a real test database.
-   **Database Strategy**: **Database Cleanup**. Because each API request in the application runs in its own transaction and commits data, a simple rollback is not effective for isolation. Instead, after each E2E test function completes, all rows from all tables in the database are deleted. This ensures that every test starts with a clean, empty database, guaranteeing true isolation. This is managed by the `_clean_db_after_e2e_test` autouse fixture in `e2e/conftest.py`.
