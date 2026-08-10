import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

class EncryptionManager:
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY")
        if self.key:
            self.key = self.key.strip()
            
        if not self.key:
            # Jika tidak ada kunci, generate baru (hanya untuk fallback, sebaiknya di .env)
            self.key = Fernet.generate_key()
            print("WARNING: ENCRYPTION_KEY not found in .env. Generated a temporary key.")
        
        if isinstance(self.key, str):
            self.key = self.key.encode()
            
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, plain_text: str) -> str:
        """Enkripsi teks biasa menjadi token terenkripsi (AES-256/Fernet)."""
        if not plain_text:
            return ""
        try:
            encrypted_text = self.cipher_suite.encrypt(plain_text.encode())
            return encrypted_text.decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            return plain_text

    def decrypt(self, encrypted_text: str) -> str:
        """Dekripsi token terenkripsi kembali menjadi teks biasa."""
        if not encrypted_text:
            return ""
        try:
            decrypted_text = self.cipher_suite.decrypt(encrypted_text.encode())
            return decrypted_text.decode()
        except Exception as e:
            # Jika gagal dekripsi, mungkin data tidak terenkripsi atau kunci salah
            print(f"Decryption error: {e}")
            return encrypted_text

# Singleton instance
encryptor = EncryptionManager()
