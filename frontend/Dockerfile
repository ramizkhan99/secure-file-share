# Use an official Node.js 22 image as the base image
FROM node:22

ENV VITE_API_URL=/api

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY ./package.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Expose the port that the app runs on
EXPOSE 4173

# Run the application
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4173"]
