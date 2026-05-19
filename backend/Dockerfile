FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (production + devDeps not needed at runtime)
RUN npm install --omit=dev

# Copy application files
COPY . .

# Create uploads directory and set ownership to non-root user
RUN mkdir -p uploads && chown -R node:node /app

# Run as non-root user for security
USER node

# Expose port
EXPOSE 5000

# Start server (production-safe, NOT nodemon)
CMD ["node", "server.js"]
