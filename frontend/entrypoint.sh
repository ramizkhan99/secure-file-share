 ```bash
 #!/bin/bash
 set -e

 echo "Running entrypoint.sh"

 # Generate certificates
 openssl req -x509 -newkey rsa:4096 \
     -keyout /app/localhost.key \
     -out /app/localhost.crt \
     -days 365 \
     -nodes \
     -subj "/CN=localhost" \
     2>&1 | tee /tmp/openssl.log

 echo "Certificates generated. Output in /tmp/openssl.log"
 ls -l /app

 echo "Starting Vite development server..."
 npm run dev -- --host 0.0.0.0 --port 4173
 ```