"""Unit tests for AES-256-GCM token encryption and key derivation.
"""

import base64

import pytest

from backend.app.core.crypto import (
    CURRENT_KEY_VERSION,
    ConfigurationError,
    TokenDecryptionError,
    TokenEncryptionService,
    derive_key,
)


def test_derive_key_length_and_entropy():
    key = derive_key("a-very-strong-production-secret-key-32b")
    assert len(key) == 32
    assert isinstance(key, bytes)

    # Empty or short secrets rejected
    with pytest.raises(ConfigurationError):
        derive_key("")
    with pytest.raises(ConfigurationError):
        derive_key("short")


def test_encryption_decryption_round_trip():
    service = TokenEncryptionService(primary_secret="primary-secret-key-for-testing-12345")
    user_id = "user-uuid-1234-abcd"
    plaintext = "ya29.a0AfH6SMB_sample_google_oauth_access_token_xyz"

    encrypted = service.encrypt(plaintext, user_id=user_id)
    assert encrypted != plaintext
    assert isinstance(encrypted, str)

    decrypted = service.decrypt(encrypted, user_id=user_id)
    assert decrypted == plaintext


def test_nonce_uniqueness_across_encryptions():
    service = TokenEncryptionService(primary_secret="primary-secret-key-for-testing-12345")
    user_id = "user-uuid-1234-abcd"
    plaintext = "same-token-value"

    enc1 = service.encrypt(plaintext, user_id=user_id)
    enc2 = service.encrypt(plaintext, user_id=user_id)
    assert enc1 != enc2  # Random 12-byte nonce ensures different ciphertexts


def test_tamper_detection_ciphertext():
    service = TokenEncryptionService(primary_secret="primary-secret-key-for-testing-12345")
    user_id = "user-uuid-1234-abcd"
    plaintext = "secret-token-content"

    encrypted = service.encrypt(plaintext, user_id=user_id)
    raw = bytearray(base64.urlsafe_b64decode(encrypted.encode("ascii")))

    # Tamper with the ciphertext byte (offset after version + nonce = 1 + 12 = 13)
    raw[15] ^= 0xFF
    tampered_b64 = base64.urlsafe_b64encode(bytes(raw)).decode("ascii")

    with pytest.raises(TokenDecryptionError, match="authentication tag mismatch or corrupted ciphertext"):
        service.decrypt(tampered_b64, user_id=user_id)


def test_tamper_detection_auth_tag():
    service = TokenEncryptionService(primary_secret="primary-secret-key-for-testing-12345")
    user_id = "user-uuid-1234-abcd"
    plaintext = "secret-token-content"

    encrypted = service.encrypt(plaintext, user_id=user_id)
    raw = bytearray(base64.urlsafe_b64decode(encrypted.encode("ascii")))

    # Tamper with the last byte (part of the 16-byte GCM authentication tag)
    raw[-1] ^= 0x01
    tampered_b64 = base64.urlsafe_b64encode(bytes(raw)).decode("ascii")

    with pytest.raises(TokenDecryptionError, match="authentication tag mismatch or corrupted ciphertext"):
        service.decrypt(tampered_b64, user_id=user_id)


def test_cross_user_aad_binding():
    service = TokenEncryptionService(primary_secret="primary-secret-key-for-testing-12345")
    user_a = "user-alice-1111"
    user_b = "user-bob-2222"
    plaintext = "alice-gmail-refresh-token"

    encrypted = service.encrypt(plaintext, user_id=user_a)

    # Attempting to decrypt with user_b must fail due to AAD tag mismatch
    with pytest.raises(TokenDecryptionError, match="authentication tag mismatch or corrupted ciphertext"):
        service.decrypt(encrypted, user_id=user_b)


def test_key_rotation_and_fallback():
    old_secret = "legacy-secret-key-version-0-12345"
    new_secret = "brand-new-primary-secret-key-67890"

    # Encrypt with old service (pretend it was encrypted under old secret with version prefix 0)
    old_service = TokenEncryptionService(primary_secret=old_secret)
    user_id = "rotation-user-3333"
    token = "long-lived-refresh-token-xyz"

    # Create ciphertext with old key and version byte 0
    raw_old = bytearray(base64.urlsafe_b64decode(old_service.encrypt(token, user_id=user_id).encode("ascii")))
    raw_old[0] = 0  # Set version to 0
    # Recompute with old cipher for version 0
    nonce = raw_old[1:13]
    ct_with_tag = old_service._primary_aesgcm.encrypt(bytes(nonce), token.encode("utf-8"), user_id.encode("utf-8"))
    payload_v0 = bytes([0]) + bytes(nonce) + ct_with_tag
    b64_v0 = base64.urlsafe_b64encode(payload_v0).decode("ascii")

    # Service with new primary key and old key as fallback
    new_service = TokenEncryptionService(primary_secret=new_secret, fallback_secret=old_secret)

    # Decrypting v0 should use fallback key successfully
    decrypted = new_service.decrypt(b64_v0, user_id=user_id)
    assert decrypted == token

    # Rotating token should produce a v1 ciphertext encrypted under new primary key
    rotated_b64 = new_service.rotate_token(b64_v0, user_id=user_id)
    raw_rotated = base64.urlsafe_b64decode(rotated_b64.encode("ascii"))
    assert raw_rotated[0] == CURRENT_KEY_VERSION

    # Rotated ciphertext can be decrypted by new service even without fallback
    strict_new_service = TokenEncryptionService(primary_secret=new_secret)
    assert strict_new_service.decrypt(rotated_b64, user_id=user_id) == token


def test_invalid_input_handling():
    service = TokenEncryptionService(primary_secret="primary-secret-key-for-testing-12345")

    with pytest.raises(ValueError):
        service.encrypt("", user_id="u1")
    with pytest.raises(ValueError):
        service.encrypt("data", user_id="")

    with pytest.raises(ValueError):
        service.decrypt("", user_id="u1")
    with pytest.raises(ValueError):
        service.decrypt("data", user_id="")

    with pytest.raises(TokenDecryptionError):
        service.decrypt("not-base-64!#$%", user_id="u1")

    # Truncated payload
    short_payload = base64.urlsafe_b64encode(b"short").decode("ascii")
    with pytest.raises(TokenDecryptionError, match="Ciphertext payload too short"):
        service.decrypt(short_payload, user_id="u1")
