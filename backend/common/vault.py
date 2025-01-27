import os
import hvac

def get_vault_client():
    """Initialize and return a vault client only when needed"""
    vault_addr = os.environ.get('VAULT_ADDR', 'http://localhost:8200')
    vault_token = os.environ.get('VAULT_TOKEN', 'your_root_token')

    client = hvac.Client(
        url=vault_addr,
        token=vault_token,
        verify=False  # Disable SSL verification (only for development without TLS)
    )
    
    return client if client.is_authenticated() else None 