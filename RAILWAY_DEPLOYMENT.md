# 🚀 Railway Deployment Guide for Culturo

This guide will help you deploy your Culturo Cultural Intelligence Platform on Railway.

## 📋 Prerequisites

Before deploying, make sure you have:

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your Culturo project pushed to GitHub
3. **API Keys**: All required API keys (Qloo, Gemini, OpenAI, Clerk, etc.)
4. **Database**: Railway PostgreSQL (will be set up during deployment)

## 🏗️ Project Structure for Railway

Your project should have this structure for Railway deployment:

```
culturo/
├── main.py                 # Main entry point for Railway
├── unified_server.py       # Unified server for API + Frontend
├── railway.json           # Railway configuration
├── nixpacks.toml          # Build configuration
├── Procfile               # Process definition
├── runtime.txt            # Python version
├── package.json           # Root package.json
├── env.template           # Environment variables template
├── culturo-backend/       # FastAPI backend
├── culturo-frontend/      # React frontend
└── image/                 # App screenshots
```

## 🚀 Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your repository is ready for deployment:

```bash
# Ensure all files are committed
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Connect to Railway

1. **Login to Railway**: Go to [railway.app](https://railway.app) and sign in
2. **Create New Project**: Click "New Project"
3. **Deploy from GitHub**: Select "Deploy from GitHub repo"
4. **Select Repository**: Choose your Culturo repository
5. **Deploy**: Railway will automatically detect the configuration and start building

### 3. Configure Environment Variables

After the initial deployment, configure your environment variables:

1. **Go to Variables Tab**: In your Railway project dashboard
2. **Add Environment Variables**: Use the template from `env.template`

#### Required Environment Variables:

```env
# Railway Environment
RAILWAY_ENVIRONMENT=production
PORT=8000

# Database (Railway will provide this)
DATABASE_URL=postgresql://...

# Redis (Railway will provide this)
REDIS_URL=redis://...

# API Keys
QLOO_API_KEY=your_qloo_api_key
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Authentication
CLERK_SECRET_KEY=your_clerk_secret_key
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key

# Application Settings
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
```

### 4. Add PostgreSQL Database

1. **Add PostgreSQL**: In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. **Connect to App**: The database will automatically be connected to your app
3. **Environment Variables**: Railway will automatically set `DATABASE_URL`

### 5. Add Redis (Optional)

1. **Add Redis**: In Railway dashboard, click "New" → "Database" → "Redis"
2. **Connect to App**: The Redis instance will automatically be connected
3. **Environment Variables**: Railway will automatically set `REDIS_URL`

### 6. Configure Custom Domain (Optional)

1. **Go to Settings**: In your Railway project
2. **Custom Domains**: Add your custom domain
3. **Update CORS**: Update `CORS_ORIGINS` in environment variables

## 🔧 Configuration Files Explained

### `main.py`
- Main entry point that Railway detects
- Handles both development and production modes
- Automatically detects Railway environment

### `unified_server.py`
- Combines FastAPI backend with React frontend
- Serves static files from React build
- Handles SPA routing

### `railway.json`
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

### `nixpacks.toml`
```toml
[phases.setup]
nixPkgs = ["nodejs", "npm", "python3", "python3Packages.pip"]

[phases.install]
cmds = [
  "cd culturo-frontend && npm install",
  "cd ../culturo-backend && pip install -r requirements.txt"
]

[phases.build]
cmds = [
  "cd culturo-frontend && npm run build"
]

[start]
cmd = "python main.py"
```

## 🌐 How the Unified Server Works

### Production Mode (Railway)
1. **Build Process**: Nixpacks builds both frontend and backend
2. **Frontend Build**: React app is built to `culturo-frontend/dist`
3. **Unified Server**: FastAPI serves both API and frontend
4. **API Routes**: All API calls go to `/api/*`
5. **Frontend Routes**: All other routes serve the React app

### URL Structure
- **API Documentation**: `https://your-app.railway.app/api/docs`
- **Health Check**: `https://your-app.railway.app/api/health`
- **Frontend**: `https://your-app.railway.app/`
- **API Endpoints**: `https://your-app.railway.app/api/v1/*`

## 🔍 Monitoring and Debugging

### Railway Dashboard
- **Logs**: View real-time application logs
- **Metrics**: Monitor CPU, memory, and network usage
- **Deployments**: Track deployment history and status

### Health Check
The app includes a health check endpoint at `/api/health` that Railway uses to monitor the application.

### Logs
Check logs in Railway dashboard for:
- Application startup messages
- API request logs
- Error messages
- Build process logs

## 🚨 Troubleshooting

### Common Issues

#### 1. Build Failures
**Problem**: Frontend or backend build fails
**Solution**: 
- Check logs in Railway dashboard
- Ensure all dependencies are in `requirements.txt` and `package.json`
- Verify Node.js and Python versions

#### 2. Environment Variables
**Problem**: App can't find API keys or database
**Solution**:
- Verify all environment variables are set in Railway
- Check variable names match exactly
- Ensure no extra spaces or quotes

#### 3. Database Connection
**Problem**: Database connection fails
**Solution**:
- Verify PostgreSQL is added to Railway project
- Check `DATABASE_URL` is set correctly
- Ensure database migrations run

#### 4. Frontend Not Loading
**Problem**: Frontend shows blank page or errors
**Solution**:
- Check if frontend build completed successfully
- Verify static files are being served
- Check browser console for errors

#### 5. API Endpoints Not Working
**Problem**: API calls return 404 or errors
**Solution**:
- Verify API routes are prefixed with `/api`
- Check FastAPI app is running correctly
- Ensure CORS is configured properly

### Debug Commands

```bash
# Check Railway logs
railway logs

# Check environment variables
railway variables

# Restart the application
railway service restart

# Check service status
railway service status
```

## 🔄 Continuous Deployment

### Automatic Deployments
Railway automatically deploys when you push to your main branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

### Manual Deployments
You can also trigger manual deployments from the Railway dashboard.

## 📊 Performance Optimization

### Railway Resources
- **CPU**: Adjust based on your needs (0.5 to 4 cores)
- **Memory**: Start with 512MB, increase if needed
- **Storage**: 1GB should be sufficient for most deployments

### Application Optimization
- **Caching**: Use Redis for session and data caching
- **Database**: Optimize queries and use connection pooling
- **Static Files**: Frontend assets are served efficiently

## 🔒 Security Considerations

### Environment Variables
- Never commit API keys to Git
- Use Railway's secure environment variable storage
- Rotate keys regularly

### CORS Configuration
- Configure CORS origins properly
- Only allow necessary domains
- Use HTTPS in production

### Database Security
- Use Railway's managed PostgreSQL
- Enable SSL connections
- Regular backups

## 📈 Scaling

### Horizontal Scaling
Railway supports automatic scaling based on:
- CPU usage
- Memory usage
- Request volume

### Vertical Scaling
You can increase resources in Railway dashboard:
- More CPU cores
- More memory
- Faster storage

## 🎉 Success!

Once deployed, your Culturo app will be available at:
`https://your-app-name.railway.app`

### Next Steps
1. **Test All Features**: Verify all functionality works
2. **Set Up Monitoring**: Configure alerts and monitoring
3. **Custom Domain**: Add your custom domain
4. **SSL Certificate**: Railway provides automatic SSL
5. **Backup Strategy**: Set up database backups

## 📞 Support

If you encounter issues:
1. Check Railway documentation
2. Review application logs
3. Verify environment configuration
4. Test locally first
5. Contact Railway support if needed

---

**Happy Deploying! 🚀**

Your Culturo Cultural Intelligence Platform is now ready for production on Railway! 