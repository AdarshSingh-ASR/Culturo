# Backend Deployment Guide (Render)

## Prerequisites
- Render account
- GitHub repository
- Neon database (PostgreSQL)
- Redis instance (optional, for caching)
- API keys for external services

## Step 1: Database Setup (Neon)

1. Go to [neon.tech](https://neon.tech) and create an account
2. Create a new project
3. Copy the connection string (it will look like):
   ```
   postgresql://username:password@ep-example-123456.us-east-1.aws.neon.tech/culturo_db?sslmode=require
   ```

## Step 2: Deploy to Render

### Option A: Using render.yaml (Recommended)
1. Go to [render.com](https://render.com)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Configure the environment variables (see Step 3)

### Option B: Manual Setup
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Set the following:
   - **Name**: `culturo-backend`
   - **Root Directory**: `culturo-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements-render.txt && prisma generate`
   - **Start Command**: `prisma db push && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Step 3: Configure Environment Variables

In your Render service dashboard, add the following environment variables:

### Required Variables (set these in Render dashboard):
- `DATABASE_URL`: Your Neon database connection string
- `REDIS_URL`: Your Redis connection string (optional)
- `QLOO_API_KEY`: Your Qloo API key
- `GEMINI_API_KEY`: Your Google Gemini API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: A long, random secret key for JWT tokens
- `CLERK_SECRET_KEY`: Your Clerk secret key
- `CLERK_PUBLISHABLE_KEY`: Your Clerk publishable key
- `CLERK_JWT_ISSUER`: Your Clerk JWT issuer URL
- `CLERK_WEBHOOK_SECRET`: Your Clerk webhook secret

### Optional Variables:
- `GOOGLE_PLACES_API_KEY`: Google Places API key
- `OPENWEATHER_API_KEY`: OpenWeather API key

### Fixed Variables (already in render.yaml):
- `CORS_ORIGINS`: `["https://your-app-name.vercel.app"]`
- `ENVIRONMENT`: `production`
- `DEBUG`: `false`

## Step 4: Database Migration

After deployment, the database will be automatically migrated using:
```bash
prisma db push
```

## Step 5: Update Frontend Configuration

Update your frontend's `VITE_API_URL` to point to your Render backend:
```env
VITE_API_URL=https://your-app-name.onrender.com/api
```

## Step 6: Test the Deployment

1. Visit your Render service URL
2. Test the health endpoint: `https://your-app-name.onrender.com/health`
3. Test the API documentation: `https://your-app-name.onrender.com/docs`

## Troubleshooting

### Common Issues:

1. **Build Failures**: 
   - Check if all dependencies are in `requirements-render.txt`
   - Ensure Python version is 3.11

2. **Database Connection Issues**:
   - Verify `DATABASE_URL` is correct
   - Check if Neon database is accessible

3. **CORS Issues**:
   - Update `CORS_ORIGINS` to include your Vercel frontend URL

4. **API Key Issues**:
   - Verify all API keys are correctly set in Render environment variables

### Logs:
- Check Render service logs for detailed error information
- Monitor the health endpoint for service status

## Notes
- Render will automatically scale your service based on traffic
- The service will sleep after 15 minutes of inactivity (free tier)
- Consider upgrading to a paid plan for always-on service
- Your API will be available at `https://your-app-name.onrender.com` 