# Use the official Vault image
FROM hashicorp/vault:latest

ENV VAULT_DEV_ROOT_TOKEN_ID=root

# Install openssl
RUN apk add --no-cache openssl

# Expose Vault's default port
EXPOSE 8200

# Copy the initialization script into the container
COPY init-vault.sh /init-vault.sh

# Make the script executable
RUN chmod +x /init-vault.sh

# Start Vault in -dev mode and run the initialization script
CMD ["sh", "-c", "vault server -dev -dev-listen-address=0.0.0.0:8200 & sleep 5 && /init-vault.sh && tail -f /dev/null"]
