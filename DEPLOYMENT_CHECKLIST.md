# Culturo Deployment Checklist

## Pre-Deployment Setup

### 1. Database Setup
- [ ] Create Neon database account at [neon.tech](https://neon.tech)
- [ ] Create new project in Neon
- [ ] Copy database connection string
- [ ] Test database connection locally

### 2. External Services Setup
- [ ] Get Clerk API keys (publishable and secret)
- [ ] Get Qloo API key
- [ ] Get Google Gemini API key
- [ ] Get OpenAI API key
- [ ] (Optional) Get Google Places API key
- [ ] (Optional) Get OpenWeather API key

### 3. Repository Preparation
- [ ] Ensure all code is committed to GitHub
- [ ] Test frontend build locally: `cd culturo-frontend && npm run build`
- [ ] Test backend locally: `cd culturo-backend && uvicorn app.main:app --reload`

## Backend Deployment (Render)

### 1. Render Account Setup
- [ ] Create Render account at [render.com](https://render.com)
- [ ] Connect GitHub repository to Render

### 2. Deploy Backend Service
- [ ] Go to Render dashboard
- [ ] Click "New +" → "Blueprint"
- [ ] Select your repository
- [ ] Render will auto-detect `render.yaml`

### 3. Configure Environment Variables
- [ ] Set `DATABASE_URL` (Neon connection string)
- [ ] Set `REDIS_URL` (if using Redis)
- [ ] Set `QLOO_API_KEY`
- [ ] Set `GEMINI_API_KEY`
- [ ] Set `OPENAI_API_KEY`
- [ ] Set `SECRET_KEY` (generate a long random string)
- [ ] Set `CLERK_SECRET_KEY`
- [ ] Set `CLERK_PUBLISHABLE_KEY`
- [ ] Set `CLERK_JWT_ISSUER`
- [ ] Set `CLERK_WEBHOOK_SECRET`
- [ ] (Optional) Set `GOOGLE_PLACES_API_KEY`
- [ ] (Optional) Set `OPENWEATHER_API_KEY`

### 4. Test Backend
- [ ] Wait for deployment to complete
- [ ] Test health endpoint: `https://your-app-name.onrender.com/health`
- [ ] Test API docs: `https://your-app-name.onrender.com/docs`
- [ ] Verify database connection
- [ ] Test authentication endpoints

## Frontend Deployment (Vercel)

### 1. Vercel Account Setup
- [ ] Create Vercel account at [vercel.com](https://vercel.com)
- [ ] Connect GitHub repository to Vercel

### 2. Deploy Frontend Service
- [ ] Go to Vercel dashboard
- [ ] Click "New Project"
- [ ] Import your repository
- [ ] **Important**: Keep root directory as project root (don't change it)
- [ ] Vercel will auto-detect root `vercel.json`

### 3. Configure Environment Variables
- [ ] Set `VITE_API_URL` to your Render backend URL
- [ ] Set `VITE_CLERK_PUBLISHABLE_KEY`
- [ ] Set `VITE_APP_NAME` to "Culturo"
- [ ] Set `VITE_APP_VERSION` to "1.0.0"
- [ ] Set `VITE_ENVIRONMENT` to "production"

### 4. Test Frontend
- [ ] Wait for deployment to complete
- [ ] Visit your Vercel app URL
- [ ] Test authentication flow
- [ ] Test API calls to backend
- [ ] Verify all features work correctly

## Post-Deployment Configuration

### 1. Update CORS Settings
- [ ] Update backend `CORS_ORIGINS` to include your Vercel domain
- [ ] Test cross-origin requests

### 2. Domain Configuration
- [ ] (Optional) Add custom domain to Vercel
- [ ] (Optional) Add custom domain to Render
- [ ] Update environment variables with custom domains

### 3. Monitoring Setup
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Configure logging
- [ ] Set up health checks

## Final Testing

### 1. End-to-End Testing
- [ ] Test user registration/login
- [ ] Test all main features
- [ ] Test API endpoints
- [ ] Test file uploads (if applicable)
- [ ] Test error handling

### 2. Performance Testing
- [ ] Test page load times
- [ ] Test API response times
- [ ] Monitor resource usage

### 3. Security Testing
- [ ] Verify HTTPS is working
- [ ] Test authentication flows
- [ ] Check CORS configuration
- [ ] Verify API key security

## URLs to Remember

### Backend (Render)
- **Service URL**: `https://your-app-name.onrender.com`
- **Health Check**: `https://your-app-name.onrender.com/health`
- **API Docs**: `https://your-app-name.onrender.com/docs`

### Frontend (Vercel)
- **App URL**: `https://your-app-name.vercel.app`
- **Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)

### Database (Neon)
- **Dashboard**: [console.neon.tech](https://console.neon.tech)
- **Connection String**: `postgresql://username:password@ep-example-123456.us-east-1.aws.neon.tech/culturo_db?sslmode=require`

## Troubleshooting

### Common Issues
- [ ] Backend build failures → Check `requirements-render.txt`
- [ ] Database connection issues → Verify `DATABASE_URL`
- [ ] CORS errors → Update `CORS_ORIGINS` in backend
- [ ] Authentication issues → Check Clerk configuration
- [ ] API key errors → Verify all keys are set correctly

### Support Resources
- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Neon Documentation](https://neon.tech/docs)
- [Clerk Documentation](https://clerk.com/docs)

## Notes
- Keep your API keys secure and never commit them to version control
- Monitor your usage to stay within free tier limits
- Consider upgrading to paid plans for production use
- Set up automated backups for your database
- Regular security updates and monitoring 