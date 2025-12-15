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

Write-Host "Environment files created successfully!" -ForegroundColor Green
Write-Host "Please edit the .env files with your actual API keys:" -ForegroundColor Yellow
Write-Host "  - backend/.env" -ForegroundColor Cyan
Write-Host "  - python-service/.env" -ForegroundColor Cyan
Write-Host "  - frontend/.env" -ForegroundColor Cyan
