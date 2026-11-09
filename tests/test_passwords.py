import pytest
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User
from app.services.passwords import hash_password, needs_rehash, verify_password
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def _add_user(app, email, password=None, raw_hash=None):
    with app.app_context():
        user = User(email=email, role='teacher')
        if raw_hash:
            user.password_hash = raw_hash
        else:
            user.set_password(password)
        db.session.add(user)
        db.session.commit()


def _hash_of(app, email):
    with app.app_context():
        return User.query.filter_by(email=email).first().password_hash


def test_hash_is_argon2id_and_not_plaintext():
    h = hash_password('geheim-wachtwoord')
    assert h.startswith('$argon2id$')
    assert 'geheim-wachtwoord' not in h


def test_same_password_gives_different_hash_because_of_salt():
    assert hash_password('zelfde-wachtwoord') != hash_password('zelfde-wachtwoord')


def test_verify_correct_and_wrong_password():
    h = hash_password('juist-wachtwoord')
    assert verify_password(h, 'juist-wachtwoord')
    assert not verify_password(h, 'fout-wachtwoord')
    assert not verify_password('', 'x')
    assert not verify_password('geen-hash', 'x')


def test_legacy_hash_still_verifies_and_needs_rehash():
    legacy = generate_password_hash('oud-wachtwoord')
    assert verify_password(legacy, 'oud-wachtwoord')
    assert needs_rehash(legacy)
    assert not needs_rehash(hash_password('nieuw-wachtwoord'))


def test_login_success_and_failure(app, client):
    _add_user(app, 'a@school.nl', 'wachtwoord123')
    bad = client.post('/auth/login', data={'email': 'a@school.nl', 'password': 'fout'})
    assert 'Verkeerd e-mailadres of wachtwoord' in bad.get_data(as_text=True)
    ok = client.post('/auth/login', data={'email': 'a@school.nl', 'password': 'wachtwoord123'})
    assert ok.status_code == 302


def test_unknown_email_gives_same_message(app, client):
    r = client.post('/auth/login', data={'email': 'bestaat@niet.nl', 'password': 'x'})
    assert 'Verkeerd e-mailadres of wachtwoord' in r.get_data(as_text=True)


def test_legacy_hash_is_upgraded_on_login(app, client):
    legacy = generate_password_hash('oud-wachtwoord')
    _add_user(app, 'oud@school.nl', raw_hash=legacy)
    r = client.post('/auth/login', data={'email': 'oud@school.nl', 'password': 'oud-wachtwoord'})
    assert r.status_code == 302
    new_hash = _hash_of(app, 'oud@school.nl')
    assert new_hash.startswith('$argon2id$')
    with app.app_context():
        assert User.query.filter_by(email='oud@school.nl').first().password_updated_at is not None


def test_failed_login_does_not_change_legacy_hash(app, client):
    legacy = generate_password_hash('oud-wachtwoord')
    _add_user(app, 'oud@school.nl', raw_hash=legacy)
    client.post('/auth/login', data={'email': 'oud@school.nl', 'password': 'fout'})
    assert _hash_of(app, 'oud@school.nl') == legacy


def test_new_user_gets_argon2id_hash_with_unique_salt(app):
    _add_user(app, 'x@school.nl', 'zelfde-wachtwoord')
    _add_user(app, 'y@school.nl', 'zelfde-wachtwoord')
    hx, hy = _hash_of(app, 'x@school.nl'), _hash_of(app, 'y@school.nl')
    assert hx.startswith('$argon2id$') and hx != hy
    assert hx.split('$')[4] != hy.split('$')[4]  # different salt


def test_password_updated_at_column_added_to_old_database(app):
    # Simulate an old database without the new column and run the migration.
    from app import _ensure_schema_compatibility
    with app.app_context():
        db.session.execute(text('ALTER TABLE user DROP COLUMN password_updated_at'))
        db.session.commit()
        _ensure_schema_compatibility()
        cols = {r[1] for r in db.session.execute(text('PRAGMA table_info(user)'))}
        assert 'password_updated_at' in cols


def test_teacher_cannot_set_short_password(app, client):
    from app.models import Student
    with app.app_context():
        s = Student(id=1, name='Sam')
        db.session.add(s)
        db.session.commit()
    _add_user(app, 'docent@school.nl', 'docent-wachtwoord')
    client.post('/auth/login', data={'email': 'docent@school.nl', 'password': 'docent-wachtwoord'})
    r = client.post('/teacher/student/1/create-account',
                    data={'email': 'sam@leerling.nl', 'password': 'kort'}, follow_redirects=True)
    assert 'minimaal 8 tekens' in r.get_data(as_text=True)
    with app.app_context():
        assert User.query.filter_by(email='sam@leerling.nl').first() is None
