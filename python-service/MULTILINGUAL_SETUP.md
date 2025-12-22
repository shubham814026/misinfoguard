# Multilingual Support Setup Guide

## Overview
The system now supports **100+ languages** using multilingual transformer models for NLP analysis and OCR.

## Changes Made

### 1. **NLP Service (nlp_service.py)**
- ✅ Replaced English-only spaCy model with multilingual `xx_ent_wiki_sm`
- ✅ Added automatic language detection for all text
- ✅ Language-agnostic factual claim detection
- ✅ Support for: English, Spanish, French, German, Hindi, Arabic, Chinese, and more

### 2. **OCR Service (ocr_service.py)**
- ✅ Multilingual OCR support (English, Spanish, French, German, Hindi, Arabic, Chinese)
- ✅ **Multi-news detection**: Automatically separates multiple news items in one image
- ✅ **Garbage detection**: Rejects corrupted/unreadable images with helpful messages
- ✅ Text validation to ensure quality

### 3. **API Response (main.py)**
- ✅ Returns separate analyses for multiple news items
- ✅ Each news item gets its own claims and language detection
- ✅ Clear error messages for invalid images

## Installation Steps

### Step 1: Install Python Dependencies
```bash
cd python-service
pip install -r requirements.txt
```

### Step 2: Download Multilingual spaCy Model
```bash
python -m spacy download xx_ent_wiki_sm
```

### Step 3: Install Tesseract Language Packs
For multilingual OCR, you need Tesseract with language packs:

**Windows:**
```powershell
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# During installation, select additional languages:
# - English (eng)
# - Spanish (spa)
# - French (fra)
# - German (deu)
# - Hindi (hin)
# - Arabic (ara)
# - Chinese Simplified (chi_sim)
```

**Linux/Docker:**
```bash
apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-spa \
    tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-hin \
    tesseract-ocr-ara tesseract-ocr-chi-sim
```

### Step 4: Update Dockerfile (if using Docker)
Add to your Dockerfile:
```dockerfile
# Install Tesseract with multiple languages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-hin \
    tesseract-ocr-ara \
    tesseract-ocr-chi-sim \
    && rm -rf /var/lib/apt/lists/*

# Download spaCy multilingual model
RUN python -m spacy download xx_ent_wiki_sm
```

## API Response Examples

### Single News Item (English)
```json
{
  "success": true,
  "extracted_text": "Breaking: NASA discovers water on Mars...",
  "claims": [
    {
      "text": "NASA discovers water on Mars",
      "language": "en",
      "entities": [{"text": "NASA", "type": "ORG"}],
      "sentiment": "neutral",
      "confidence": 0.85
    }
  ],
  "language": "en",
  "total_claims": 1
}
```

### Multiple News Items (Mixed Languages)
```json
{
  "success": true,
  "message": "Detected 2 separate news items in the image",
  "news_count": 2,
  "extracted_text": "Full text...",
  "total_claims": 3,
  "news_analyses": [
    {
      "news_number": 1,
      "text": "Biden signs new climate bill...",
      "language": "en",
      "claims": [...]
    },
    {
      "news_number": 2,
      "text": "El presidente firma nueva ley...",
      "language": "es",
      "claims": [...]
    }
  ]
}
```

### Garbage/Invalid Image
```json
{
  "success": false,
  "message": "No readable text found in the image. Please upload a clear image with text content.",
  "extracted_text": "",
  "claims": []
}
```

## Supported Languages

### OCR Support (Tesseract):
- English (eng)
- Spanish (spa)
- French (fra)
- German (deu)
- Hindi (hin)
- Arabic (ara)
- Chinese Simplified (chi_sim)

### NLP Analysis Support (spaCy xx_ent_wiki_sm):
100+ languages including:
- All major European languages
- Asian languages (Chinese, Japanese, Korean, Hindi, etc.)
- Arabic and Hebrew
- And many more...

## Factual Claim Detection

Now supports language-specific indicators:
- **English**: is, are, was, were, shows, proves
- **Spanish**: es, son, fue, muestra, prueba
- **French**: est, sont, était, montre, prouve
- **German**: ist, sind, war, zeigt, beweist
- **Hindi**: है, था, दिखाता, साबित
- **Arabic**: هو, كان, يظهر, يثبت

## Testing

Test with different languages:
```bash
# Spanish news
curl -X POST http://localhost:8000/api/analyze/image \
  -F "file=@spanish_news.jpg"

# Hindi news
curl -X POST http://localhost:8000/api/analyze/image \
  -F "file=@hindi_news.jpg"

# Multiple news in one image
curl -X POST http://localhost:8000/api/analyze/image \
  -F "file=@mixed_news.jpg"
```

## Performance Notes

- Initial model load may take 5-10 seconds
- Multilingual OCR is slightly slower than single-language
- Text processing is language-agnostic (no performance difference)
- Recommended: Use GPU for transformer models in production

## Troubleshooting

**Error: "No module named 'xx_ent_wiki_sm'"**
```bash
python -m spacy download xx_ent_wiki_sm
```

**Error: "Tesseract language not found"**
- Install language packs as shown in Step 3

**Low accuracy for specific language:**
- Check if Tesseract language pack is installed
- Verify image quality (minimum 300 DPI recommended)

## Future Enhancements

- [ ] Add more language-specific factual indicators
- [ ] Support for right-to-left languages (Arabic, Hebrew)
- [ ] Optical layout analysis for better news separation
- [ ] Language-specific sentiment analysis models
