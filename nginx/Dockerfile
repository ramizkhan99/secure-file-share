FROM nginx:latest

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the certificate generation script
COPY generate_cert.sh /generate_cert.sh

# Make the script executable
RUN chmod +x /generate_cert.sh

# Use entry point to generate the certificate then start nginx
ENTRYPOINT ["/bin/bash", "-c", "/generate_cert.sh && nginx -g 'daemon off;'"]
