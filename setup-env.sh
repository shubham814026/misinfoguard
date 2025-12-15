#!/bin/bash

# Copy backend environment file
cd backend
cp .env.example .env

# Copy Python service environment file  
cd ../python-service
cp .env.example .env

# Copy frontend environment file
cd ../frontend
cp .env.example .env

# Create uploads directory
cd ..
mkdir -p uploads

echo "Environment files created successfully!"
echo "Please edit the .env files with your actual API keys:"
echo "  - backend/.env"
echo "  - python-service/.env"
echo "  - frontend/.env"
