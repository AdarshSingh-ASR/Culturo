from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class TravelStyleEnum(str, Enum):
    cultural = "cultural"
    adventure = "adventure"
    relaxing = "relaxing"
    luxury = "luxury"
    budget = "budget"
    family = "family"
    romantic = "romantic"
    business = "business"
    educational = "educational"
    wellness = "wellness"

class BudgetLevelEnum(str, Enum):
    budget = "budget"
    moderate = "moderate"
    luxury = "luxury"
    ultra_luxury = "ultra_luxury"

class TravelPlanningRequest(BaseModel):
    destination: str = Field(..., min_length=2, max_length=100)
    travel_style: Optional[TravelStyleEnum] = None
    duration: Optional[str] = None
    budget_level: Optional[BudgetLevelEnum] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    group_size: int = Field(1, ge=1, le=20)
    cultural_interests: List[str] = []
    dietary_restrictions: List[str] = []
    accessibility_needs: List[str] = []
    user_id: Optional[int] = None

class CulturalActivity(BaseModel):
    name: str
    description: str
    cultural_significance: str
    duration: str
    cost_range: str
    location: str
    best_time: str
    difficulty_level: str
    cultural_insights: List[str]

class Accommodation(BaseModel):
    name: str
    type: str  # hotel, hostel, apartment, etc.
    description: str
    cultural_authenticity: float
    price_range: str
    location: str
    amenities: List[str]
    cultural_features: List[str]

class LocalExperience(BaseModel):
    name: str
    description: str
    cultural_value: float
    duration: str
    cost: str
    location: str
    local_contact: Optional[str] = None
    cultural_context: str

class DayItinerary(BaseModel):
    day_number: int
    date: Optional[date] = None
    theme: str
    activities: List[CulturalActivity]
    meals: List[Dict[str, Any]]
    accommodation: Optional[Accommodation] = None
    cultural_notes: List[str]
    practical_tips: List[str]

class CulturalInsight(BaseModel):
    aspect: str  # customs, etiquette, history, etc.
    description: str
    importance: str
    practical_tips: List[str]
    cultural_context: str

class TravelPlanningResponse(BaseModel):
    destination: str
    duration: str
    travel_style: str
    budget_estimate: str
    cultural_insights: str  # Changed to string to match frontend
    itinerary: List[Dict[str, Any]]  # Simplified to match frontend expectations
    local_experiences: List[LocalExperience]
    accommodation_recommendations: List[Accommodation]
    cultural_activities: List[CulturalActivity]
    practical_information: Dict[str, Any]
    safety_considerations: List[str]
    cultural_etiquette: List[str]
    planning_date: datetime
    llm_summary: Optional[str] = None
    qloo_places: Optional[List[Dict[str, Any]]] = None

class DestinationRecommendation(BaseModel):
    destination: str
    country: str
    region: str
    cultural_score: float
    match_score: float
    reasons: List[str]
    cultural_highlights: List[str]
    best_time_to_visit: str
    cultural_events: List[str]

class DestinationRecommendationRequest(BaseModel):
    interests: List[str] = []
    travel_style: Optional[TravelStyleEnum] = None
    budget_level: Optional[BudgetLevelEnum] = None
    duration_range: str = "1-2 weeks"
    preferred_climate: Optional[str] = None
    cultural_preferences: List[str] = []
    user_id: Optional[int] = None

class DestinationRecommendationResponse(BaseModel):
    recommendations: List[DestinationRecommendation]
    insights: List[str]
    cultural_themes: List[str]
    recommendation_date: datetime

class CulturalEvent(BaseModel):
    name: str
    description: str
    date: str
    location: str
    cultural_significance: str
    duration: str
    cost: str
    participation_level: str  # spectator, participant, both

class CulturalEventsRequest(BaseModel):
    destination: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    event_types: List[str] = []
    user_id: Optional[int] = None

class CulturalEventsResponse(BaseModel):
    destination: str
    events: List[CulturalEvent]
    cultural_calendar: Dict[str, List[str]]
    insights: List[str]
    planning_tips: List[str]
    response_date: datetime

class LocalGuide(BaseModel):
    name: str
    specialization: str
    languages: List[str]
    experience_years: int
    cultural_expertise: List[str]
    rating: float
    contact_info: Dict[str, str]
    availability: str

class LocalGuidesRequest(BaseModel):
    destination: str
    specialization: Optional[str] = None
    languages: List[str] = []
    user_id: Optional[int] = None

class LocalGuidesResponse(BaseModel):
    destination: str
    guides: List[LocalGuide]
    insights: List[str]
    booking_tips: List[str]
    response_date: datetime

class TravelBudget(BaseModel):
    accommodation: float
    food: float
    activities: float
    transportation: float
    cultural_experiences: float
    miscellaneous: float
    total: float
    currency: str = "USD"

class TravelBudgetRequest(BaseModel):
    destination: str
    duration: str
    group_size: int
    budget_level: BudgetLevelEnum
    include_cultural_activities: bool = True
    user_id: Optional[int] = None

class TravelBudgetResponse(BaseModel):
    destination: str
    duration: str
    budget: TravelBudget
    cost_breakdown: Dict[str, Any]
    money_saving_tips: List[str]
    cultural_investment_recommendations: List[str]
    response_date: datetime

class TravelSafety(BaseModel):
    category: str  # health, security, cultural, etc.
    risk_level: str  # low, medium, high
    description: str
    recommendations: List[str]
    emergency_contacts: List[str]

class TravelSafetyRequest(BaseModel):
    destination: str
    travel_dates: Optional[str] = None
    user_id: Optional[int] = None

class TravelSafetyResponse(BaseModel):
    destination: str
    safety_overview: str
    safety_concerns: List[TravelSafety]
    health_considerations: List[str]
    cultural_safety: List[str]
    emergency_information: Dict[str, Any]
    response_date: datetime

class TravelReview(BaseModel):
    id: int
    destination: str
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    review_text: str
    cultural_experience_rating: int
    cultural_insights: List[str]
    recommendations: List[str]
    created_at: datetime

class TravelReviewCreate(BaseModel):
    destination: str
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    review_text: str
    cultural_experience_rating: int
    cultural_insights: List[str]
    recommendations: List[str]

class TravelReviewResponse(BaseModel):
    id: int
    destination: str
    user_id: int
    rating: int
    review_text: str
    cultural_experience_rating: int
    cultural_insights: List[str]
    recommendations: List[str]
    created_at: datetime

    class Config:
        from_attributes = True 