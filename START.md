# 🚀 Getting Started with MisinfoGuard

Welcome to **MisinfoGuard**! This guide will walk you through the steps required to set up, configure, and launch the application on your local machine.

---

## 🏗️ System Overview

MisinfoGuard is composed of three primary services:
1. **Frontend:** React application utilizing Tailwind CSS and Framer Motion.
2. **Backend:** Node.js Express server connected to MongoDB to track analytics and manage uploads.
3. **Python AI Service:** FastAPI service running Tesseract OCR, spaCy NLP models, and Google APIs for fact-checking.

---

## ⚙️ Prerequisites

Before launching the project, ensure you have the following installed:

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Highly Recommended for containerized setup)
* Alternatively, for local setup:
  * [Node.js](https://nodejs.org/) (v18 or higher)
  * [Python](https://www.python.org/) (v3.9 or higher)
  * [MongoDB](https://www.mongodb.com/try/download/community) (Local instance or MongoDB Atlas URI)
  * [Tesseract OCR Engine](https://github.com/UB-Mannheim/tesseract/wiki) (Must be added to system PATH if running locally)

---

## 🔑 1. Configure Environment Variables

You must create and configure `.env` files for each service. Example configurations are provided in each directory.

### A. Frontend Environment
Create [frontend/.env](file:///d:/misinfoguard/frontend/.env):
```env
REACT_APP_API_URL=http://localhost:5000
```

### B. Backend Environment
Create [backend/.env](file:///d:/misinfoguard/backend/.env):
```env
NODE_ENV=development
PORT=5000
PYTHON_SERVICE_URL=http://localhost:8000  # Change to http://python-service:8000 when using Docker
MONGODB_URI=mongodb://localhost:27017/misinfoguard # Change to mongodb://mongodb:27017/misinfoguard when using Docker
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX_ID=your_custom_search_engine_id
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads
```

### C. Python Service Environment
Create [python-service/.env](file:///d:/misinfoguard/python-service/.env):
```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX_ID=your_custom_search_engine_id
PORT=8000
DEBUG=True
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf,gif
```

> [!NOTE]
> Detailed instructions on how to obtain `GOOGLE_API_KEY` and `GOOGLE_CX_ID` can be found in the [GOOGLE_API_SETUP.md](file:///d:/misinfoguard/GOOGLE_API_SETUP.md) guide.

---

## 🐳 Option A: Launch with Docker (Recommended)

Docker handles all service installation, environment configurations, and dependency resolution automatically.

1. Navigate to the root directory.
2. Build and start all services using Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. Once the build finishes and all health checks pass:
   * **Frontend:** [http://localhost:3000](http://localhost:3000)
   * **Backend API:** [http://localhost:5000](http://localhost:5000)
   * **Python Service Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 Option B: Run Locally (Without Docker)

If you prefer to run the services individually on your host OS:

### 1. Run MongoDB Database
Make sure your local MongoDB instance is running on port `27017`.

### 2. Launch the Node.js Backend
```bash
cd backend
npm install
npm run dev
```
*Server runs on [http://localhost:5000](http://localhost:5000)*

### 3. Launch the Python AI Service
Ensure Tesseract OCR is installed and available in your environment variables.
```bash
cd python-service
# (Optional) Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload --port 8000
```
*Service runs on [http://localhost:8000](http://localhost:8000)*

### 4. Launch the React Frontend
```bash
cd frontend
npm install
npm start
```
*Frontend opens on [http://localhost:3000](http://localhost:3000)*

---

## 🧪 Verification & Health Checks

To verify that the system components are communicating correctly, visit the following URLs in your browser or make API requests:

* **Backend Health Check:** `GET` [http://localhost:5000/api/health](http://localhost:5000/api/health)
* **Python Service Health Check:** `GET` [http://localhost:8000/health](http://localhost:8000/health)
