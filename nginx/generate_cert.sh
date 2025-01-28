#!/bin/bash

# Create the directory for certificates if it doesn't exist
mkdir -p /etc/nginx/certs

# Generate a self-signed certificate using OpenSSL
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/certs/server.key \
  -out /etc/nginx/certs/server.crt \
  -subj "/C=US/ST=California/L=San Francisco/O=MyOrganization/CN=localhost"

echo "Self-signed certificate generated successfully!"
