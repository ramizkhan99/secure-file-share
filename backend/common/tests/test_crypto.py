from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
from django.test import TestCase
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from common.crypto import (
    generate_encryption_key,
    store_encryption_key,
    get_encryption_key,
    encrypt_file,
    decrypt_file,
    CryptoError
)
import base64

class CryptoTests(TestCase):
    def setUp(self):
        # Create test directory
        self.test_dir = tempfile.mkdtemp()
        self.test_data = b"This is test data for encryption with some binary content \x00\x01\x02\x03"
        self.file_id = "test123"
        self.key = generate_encryption_key()
        
        # Create test file
        self.test_file_path = os.path.join(self.test_dir, "test_file.txt")
        with open(self.test_file_path, 'wb') as f:
            f.write(self.test_data)

        # Setup mock vault client
        self.vault_patcher = patch('common.vault.get_vault_client')
        self.mock_vault = self.vault_patcher.start()
        self.mock_client = MagicMock()
        self.mock_vault.return_value = self.mock_client
        
        # Setup mock KV responses
        self.stored_keys = {}
        def mock_store_secret(path, secret):
            self.stored_keys[path] = secret
        def mock_read_secret(path):
            if path not in self.stored_keys:
                raise Exception("Key not found")
            return {'data': {'data': self.stored_keys[path]}}
            
        self.mock_client.secrets.kv.v2.create_or_update_secret.side_effect = mock_store_secret
        self.mock_client.secrets.kv.v2.read_secret_version.side_effect = mock_read_secret

    def tearDown(self):
        # Clean up test directory and all its contents
        shutil.rmtree(self.test_dir)
        self.vault_patcher.stop()

    def test_encryption_key_generation(self):
        key = generate_encryption_key()
        self.assertEqual(len(key), 32)  # 256-bit key
        self.assertTrue(isinstance(key, bytes))
        # Verify the key can be used with AESGCM
        aesgcm = AESGCM(key)
        self.assertIsInstance(aesgcm, AESGCM)

    def test_key_storage_and_retrieval(self):
        # Store the key
        store_encryption_key(self.file_id, self.key)
        
        # Retrieve the key
        retrieved_key = get_encryption_key(self.file_id)
        self.assertEqual(self.key, retrieved_key)
        
        # Verify the retrieved key is valid for AESGCM
        aesgcm = AESGCM(retrieved_key)
        self.assertIsInstance(aesgcm, AESGCM)

    def test_file_encryption_decryption(self):
        # Store the key first
        store_encryption_key(self.file_id, self.key)
        
        # Get original file stats
        original_stats = os.stat(self.test_file_path)
        
        # Encrypt the file
        encrypt_file(self.file_id, self.test_file_path)
        
        # Verify the file still exists
        self.assertTrue(os.path.exists(self.test_file_path))
        
        # Verify the file content has changed
        with open(self.test_file_path, 'rb') as f:
            encrypted_content = f.read()
        self.assertNotEqual(encrypted_content, self.test_data)
        
        # Decrypt the file
        decrypt_file(self.file_id, self.test_file_path)
        
        # Verify the file still exists
        self.assertTrue(os.path.exists(self.test_file_path))
        
        # Verify the content is restored exactly
        with open(self.test_file_path, 'rb') as f:
            decrypted_content = f.read()
        self.assertEqual(decrypted_content, self.test_data)

    def test_encryption_with_different_key_fails(self):
        # Store the original key
        store_encryption_key(self.file_id, self.key)
        
        # Encrypt with original key
        encrypt_file(self.file_id, self.test_file_path)
        
        # Save encrypted content
        with open(self.test_file_path, 'rb') as f:
            encrypted_content = f.read()
        
        # Try to decrypt with a different key
        different_key = generate_encryption_key()
        store_encryption_key(self.file_id, different_key)
        
        # Attempt to decrypt should raise an exception
        with self.assertRaises(CryptoError):
            decrypt_file(self.file_id, self.test_file_path)
            
        # Verify original encrypted content wasn't corrupted
        with open(self.test_file_path, 'rb') as f:
            current_content = f.read()
        self.assertEqual(current_content, encrypted_content)

    def test_tampered_data_fails(self):
        # Encrypt the file
        encrypt_file(self.file_id, self.test_file_path)
        
        # Tamper with the encrypted data
        with open(self.test_file_path, 'rb+') as f:
            data = bytearray(f.read())
            # Modify a byte in the encrypted portion (after nonce)
            data[15] ^= 1
            f.seek(0)
            f.write(data)
        
        # Attempt to decrypt should fail
        with self.assertRaises(CryptoError):
            decrypt_file(self.file_id, self.test_file_path)

    def test_large_file_handling(self):
        # Create a larger test file (5MB)
        large_data = os.urandom(5 * 1024 * 1024)  # 5MB of random data
        large_file_path = os.path.join(self.test_dir, "large_file.bin")
        with open(large_file_path, 'wb') as f:
            f.write(large_data)
        
        # Store the key
        store_encryption_key(self.file_id, self.key)
        
        # Encrypt and decrypt
        encrypt_file(self.file_id, large_file_path)
        decrypt_file(self.file_id, large_file_path)
        
        # Verify content
        with open(large_file_path, 'rb') as f:
            decrypted_content = f.read()
        self.assertEqual(decrypted_content, large_data) 