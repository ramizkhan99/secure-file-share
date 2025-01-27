#!/bin/sh
set -e

echo "Running generate-certs.sh"

# Create the output directory if it doesn't exist
mkdir -p /app/certs

# Generate self-signed certificates in /app/certs
openssl req -x509 -newkey rsa:4096 \
    -keyout /app/certs/localhost.key \
    -out /app/certs/localhost.crt \
    -days 365 \
    -nodes \
    -subj "/CN=localhost"

echo "Certificates generated in /app/certs"
ls -l /app/certs

echo "generate-certs.sh completed"
