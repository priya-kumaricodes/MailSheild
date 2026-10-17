"""Authenticated symmetric token encryption using AES-256-GCM.

Provides secure key derivation, random 96-bit nonce generation,
user-bound Additional Authenticated Data (AAD), payload versioning for key rotation,
and strict fail-closed tamper detection without leaking secrets.
"""

import base64
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from backend.app.core.config import settings

CURRENT_KEY_VERSION = 1
NONCE_LENGTH_BYTES = 12
HKDF_SALT = b"mailshield-salt-v1"
HKDF_INFO = b"mailshield-gmail-token-encryption-v1"


class TokenEncryptionError(Exception):
    """Base exception for token encryption errors."""
    pass


class TokenDecryptionError(TokenEncryptionError):
    """Raised when token decryption or verification fails."""
    pass


class ConfigurationError(Exception):
    """Raised when encryption key configuration is invalid or insecure."""
    pass


def derive_key(secret: str, salt: bytes = HKDF_SALT, info: bytes = HKDF_INFO) -> bytes:
    """Derive a 256-bit (32-byte) key from secret material using HKDF-SHA256."""
    if not secret or len(secret.strip()) < 16:
        raise ConfigurationError("Encryption secret must contain at least 16 characters with high entropy.")
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info,
    )
    return hkdf.derive(secret.strip().encode("utf-8"))


class TokenEncryptionService:
    """Service for encrypting and decrypting OAuth tokens at rest."""

    def __init__(
        self,
        primary_secret: str | None = None,
        fallback_secret: str | None = None,
    ):
        raw_primary = primary_secret or getattr(settings, "TOKEN_ENCRYPTION_KEY", "") or settings.SECRET_KEY
        if not raw_primary:
            raise ConfigurationError("No encryption key configured for TokenEncryptionService.")
        self._primary_key = derive_key(raw_primary)
        self._primary_aesgcm = AESGCM(self._primary_key)

        raw_fallback = fallback_secret or getattr(settings, "TOKEN_ENCRYPTION_KEY_FALLBACK", "")
        self._fallback_aesgcm: AESGCM | None = None
        if raw_fallback and len(raw_fallback.strip()) >= 16:
            fallback_key = derive_key(raw_fallback)
            self._fallback_aesgcm = AESGCM(fallback_key)

    def encrypt(self, plaintext: str, user_id: str) -> str:
        """Encrypt token plaintext with AES-256-GCM bound to user_id as AAD.

        Payload structure:
        [1-byte version][12-byte nonce][ciphertext + 16-byte tag]
        """
        if not plaintext:
            raise ValueError("Cannot encrypt empty token plaintext.")
        if not user_id:
            raise ValueError("user_id is required for AAD binding.")

        nonce = os.urandom(NONCE_LENGTH_BYTES)
        aad = user_id.encode("utf-8")
        data = plaintext.encode("utf-8")

        ciphertext_with_tag = self._primary_aesgcm.encrypt(nonce, data, aad)

        version_byte = bytes([CURRENT_KEY_VERSION])
        payload = version_byte + nonce + ciphertext_with_tag
        return base64.urlsafe_b64encode(payload).decode("ascii")

    def decrypt(self, encrypted_b64: str, user_id: str) -> str:
        """Decrypt token ciphertext verifying AAD user_id and GCM authentication tag.

        Raises TokenDecryptionError on tamper, mismatch, or corruption.
        """
        if not encrypted_b64:
            raise ValueError("Cannot decrypt empty encrypted token string.")
        if not user_id:
            raise ValueError("user_id is required for AAD verification.")

        try:
            raw = base64.urlsafe_b64decode(encrypted_b64.encode("ascii"))
        except Exception as e:
            raise TokenDecryptionError("Invalid base64 payload encoding.") from e

        if len(raw) < 1 + NONCE_LENGTH_BYTES + 16:
            raise TokenDecryptionError("Ciphertext payload too short.")

        version = raw[0]
        nonce = raw[1 : 1 + NONCE_LENGTH_BYTES]
        ciphertext_with_tag = raw[1 + NONCE_LENGTH_BYTES :]
        aad = user_id.encode("utf-8")

        # Select cipher based on version
        cipher = self._primary_aesgcm
        if version != CURRENT_KEY_VERSION:
            if self._fallback_aesgcm is not None:
                cipher = self._fallback_aesgcm
            else:
                raise TokenDecryptionError(f"Unsupported token encryption version {version} and no fallback key.")

        try:
            decrypted_bytes = cipher.decrypt(nonce, ciphertext_with_tag, aad)
            return decrypted_bytes.decode("utf-8")
        except InvalidTag as e:
            raise TokenDecryptionError("Decryption failed: authentication tag mismatch or corrupted ciphertext.") from e
        except Exception as e:
            raise TokenDecryptionError("Decryption failed due to invalid token payload.") from e

    def rotate_token(self, encrypted_b64: str, user_id: str) -> str:
        """Decrypt with existing key (primary or fallback) and re-encrypt under current primary key."""
        plaintext = self.decrypt(encrypted_b64, user_id)
        return self.encrypt(plaintext, user_id)


# Module-level singleton
_service_instance: TokenEncryptionService | None = None


def get_token_encryption_service() -> TokenEncryptionService:
    global _service_instance
    if _service_instance is None:
        _service_instance = TokenEncryptionService()
    return _service_instance


def reset_token_encryption_service() -> None:
    global _service_instance
    _service_instance = None
