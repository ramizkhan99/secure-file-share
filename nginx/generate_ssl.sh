#!/bin/bash
# nginx/generate_ssl_cert.sh

# Generate self-signed SSL certificate and key
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/key.pem \
  -out /etc/nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Adjust permissions (optional but recommended)
chmod 600 /etc/nginx/ssl/key.pem
