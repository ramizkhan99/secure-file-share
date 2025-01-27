# nginx/Dockerfile

FROM nginx:latest

# Create the SSL directory
RUN mkdir -p /etc/nginx/ssl

# Copy the script to generate SSL certificates
COPY ./generate_ssl.sh /etc/nginx/ssl/

# Copy the Nginx configuration
COPY ./nginx.conf /etc/nginx/

# Run the script to generate certificates
RUN chmod 700 /etc/nginx/ssl/generate_ssl.sh
RUN /etc/nginx/ssl/generate_ssl.sh

# Expose ports
EXPOSE 80
EXPOSE 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
