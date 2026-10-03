import pytest

from app.services.production_security import assert_admin_passwords_safe
from tests.conftest import create_test_account


def test_shipped_admin_password_is_rejected(db_session):
    create_test_account(db_session, role='admin', password='AdminPassword123!')
    with pytest.raises(RuntimeError, match='development password'):
        assert_admin_passwords_safe(db_session)


def test_unique_admin_password_is_allowed(db_session):
    create_test_account(db_session, role='admin')
    assert_admin_passwords_safe(db_session)
