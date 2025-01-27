import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from common.vault import get_vault_client

class CryptoError(Exception):
    pass

def generate_encryption_key():
    """Generate a new AES-256 key for GCM"""
    return AESGCM.generate_key(bit_length=256)  # 32 bytes

def store_encryption_key(file_id, key):
    """Store the encryption key in Vault"""
    vault_client = get_vault_client()
    if not vault_client:
        raise Exception("Could not connect to vault")
    path = f'secret/data/file-encryption-key/{file_id}'
    vault_client.secrets.kv.v2.create_or_update_secret(
        path=path,
        secret={'key': key.hex()}  # Store hex-encoded key
    )

def get_encryption_key(file_id):
    """Retrieve the encryption key from Vault"""
    path = f'secret/data/file-encryption-key/{file_id}'
    vault_client = get_vault_client()
    if not vault_client:
        raise Exception("Could not connect to vault")
    response = get_vault_client().secrets.kv.v2.read_secret_version(path=path)
    return bytes.fromhex(response['data']['data']['key'])

def encrypt_file(file_id, file_path):
    """
    Encrypt a file using AES-256-GCM
    """
    # Get or generate key
    try:
        key = get_encryption_key(file_id)
    except Exception:
        key = generate_encryption_key()
        store_encryption_key(file_id, key)

    # Initialize AESGCM
    aesgcm = AESGCM(key)
    
    # Generate a random 96-bit (12 byte) nonce
    nonce = os.urandom(12)
    
    # Read file
    with open(file_path, 'rb') as file:
        data = file.read()
    
    # File path as associated data for additional authentication
    associated_data = file_path.encode()
    
    try:
        # Encrypt and authenticate data
        encrypted_data = aesgcm.encrypt(nonce, data, associated_data)
        
        # Combine nonce and encrypted data
        final_data = nonce + encrypted_data
        
        # Write to temp file and replace
        temp_path = f"{file_path}.tmp"
        with open(temp_path, 'wb') as file:
            file.write(final_data)
        os.replace(temp_path, file_path)
            
    except Exception as e:
        raise CryptoError(f"Encryption failed: {str(e)}")

def decrypt_file(file_id, file_path):
    """
    Decrypt a file using AES-256-GCM
    """
    print("Decrypt called with ID:", file_id)  # Add this debug print
    print("Decrypt called with path:", file_path)  # Add this debug print
    
    # Get key
    try:
        key = get_encryption_key(file_id)
        print("Retrieved key for ID:", file_id)  # Add this debug print
    except Exception as e:
        print("Error getting key:", str(e))  # Add this debug print
        raise
        
    aesgcm = AESGCM(key)
    
    # Define temp_path outside try block
    temp_path = f"{file_path}.tmp"
    
    try:
        # Read encrypted file
        with open(file_path, 'rb') as file:
            file_data = file.read()
            print("Read file size:", len(file_data))  # Add this debug print
        
        # Extract nonce and ciphertext
        nonce = file_data[:12]  # First 12 bytes
        encrypted_data = file_data[12:]  # Rest is encrypted data
        print("Nonce size:", len(nonce))  # Add this debug print
        print("Encrypted data size:", len(encrypted_data))  # Add this debug print
        
        # File path as associated data for authentication
        associated_data = file_path.encode()
        
        # Decrypt and verify
        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, associated_data)
        
        # Write to temp file and replace
        with open(temp_path, 'wb') as file:
            file.write(decrypted_data)
        os.replace(temp_path, file_path)
            
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise CryptoError(f"Decryption failed: {str(e)}")