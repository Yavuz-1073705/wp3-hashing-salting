"""Password hashing with Argon2id.

Passwords are never stored in plain text. Every password is hashed with
Argon2id (RFC 9106) using a fresh random 16-byte salt. The salt and the
cost parameters are stored inside the hash string itself, for example:

    $argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>

Accounts created before this change still have a Werkzeug scrypt hash
("scrypt:32768:8:1$<salt>$<hash>"). Those can still log in, and their hash is
upgraded to Argon2id on the first successful login (the plain-text password is
only available at that moment).
"""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from werkzeug.security import check_password_hash

MIN_PASSWORD_LENGTH = 8

ARGON2_PREFIX = '$argon2id$'
LEGACY_PREFIXES = ('scrypt:', 'pbkdf2:')

# RFC 9106 "second recommended option": 64 MiB memory, 3 passes, 4 lanes.
# This is above the OWASP minimum (19 MiB, 2 passes, 1 lane).
_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=64 * 1024,  # KiB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)

# Used when a login is attempted for an e-mail address that does not exist.
# Verifying against a dummy hash makes the response take as long as for a
# real account, so attackers cannot find valid e-mail addresses by timing.
_DUMMY_HASH = _hasher.hash('dummy-password-for-timing')


def hash_password(password: str) -> str:
    """Hash a password with Argon2id and a new random salt."""
    return _hasher.hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
    """Check a password against a stored Argon2id or legacy Werkzeug hash."""
    if not stored_hash:
        return False
    if stored_hash.startswith(ARGON2_PREFIX):
        try:
            return _hasher.verify(stored_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False
    if stored_hash.startswith(LEGACY_PREFIXES):
        return check_password_hash(stored_hash, password)
    return False


def needs_rehash(stored_hash: str) -> bool:
    """True if the hash is not Argon2id or uses outdated parameters."""
    if not stored_hash.startswith(ARGON2_PREFIX):
        return True
    return _hasher.check_needs_rehash(stored_hash)


def dummy_verify(password: str) -> None:
    """Spend the same time as a real check, for unknown e-mail addresses."""
    verify_password(_DUMMY_HASH, password)


def hash_algorithm(stored_hash: str) -> str:
    """Short algorithm name of a stored hash, for reporting."""
    if stored_hash.startswith(ARGON2_PREFIX):
        return 'argon2id'
    for prefix in LEGACY_PREFIXES:
        if stored_hash.startswith(prefix):
            return prefix.rstrip(':') + ' (oud)'
    return 'onbekend'
