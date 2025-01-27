#!/bin/sh

# Wait for Vault to start
sleep 5

# Export Vault address and token
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Enable KV secrets engine
vault secrets enable -path=secret kv-v2

# Create and store the encryption key
vault kv put secret/file-encryption-key key=$(openssl rand -base64 32)

echo "Vault initialization complete."
