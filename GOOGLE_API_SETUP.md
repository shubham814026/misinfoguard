# Setting Up Google API for Fact Checking

## Why You Need This:
The fact-checking feature uses Google's APIs to:
- Search for evidence across the web
- Check Google's Fact Check database
- Find trusted sources to verify claims

**Without API keys: You get 50% credibility with "No sources found"**

## Step-by-Step Setup:

### 1. Get Google API Key (Free - 100 searches/day)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable APIs:
   - Go to **APIs & Services** → **Library**
   - Search and enable: **Custom Search API**
   - Search and enable: **Fact Check Tools API**
4. Create API Key:
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **API Key**
   - Copy the key (looks like: `AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### 2. Create Custom Search Engine

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click **Add** or **New Search Engine**
3. Settings:
   - **Sites to search**: Leave empty or add `*` to search entire web
   - **Name**: MisinfoGuard Search
   - **Search the entire web**: Turn ON
4. Click **Create**
5. Go to **Control Panel** → **Basics**
6. Copy your **Search engine ID** (looks like: `01234567890abcdef:xxxxxxxx`)

### 3. Add Keys to Your Project

Create `.env` file in `python-service/` folder:

```env
# Google API Keys
GOOGLE_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_CX_ID=01234567890abcdef:xxxxxxxx

# API Configuration  
PORT=8000
DEBUG=True
```

### 4. Update Docker Compose

Add to `docker-compose.yml` under python-service:

```yaml
  python-service:
    build:
      context: ./python-service
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GOOGLE_CX_ID=${GOOGLE_CX_ID}
    env_file:
      - ./python-service/.env
```

### 5. Restart Services

```powershell
docker-compose down
docker-compose up
```

## Free Tier Limits:

- **Custom Search API**: 100 queries/day (free)
- **Fact Check API**: Unlimited (free)

**Need more?** Upgrade to paid ($5 per 1000 queries)

## Alternative: Work Without API Keys

If you don't want to set up APIs, I can update the code to:
- Use simpler heuristics (keywords, patterns)
- Check claim structure and sentiment
- Give reasonable estimates without external searches

**Would you like me to implement the no-API-key fallback mode?**
