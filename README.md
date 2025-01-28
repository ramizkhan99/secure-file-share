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
