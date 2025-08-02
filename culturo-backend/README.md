# 🌍 Culturo Backend

A comprehensive cultural intelligence platform that combines the best features from multiple Qloo-powered applications. Culturo provides personalized recommendations, trend analysis, story development, food analysis, travel planning, and cultural insights using AI and the Qloo Taste API.

## 🚀 Features

### Python Version Compatibility

**Important**: If you're using Python 3.13, the requirements.txt file has been configured to use PyTorch instead of TensorFlow, as TensorFlow is not yet compatible with Python 3.13.

- **Python 3.8-3.12**: Use standard TensorFlow
- **Python 3.13**: Use PyTorch (already configured in requirements.txt)

### 🎯 Core Features
- **Cultural Taste Analysis**: Deep insights into user preferences across music, food, fashion, books, and more
- **AI-Powered Recommendations**: Personalized suggestions using Gemini, OpenAI, and other LLMs

- **Story Development**: AI-assisted story creation with audience analysis
- **Food Intelligence**: Computer vision-based food recognition and nutritional analysis
- **Travel Planning**: Culturally-aware trip itineraries based on personal tastes
- **Content Generation**: Create personalized narratives and creative content

### 🔧 Technical Features
- **Multi-LLM Support**: Gemini, OpenAI GPT, Claude, and more
- **Real-time Processing**: Fast API responses with caching
- **Image Analysis**: Food recognition and cultural context
- **Clerk Authentication**: Modern authentication with Clerk integration
- **User Management**: Secure user profiles and preferences
- **Analytics**: User behavior tracking and insights
- **Scalable Architecture**: Microservices-ready design

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Prisma**: Type-safe database ORM
- **Redis**: Caching and session management
- **Neon DB**: Serverless PostgreSQL database

### AI & ML
- **Google Gemini**: Primary LLM for content generation
- **OpenAI GPT**: Alternative LLM for specific tasks
- **PyTorch/TensorFlow**: Machine learning models (PyTorch for Python 3.13)
- **OpenCV**: Computer vision for food analysis
- **Sentence Transformers**: Text embeddings

### APIs & Services
- **Qloo Taste API**: Cultural affinity data
- **Clerk API**: Authentication and user management
- **Google Places API**: Location-based recommendations
- **OpenWeather API**: Weather-based planning
- **Pusher**: Real-time notifications

## 📁 Project Structure

```
culturo-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── dependencies.py         # Dependency injection
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── trip.py
│   │   ├── story.py
│   │   └── analytics.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── trip.py
│   │   ├── story.py
│   │   └── recommendations.py
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py

│   │   ├── stories.py
│   │   ├── food.py
│   │   ├── travel.py
│   │   ├── recommendations.py
│   │   └── analytics.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── qloo_service.py
│   │   ├── llm_service.py
│   │   ├── auth_service.py
│   │   ├── food_service.py
│   │   ├── story_service.py
│   │   └── travel_service.py
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   ├── validators.py
│   │   └── cache.py
│   └── ml/                     # Machine learning models
│       ├── __init__.py
│       ├── food_analyzer.py
│       └── models/
├── alembic/                    # Database migrations
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── docker-compose.yml         # Docker configuration
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Neon DB account (free tier available)
- Redis (optional, for caching)
- API keys for:
  - Qloo Taste API
  - Google Gemini
  - OpenAI (optional)
  - Google Places (optional)
  - Clerk (for authentication)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd culturo-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note**: If you encounter TensorFlow installation issues with Python 3.13, the requirements.txt has been pre-configured to use PyTorch which is compatible with Python 3.13.

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database credentials
   ```

5. **Set up database**
   ```bash
   # Set up Prisma with Neon DB
   python setup_prisma.py
   
   # Or manually:
   # prisma generate
   # prisma db push
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication (Clerk)
- `GET /api/v1/auth/me` - Get current user profile
- `GET /api/v1/auth/clerk/me` - Get Clerk user information
- `POST /api/v1/auth/clerk/verify` - Verify Clerk token
- `POST /api/v1/clerk/webhook` - Clerk webhook handler

#### Cultural Analysis

- `POST /api/v1/audience/analyze` - Analyze target audiences

#### Story Development
- `POST /api/v1/stories/analyze` - Analyze story ideas
- `POST /api/v1/stories/generate` - Generate story content
- `POST /api/v1/stories/surprise` - Get random story prompts

#### Food Intelligence
- `POST /api/v1/food/analyze` - Analyze food images
- `POST /api/v1/food/recommendations` - Get food recommendations
- `GET /api/v1/food/nutrition` - Get nutritional information

#### Travel Planning
- `POST /api/v1/travel/plan` - Create travel itineraries
- `GET /api/v1/travel/destinations` - Get destination recommendations
- `POST /api/v1/travel/cultural-insights` - Get cultural insights

#### Recommendations
- `POST /api/v1/recommendations/personalized` - Get personalized recommendations
- `POST /api/v1/recommendations/cultural` - Get culturally-aware recommendations
- `GET /api/v1/recommendations/trending` - Get trending items

## 🔧 Configuration

### Neon DB Setup

1. **Create a Neon Account**
   - Sign up at [neon.tech](https://neon.tech)
   - Create a new project

2. **Get Your Connection String**
   - Copy the connection string from your Neon dashboard
   - It should look like: `postgresql://username:password@ep-example-123456.us-east-1.aws.neon.tech/culturo_db?sslmode=require`

3. **Update Environment Variables**
   - Add the connection string to your `.env` file as `DATABASE_URL`

4. **Initialize Database**
   ```bash
   python setup_prisma.py
   ```

### Clerk Authentication Setup

1. **Create a Clerk Account**
   - Sign up at [clerk.com](https://clerk.com)
   - Create a new application

2. **Configure Clerk Application**
   - Get your API keys from the Clerk dashboard
   - Set up JWT templates for your application
   - Configure webhook endpoints

3. **Environment Variables**
   - Add Clerk configuration to your `.env` file
   - Set up webhook secrets for secure communication

4. **Frontend Integration**
   - Use Clerk's React/Vue/Angular components
   - Handle authentication state in your frontend
   - Send JWT tokens with API requests

### Environment Variables

```env
# Database (Neon DB)
DATABASE_URL=postgresql://username:password@ep-example-123456.us-east-1.aws.neon.tech/culturo_db?sslmode=require
REDIS_URL=redis://localhost:6379/0

# API Keys
QLOO_API_KEY=your_qloo_api_key
QLOO_API_URL=https://api.qloo.com/v1
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Authentication
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Clerk Authentication
CLERK_SECRET_KEY=your_clerk_secret_key
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_JWT_ISSUER=https://clerk.culturo.com
CLERK_WEBHOOK_SECRET=your_clerk_webhook_secret

# External APIs
GOOGLE_PLACES_API_KEY=your_google_places_key
OPENWEATHER_API_KEY=your_openweather_key

# Monitoring
PROMETHEUS_ENABLED=true
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file

```

## 📊 Monitoring

The application includes:
- **Health checks**: `/health` endpoint
- **Metrics**: Prometheus integration
- **Logging**: Structured logging with different levels
- **Error tracking**: Comprehensive error handling

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   # Set production environment variables
   export ENVIRONMENT=production
   export DATABASE_URL=your_production_db_url
   ```

2. **Database Migration**
   ```bash
   alembic upgrade head
   ```

3. **Start with Gunicorn**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Production

```bash
# Build production image
docker build -t culturo-backend:latest .

# Run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project combines features and inspiration from:
- **Trend Compass AI**: Trend analysis and forecasting
- **Story Scope**: Story development and audience analysis
- **Qloo TasteBot**: Multi-domain recommendations
- **Appmuseme**: Travel planning with cultural intelligence
- **CultureTrip Planner**: Trip itinerary generation
- **neXtaste**: Food analysis and recommendations
- **ApoShorts AI**: Creative content generation

---

**Built with ❤️ for cultural intelligence and personalized experiences** 