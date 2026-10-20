import pytest

from database.db import db


@pytest.fixture(autouse=True)
def reset_database():
    """Every test starts (and ends) with clean seed data."""
    db.reset()
    yield
    db.reset()
