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


# ── FAISS Integrity Validation Checksums ─────────────────────────────────────
import hashlib

def calculate_file_hash(filepath: str) -> str:
    """Menghitung hash SHA256 dari sebuah berkas."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        return ""

def write_faiss_checksum(db_path: str):
    """Menulis checksum SHA256 untuk index.faiss dan index.pkl."""
    index_faiss_path = os.path.join(db_path, "index.faiss")
    index_pkl_path = os.path.join(db_path, "index.pkl")
    hash_faiss = calculate_file_hash(index_faiss_path)
    hash_pkl = calculate_file_hash(index_pkl_path)
    
    checksum_path = os.path.join(db_path, "index.sha256")
    os.makedirs(db_path, exist_ok=True)
    with open(checksum_path, "w") as f:
        f.write(f"{hash_faiss}\n{hash_pkl}")

def verify_faiss_checksum(db_path: str) -> bool:
    """Memverifikasi kecocokan checksum SHA256 sebelum deserialisasi."""
    index_faiss_path = os.path.join(db_path, "index.faiss")
    index_pkl_path = os.path.join(db_path, "index.pkl")
    checksum_path = os.path.join(db_path, "index.sha256")
    
    if not os.path.exists(checksum_path):
        return False
        
    try:
        with open(checksum_path, "r") as f:
            lines = f.read().splitlines()
        if len(lines) < 2:
            return False
        expected_hash_faiss, expected_hash_pkl = lines[0], lines[1]
        
        actual_hash_faiss = calculate_file_hash(index_faiss_path)
        actual_hash_pkl = calculate_file_hash(index_pkl_path)
        
        return (actual_hash_faiss == expected_hash_faiss) and (actual_hash_pkl == expected_hash_pkl)
    except Exception as e:
        print(f"[FAISS Integrity] Error verifying checksum: {e}")
        return False
