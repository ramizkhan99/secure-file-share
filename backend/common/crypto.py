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

def decrypt_file(file_id, file_path, temp_output_path=None, vault_client=None):
    """Decrypt a file using AES-256-GCM"""
    if vault_client is None:
        vault_client = get_vault_client()

    key = get_encryption_key(file_id)
    aesgcm = AESGCM(key)

    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()

        nonce = file_data[:12]
        encrypted_data = file_data[12:]
        associated_data = file_path.encode()

        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, associated_data)

        # Determine where to write the decrypted data
        if temp_output_path:
            output_path = temp_output_path
        else:
            temp_path = f"{file_path}.tmp"
            output_path = temp_path

        # Write to the determined output path
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)

        # If not using a temporary output path, replace the original file
        if not temp_output_path:
            os.replace(temp_path, file_path)

    except Exception as e:
        if not temp_output_path and os.path.exists(temp_path):
            os.remove(temp_path)  # Clean up only if temp_path was used
        raise CryptoError(f"Decryption failed: {str(e)}")