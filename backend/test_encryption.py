import os
import pytest
from security import EncryptionManager

def test_encryption_manager_encrypts_data():
    """Test that EncryptionManager properly encrypts data and output is not plaintext."""
    manager = EncryptionManager()
    plain_text = "This is a secret message for AES encryption test"
    
    encrypted_text = manager.encrypt(plain_text)
    
    # Assert it was encrypted (not equal to plain text and not empty)
    assert encrypted_text != ""
    assert encrypted_text != plain_text
    # Fernet tokens start with 'gAAAAA' typically, indicating base64 encoded token
    assert isinstance(encrypted_text, str)
    assert len(encrypted_text) > len(plain_text)

def test_encryption_manager_decrypts_data():
    """Test that EncryptionManager can decrypt its own encrypted data back to original."""
    manager = EncryptionManager()
    plain_text = "Testing decryption process 123"
    
    encrypted_text = manager.encrypt(plain_text)
    decrypted_text = manager.decrypt(encrypted_text)
    
    # Assert the decrypted text matches the original
    assert decrypted_text == plain_text

def test_empty_string_encryption():
    """Test behavior with empty strings."""
    manager = EncryptionManager()
    assert manager.encrypt("") == ""
    assert manager.decrypt("") == ""

def test_invalid_decryption_returns_original_string():
    """Test behavior when trying to decrypt an invalid token."""
    manager = EncryptionManager()
    invalid_token = "NotAVanillaFernetToken"
    
    # According to current security.py implementation, failing to decrypt returns the original string (or prints error)
    decrypted_text = manager.decrypt(invalid_token)
    assert decrypted_text == invalid_token
