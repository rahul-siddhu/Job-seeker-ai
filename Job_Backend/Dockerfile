# Use the Alpine-based Node.js 20.16.0 image
FROM node:20.16.0-alpine

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy all project files to the container
COPY . .

# Install dependencies
RUN npm install

# Expose port 5001
EXPOSE 5001

# Set the entry point to use npm
ENTRYPOINT ["npm"]

# Command to run the application
CMD ["run", "start"]
