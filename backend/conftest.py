"""Shared fixtures. The test database is rebuilt only when a test asks for it."""

import pytest

from tests.db_setup import rebuild_test_database, require_test_database_url


@pytest.fixture(scope="session")
def migrated_database() -> None:
    rebuild_test_database(require_test_database_url())
