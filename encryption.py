"""AES-256-GCM encryption helpers for report files."""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_key() -> str:
    """Generate a random 256-bit AES key, returned as base64 string for DB storage."""
    raw_key = AESGCM.generate_key(bit_length=256)
    return base64.b64encode(raw_key).decode("utf-8")


def encrypt_file(data: bytes, key_b64: str) -> bytes:
    """Encrypt data with AES-256-GCM. Returns nonce (12 bytes) + ciphertext."""
    key = base64.b64decode(key_b64)
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce, data, None)
    return nonce + ciphertext


def decrypt_file(encrypted_data: bytes, key_b64: str) -> bytes:
    """Decrypt AES-256-GCM data. Expects nonce (first 12 bytes) + ciphertext."""
    key = base64.b64decode(key_b64)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return AESGCM(key).decrypt(nonce, ciphertext, None)
