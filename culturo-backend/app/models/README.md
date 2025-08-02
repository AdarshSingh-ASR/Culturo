# Database Models

This directory previously contained SQLAlchemy models, but we have migrated to **Prisma ORM** for better type safety and developer experience.

## Migration to Prisma

All database models are now defined in the Prisma schema file:
- **Schema**: `../prisma/schema.prisma`
- **Models**: User, UserPreference, Trip, Story, Analytics, FoodAnalysis, TrendAnalysis, Recommendation

## Benefits of Prisma

- **Type Safety**: Full TypeScript-like type safety
- **Auto-completion**: Better IDE support
- **Migrations**: Automatic schema migrations
- **Relations**: Easier relationship management
- **Neon DB**: Perfect integration with serverless PostgreSQL

## Usage

Instead of SQLAlchemy models, use the Prisma client:

```python
from prisma import Prisma

prisma = Prisma()
prisma.connect()

# Create a user
user = prisma.user.create(
    data={
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
)

# Find users
users = prisma.user.find_many(
    where={
        "is_active": True
    }
)

prisma.disconnect()
```

## Old Models

The old SQLAlchemy models in this directory are kept for reference but are no longer used:
- `user.py` - User model
- `trip.py` - Trip model  
- `story.py` - Story model
- `analytics.py` - Analytics model 