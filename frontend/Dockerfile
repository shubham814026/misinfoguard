FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# Set ownership to non-root user
RUN chown -R node:node /app

# Run as non-root user for security
USER node

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "start"]
