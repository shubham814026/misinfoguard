from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import uvicorn
from typing import Optional
import logging

from services.ocr_service import OCRService
from services.nlp_service import NLPService
from services.fact_checker import FactChecker
from services.content_filter import ContentFilter
from utils.file_handler import FileHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MisinfoGuard Python Service",
    description="OCR, NLP, and Fact-Checking Service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ocr_service = OCRService()
nlp_service = NLPService()
fact_checker = FactChecker()
content_filter = ContentFilter()
file_handler = FileHandler()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MisinfoGuard Python Service",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "ocr": "operational",
            "nlp": "operational",
            "fact_checker": "operational"
        }
    }


@app.post("/api/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze image for misinformation
    - Extracts text using OCR
    - Performs NLP analysis
    - Checks for NSFW content
    - Returns extracted text and claims
    """
    try:
        # Validate file
        if not file_handler.validate_file(file):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Save file temporarily
        file_path = await file_handler.save_upload(file)
        
        try:
            # Check for inappropriate content
            if content_filter.is_nsfw(file_path):
                raise HTTPException(
                    status_code=400,
                    detail="Content rejected: Inappropriate or sensitive material detected"
                )
            
            # Extract text from image
            ocr_result = await ocr_service.extract_text(file_path)
            
            # Handle invalid/garbage images
            if ocr_result['status'] == 'invalid':
                return {
                    "success": False,
                    "message": ocr_result['message'],
                    "extracted_text": "",
                    "claims": []
                }
            
            # Handle OCR errors
            if ocr_result['status'] == 'error':
                return {
                    "success": False,
                    "message": ocr_result['message'],
                    "extracted_text": "",
                    "claims": []
                }
            
            extracted_text = ocr_result['text']
            news_items = ocr_result.get('news_items', [extracted_text])
            
            # Analyze each news item separately if multiple detected
            all_claims = []
            news_analyses = []
            
            for idx, news_text in enumerate(news_items):
                # Extract claims for this news item
                claims = await nlp_service.extract_claims(news_text)
                detected_lang = nlp_service.detect_language(news_text)
                
                news_analyses.append({
                    "news_number": idx + 1,
                    "text": news_text,
                    "claims": claims,
                    "language": detected_lang
                })
                all_claims.extend(claims)
            
            # Build response
            response = {
                "success": True,
                "extracted_text": extracted_text,
                "total_claims": len(all_claims)
            }
            
            # If multiple news items detected, provide separate analyses
            if len(news_items) > 1:
                response["message"] = ocr_result['message']
                response["news_count"] = len(news_items)
                response["news_analyses"] = news_analyses
            else:
                # Single news item - keep original format
                response["claims"] = all_claims
                response["language"] = news_analyses[0]["language"] if news_analyses else "en"
            
            return response
            
        finally:
            # Clean up file
            file_handler.cleanup_file(file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/text")
async def analyze_text(data: dict):
    """
    Analyze text for misinformation
    - Performs NLP analysis
    - Extracts claims
    """
    try:
        text = data.get("text", "")
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text is too short or empty")
        
        # Check for inappropriate content
        if content_filter.contains_inappropriate_text(text):
            raise HTTPException(
                status_code=400,
                detail="Content rejected: Inappropriate or sensitive material detected"
            )
        
        # Extract claims using NLP
        claims = await nlp_service.extract_claims(text)
        
        return {
            "success": True,
            "claims": claims,
            "language": nlp_service.detect_language(text)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/fact-check")
async def fact_check(data: dict):
    """
    Fact check claims using Google Search and Fact Check API
    - Searches for evidence
    - Analyzes credibility
    - Returns verdict with sources
    """
    try:
        claims = data.get("claims", [])
        
        if not claims:
            raise HTTPException(status_code=400, detail="No claims provided")
        
        results = await fact_checker.check_claims(claims)
        
        return {
            "success": True,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fact-checking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fact-checking failed: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
