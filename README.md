# Secure File Share

This is a file sharing app that encrypts and decrypts file before sending them.

Users can see, download and delete the files they have created and share them with generated links.
Admins can do the same for all available files.

## Security Measures
- Implements JWT for authentication
- Uses both access and refresh token to manage sessions
- Uses HTTP only and Secure cookies
- Files are encrypted at rest using AES-GCM
- Role based access implemented
- Implemented TLS/SSL (currently not working as nginx config broke, will update it soon)
- MFA supported
- Uses Vault for storage of encryption key

> [!CAUTION]
> This application not at all production ready. The TLS certificate is generated and self-signed and the Hashicorp vault image is used in development mode. Even the frontend is started in development mode.
