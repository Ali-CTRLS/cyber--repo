# Encryption Flow Instructions

This document explains how file encryption is designed in this project and how to implement the runtime flow using the existing crypto helpers.

## Scope

This flow applies to the Flask app in this repository, using AES-256-GCM from the `cryptography` package.

Primary crypto helper file:
- `encryption.py`

Primary report metadata model:
- `models.py` -> `Report`

Storage location for encrypted files:
- `Config.UPLOAD_FOLDER` in `config.py` (defaults to `storage/reports/`)

## Cryptography Design

The project uses authenticated encryption (AEAD) with AES-256-GCM:
- Key size: 256 bits (32 bytes)
- Nonce size: 12 bytes
- Authentication tag: generated and appended by AES-GCM
- Stored file bytes format: `nonce || ciphertext+tag`

Benefits:
- Confidentiality: file content is encrypted
- Integrity: tampering causes decryption to fail (`InvalidTag`)

## Available Helper Functions

In `encryption.py`:
- `generate_key() -> str`
  - Generates a random 256-bit key
  - Returns base64-encoded string for database storage
- `encrypt_file(data: bytes, key_b64: str) -> bytes`
  - Decodes key from base64
  - Generates random 12-byte nonce
  - Returns `nonce + ciphertext_and_tag`
- `decrypt_file(encrypted_data: bytes, key_b64: str) -> bytes`
  - Splits first 12 bytes as nonce
  - Decrypts remaining bytes

## End-to-End Encryption Flow

### 1. Upload and Encrypt (Doctor/report creation path)

1. Receive plaintext report file bytes from request.
2. Generate per-report key via `generate_key()`.
3. Encrypt plaintext via `encrypt_file(plaintext, key_b64)`.
4. Generate unique filename (for example UUID with `.enc` extension).
5. Write encrypted bytes to `Config.UPLOAD_FOLDER`.
6. Save report metadata in DB (`Report` model):
   - `encrypted_file_path`: absolute or relative path to encrypted file
   - `encryption_key`: base64 data encryption key
7. Commit transaction.

### 2. Download and Decrypt (Authorized read path)

1. Load `Report` record by ID/appointment and enforce authorization.
2. Read `encrypted_file_path` bytes from disk.
3. Decrypt via `decrypt_file(encrypted_bytes, report.encryption_key)`.
4. Return plaintext bytes as file response.
5. If decryption fails (tag mismatch), reject request and log security event.

## Data Storage Split

The design intentionally separates data and key material:
- Ciphertext file: filesystem (`storage/reports/`)
- Key and metadata: SQLite (`reports` table)

This reduces risk versus storing plaintext and supports secure at-rest handling.

## Security Notes

1. Never reuse nonces for the same key.
2. Never log plaintext report contents or encryption keys.
3. Treat `Report.encryption_key` as sensitive data in backups and exports.
4. Enforce RBAC before decrypting any report.
5. Rotate to a KMS-based key strategy for production deployments.

## Study Roadmap (What To Learn)

Use this section as your learning checklist before implementing or hardening encryption features.

### 1. Cryptography Basics

What to understand:
- Symmetric vs asymmetric encryption
- Encryption at rest vs encryption in transit
- Why randomness and entropy matter

YouTube search keys:
- `cryptography basics for beginners`
- `symmetric vs asymmetric encryption explained`
- `data at rest vs data in transit`

### 2. AES and GCM Mode

What to understand:
- How AES block cipher works at a high level
- Why GCM is AEAD (confidentiality + integrity)
- Nonce uniqueness requirement in GCM

YouTube search keys:
- `AES explained simply`
- `AES GCM mode explained`
- `AEAD authenticated encryption tutorial`
- `why nonce must be unique in AES GCM`

### 3. Authentication Tag and Tamper Detection

What to understand:
- What the GCM authentication tag does
- How tag verification blocks modified ciphertext
- Common decryption failure reasons (InvalidTag)

YouTube search keys:
- `AES GCM authentication tag explained`
- `cryptography invalidtag exception`
- `ciphertext integrity verification`

### 4. Key Management Fundamentals

What to understand:
- Data Encryption Key (DEK) concept
- Key generation, storage, rotation, and access control
- Why keys should not be logged or hardcoded

YouTube search keys:
- `key management best practices`
- `DEK vs KEK explained`
- `envelope encryption explained`
- `application secrets management tutorial`

### 5. Python Cryptography Implementation

What to understand:
- `cryptography` package structure
- `AESGCM.encrypt()` and `AESGCM.decrypt()` usage
- Byte handling, Base64 encoding/decoding, file I/O safety

YouTube search keys:
- `python cryptography AESGCM example`
- `python encrypt and decrypt file AES GCM`
- `base64 encode decode python security`

### 6. Flask Security Integration

What to understand:
- Secure file upload patterns in Flask
- Authorization checks before sensitive reads
- Error handling without leaking sensitive details

YouTube search keys:
- `flask secure file upload`
- `flask role based access control`
- `flask send_file secure download`
- `flask error handling security best practices`

### 7. OWASP and Practical App Security

What to understand:
- Sensitive data exposure risks
- Broken access control risks
- Logging and monitoring for security events

YouTube search keys:
- `OWASP Top 10 sensitive data exposure`
- `OWASP broken access control explained`
- `secure logging practices for web applications`

### 8. Production-Level Hardening

What to understand:
- Moving from DB-stored DEKs to KMS/HSM workflows
- Backup encryption and key separation
- Audit trails and incident response basics

YouTube search keys:
- `AWS KMS envelope encryption tutorial`
- `Azure Key Vault encryption key management`
- `application encryption architecture best practices`

## Suggested Study Order

1. Cryptography Basics
2. AES + GCM + Authentication Tag
3. Key Management
4. Python AES-GCM Coding
5. Flask Authorization + Secure Upload/Download
6. OWASP Security Risks
7. KMS and Production Architecture

## Current Repository Status

- The crypto primitives are implemented in `encryption.py`.
- The report metadata fields exist in `models.py` (`encrypted_file_path`, `encryption_key`).
- The active blueprints currently do not call `encrypt_file` or `decrypt_file` yet.

So, this file documents the required integration flow and expected behavior when wiring report upload/download routes.

## Minimal Integration Skeleton

Use this as implementation guidance in a report upload handler:

```python
from encryption import generate_key, encrypt_file

plaintext = uploaded_file.read()
key_b64 = generate_key()
encrypted_bytes = encrypt_file(plaintext, key_b64)

# write encrypted_bytes to disk, store path and key_b64 in Report
```

And in a download handler:

```python
from encryption import decrypt_file

encrypted_bytes = open(report.encrypted_file_path, "rb").read()
plaintext = decrypt_file(encrypted_bytes, report.encryption_key)

# return plaintext as download response
```
