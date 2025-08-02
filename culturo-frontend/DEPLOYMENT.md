# Frontend Deployment Guide (Vercel)

## Prerequisites
- Vercel account
- GitHub repository connected to Vercel
- Clerk account and API keys

## Step 1: Prepare Environment Variables

Create a `.env.production` file in the `culturo-frontend` directory with the following content:

```env
# Production environment variables for Culturo Frontend
# Update these values with your actual production URLs and keys

# API Configuration - Update with your Render backend URL
VITE_API_URL=https://your-app-name.onrender.com/api

# Clerk Authentication - Update with your actual Clerk keys
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here

# Other configuration
VITE_APP_NAME=Culturo
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=production
```

## Step 2: Deploy to Vercel

### Option A: Using Vercel CLI
1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to the root directory: `cd /path/to/culturo`
3. Run: `vercel --prod`

### Option B: Using Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. **Important**: Keep the root directory as the project root (don't change it)
5. Configure environment variables in the Vercel dashboard:
   - `VITE_API_URL`: Your Render backend URL
   - `VITE_CLERK_PUBLISHABLE_KEY`: Your Clerk publishable key
   - `VITE_APP_NAME`: Culturo
   - `VITE_APP_VERSION`: 1.0.0
   - `VITE_ENVIRONMENT`: production

## Step 3: Configure Environment Variables in Vercel

In your Vercel project dashboard:
1. Go to Settings → Environment Variables
2. Add the following variables:
   - `VITE_API_URL`: `https://your-app-name.onrender.com/api`
   - `VITE_CLERK_PUBLISHABLE_KEY`: Your actual Clerk publishable key
   - `VITE_APP_NAME`: `Culturo`
   - `VITE_APP_VERSION`: `1.0.0`
   - `VITE_ENVIRONMENT`: `production`

## Step 4: Update CORS in Backend

Make sure your backend CORS settings include your Vercel domain:
```python
CORS_ORIGINS=["https://your-app-name.vercel.app"]
```

## Notes
- The root `vercel.json` file is configured for optimal deployment
- Vercel will automatically build your project using the root `npm run build` command
- The build process will navigate to `culturo-frontend` and build the Vite app
- Your app will be available at `https://your-app-name.vercel.app` 