from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CategoryEnum(str, Enum):
    movies = "movies"
    music = "music"
    books = "books"
    food = "food"
    travel = "travel"
    fashion = "fashion"
    brands = "brands"
    art = "art"
    events = "events"
    experiences = "experiences"

class RecommendationTypeEnum(str, Enum):
    personalized = "personalized"
    cultural = "cultural"
    trending = "trending"
    collaborative = "collaborative"
    content_based = "content_based"

class RecommendationRequest(BaseModel):
    preferences: str = Field(..., min_length=10, max_length=2000)
    category: Optional[CategoryEnum] = None
    user_id: Optional[int] = None
    limit: int = Field(10, ge=1, le=50)
    include_cultural_context: bool = True
    include_similar_items: bool = True
    filter_by_rating: Optional[float] = None
    # New fields for user demographics and specific preferences
    age: Optional[str] = None  # Must match Qloo API age ranges
    gender: Optional[str] = None  # "male" or "female"
    movie_name: Optional[str] = None  # Specific movie preference
    book_name: Optional[str] = None  # Specific book preference
    place_name: Optional[str] = None  # Specific place preference

class RecommendationItem(BaseModel):
    name: str
    type: str
    category: CategoryEnum
    rating: float
    cultural_context: str
    description: str
    cultural_significance: Optional[str] = None
    target_audience: List[str]
    cultural_elements: List[str]
    popularity_score: float
    personalization_score: float
    metadata: Dict[str, Any] = {}

class CulturalInsight(BaseModel):
    insight_type: str  # preference_pattern, cultural_connection, etc.
    description: str
    confidence: float
    supporting_evidence: List[str]
    cultural_relevance: float

class RecommendationResponse(BaseModel):
    category: CategoryEnum
    items: List[RecommendationItem]
    cultural_insights: List[CulturalInsight]
    recommendation_reasoning: List[str]
    user_preference_summary: str
    cultural_profile: Dict[str, float]
    recommendation_date: datetime

class CulturalRecommendationRequest(BaseModel):
    cultural_interests: List[str] = []
    cultural_background: Optional[str] = None
    preferred_cultures: List[str] = []
    category: Optional[CategoryEnum] = None
    user_id: Optional[int] = None
    limit: int = Field(10, ge=1, le=50)

class CulturalRecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    cultural_connections: List[str]
    cross_cultural_insights: List[str]
    cultural_learning_opportunities: List[str]
    recommendation_date: datetime

class TrendingItem(BaseModel):
    name: str
    type: str
    category: CategoryEnum
    trend_score: float
    popularity_change: str  # rising, stable, declining
    cultural_factors: List[str]
    social_media_mentions: int
    cultural_relevance: float
    description: str

class TrendingItemsResponse(BaseModel):
    category: Optional[CategoryEnum] = None
    timeframe: str
    items: List[TrendingItem]
    cultural_trends: List[str]
    insights: List[str]
    response_date: datetime

class UserPreference(BaseModel):
    category: CategoryEnum
    preferences: List[str]
    cultural_elements: List[str]
    rating_history: List[Dict[str, Any]]
    last_updated: datetime

class UserPreferenceUpdate(BaseModel):
    category: CategoryEnum
    preferences: List[str]
    cultural_elements: List[str]
    user_id: int

class UserPreferenceResponse(BaseModel):
    user_id: int
    preferences: List[UserPreference]
    cultural_profile: Dict[str, float]
    preference_strength: Dict[str, float]
    last_updated: datetime

    class Config:
        from_attributes = True

class RecommendationFeedback(BaseModel):
    id: int
    recommendation_id: str
    user_id: int
    item_name: str
    category: CategoryEnum
    rating: int = Field(..., ge=1, le=5)
    feedback_type: str  # like, dislike, neutral, cultural_relevance
    feedback_text: Optional[str] = None
    cultural_relevance_rating: Optional[int] = None
    created_at: datetime

class RecommendationFeedbackCreate(BaseModel):
    recommendation_id: str
    user_id: int
    item_name: str
    category: CategoryEnum
    rating: int = Field(..., ge=1, le=5)
    feedback_type: str
    feedback_text: Optional[str] = None
    cultural_relevance_rating: Optional[int] = None

class RecommendationFeedbackResponse(BaseModel):
    id: int
    recommendation_id: str
    user_id: int
    item_name: str
    category: CategoryEnum
    rating: int
    feedback_type: str
    feedback_text: Optional[str] = None
    cultural_relevance_rating: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CollaborativeFilteringRequest(BaseModel):
    user_id: int
    category: Optional[CategoryEnum] = None
    similar_users_count: int = Field(10, ge=1, le=100)
    limit: int = Field(10, ge=1, le=50)

class CollaborativeFilteringResponse(BaseModel):
    user_id: int
    similar_users: List[Dict[str, Any]]
    recommendations: List[RecommendationItem]
    similarity_scores: Dict[str, float]
    response_date: datetime

class ContentBasedRequest(BaseModel):
    item_name: str
    category: CategoryEnum
    user_id: Optional[int] = None
    limit: int = Field(10, ge=1, le=50)
    similarity_threshold: float = Field(0.5, ge=0.0, le=1.0)

class ContentBasedResponse(BaseModel):
    source_item: str
    category: CategoryEnum
    similar_items: List[RecommendationItem]
    similarity_scores: Dict[str, float]
    content_features: Dict[str, Any]
    response_date: datetime

class RecommendationAnalytics(BaseModel):
    total_recommendations: int
    average_rating: float
    cultural_relevance_score: float
    user_engagement_rate: float
    category_distribution: Dict[str, int]
    cultural_insights_generated: int
    feedback_positive_rate: float

class RecommendationAnalyticsResponse(BaseModel):
    user_id: Optional[int] = None
    timeframe: str
    analytics: RecommendationAnalytics
    top_categories: List[str]
    cultural_trends: List[str]
    improvement_suggestions: List[str]
    response_date: datetime

class CulturalProfile(BaseModel):
    cultural_background: str
    interests: List[str]
    preferences: Dict[str, float]
    cultural_affinities: List[str]
    learning_goals: List[str]
    cultural_experience_level: str

class CulturalProfileUpdate(BaseModel):
    user_id: int
    cultural_background: Optional[str] = None
    interests: Optional[List[str]] = None
    preferences: Optional[Dict[str, float]] = None
    cultural_affinities: Optional[List[str]] = None
    learning_goals: Optional[List[str]] = None
    cultural_experience_level: Optional[str] = None

class CulturalProfileResponse(BaseModel):
    user_id: int
    profile: CulturalProfile
    last_updated: datetime
    profile_completeness: float

    class Config:
        from_attributes = True 