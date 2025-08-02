from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class FoodCategoryEnum(str, Enum):
    main_dish = "main_dish"
    appetizer = "appetizer"
    dessert = "dessert"
    beverage = "beverage"
    snack = "snack"
    soup = "soup"
    salad = "salad"
    bread = "bread"
    pasta = "pasta"
    seafood = "seafood"
    meat = "meat"
    vegetarian = "vegetarian"
    vegan = "vegan"

class CuisineEnum(str, Enum):
    italian = "italian"
    chinese = "chinese"
    japanese = "japanese"
    indian = "indian"
    mexican = "mexican"
    french = "french"
    thai = "thai"
    mediterranean = "mediterranean"
    american = "american"
    korean = "korean"
    vietnamese = "vietnamese"
    greek = "greek"
    turkish = "turkish"
    moroccan = "moroccan"
    lebanese = "lebanese"

class FoodAnalysisRequest(BaseModel):
    food_name: str = Field(..., min_length=1, max_length=100, description="Name of the food to analyze")
    cuisine_type: Optional[CuisineEnum] = None
    include_nutrition: bool = True
    include_cultural_context: bool = True
    include_recommendations: bool = True
    user_id: Optional[int] = None

class NutritionInfo(BaseModel):
    calories: float
    protein: float
    carbohydrates: float
    fat: float
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    cholesterol: Optional[float] = None
    vitamins: Dict[str, float] = {}
    minerals: Dict[str, float] = {}

class CulturalContext(BaseModel):
    origin_country: str
    origin_region: Optional[str] = None
    historical_significance: Optional[str] = None
    traditional_occasions: List[str]
    cultural_symbolism: Optional[str] = None
    preparation_methods: List[str]
    serving_traditions: List[str]

class Ingredient(BaseModel):
    name: str
    quantity: Optional[str] = None
    category: str  # protein, vegetable, grain, etc.
    nutritional_contribution: Optional[str] = None

class Recipe(BaseModel):
    title: str
    description: str
    ingredients: List[Ingredient]
    instructions: List[str]
    cooking_time: str
    difficulty_level: str
    servings: int
    cuisine_type: str

class FoodRecommendation(BaseModel):
    food_name: str
    reason: str
    similarity_score: float
    cultural_connection: Optional[str] = None
    nutritional_benefit: Optional[str] = None

class FoodAnalysisResponse(BaseModel):
    food_name: str
    confidence_score: float
    category: FoodCategoryEnum
    cuisine_type: CuisineEnum
    nutrition: Optional[NutritionInfo] = None
    cultural_context: Optional[CulturalContext] = None
    ingredients: List[Ingredient]
    recipe: Optional[Recipe] = None
    recommendations: List[FoodRecommendation]
    health_benefits: List[str]
    dietary_restrictions: List[str]
    allergens: List[str]
    analysis_date: datetime

class FoodRecommendationRequest(BaseModel):
    preferences: str = Field(..., min_length=10, max_length=1000)
    cuisine_preference: Optional[CuisineEnum] = None
    dietary_restrictions: List[str] = []
    nutrition_goals: Optional[str] = None
    skill_level: str = "beginner"  # beginner, intermediate, advanced
    time_constraint: Optional[str] = None
    user_id: Optional[int] = None

class FoodRecommendationResponse(BaseModel):
    recommendations: List[FoodRecommendation]
    cultural_insights: List[str]
    nutrition_insights: List[str]
    cooking_tips: List[str]
    recommendation_date: datetime

class FoodComparisonRequest(BaseModel):
    foods: List[str] = Field(..., min_items=2, max_items=5)
    comparison_type: str = "nutritional"  # nutritional, cultural, taste
    user_id: Optional[int] = None

class FoodComparison(BaseModel):
    food_name: str
    nutrition_score: float
    cultural_relevance: float
    taste_profile: Dict[str, float]
    health_benefits: List[str]
    preparation_complexity: str

class FoodComparisonResponse(BaseModel):
    comparison_date: datetime
    comparison_type: str
    foods: List[FoodComparison]
    insights: List[str]
    recommendations: List[str]

class FoodTrend(BaseModel):
    food_name: str
    trend_score: float
    popularity_change: str  # rising, stable, declining
    social_media_mentions: int
    cultural_factors: List[str]
    health_trends: List[str]

class FoodTrendsResponse(BaseModel):
    trends_date: datetime
    timeframe: str
    trends: List[FoodTrend]
    insights: List[str]
    predictions: List[str]

class FoodNutritionGoal(BaseModel):
    goal_type: str  # weight_loss, muscle_gain, maintenance, health
    target_calories: Optional[int] = None
    target_protein: Optional[float] = None
    target_carbs: Optional[float] = None
    target_fat: Optional[float] = None
    dietary_restrictions: List[str] = []
    user_id: int

class FoodNutritionGoalResponse(BaseModel):
    id: int
    goal_type: str
    target_calories: Optional[int] = None
    target_protein: Optional[float] = None
    target_carbs: Optional[float] = None
    target_fat: Optional[float] = None
    dietary_restrictions: List[str]
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FoodLogEntry(BaseModel):
    food_name: str
    quantity: str
    meal_type: str  # breakfast, lunch, dinner, snack
    consumed_at: datetime
    nutrition_actual: Optional[NutritionInfo] = None
    user_id: int

class FoodLogEntryCreate(BaseModel):
    food_name: str
    quantity: str
    meal_type: str
    consumed_at: datetime
    user_id: int

class FoodLogEntryResponse(BaseModel):
    id: int
    food_name: str
    quantity: str
    meal_type: str
    consumed_at: datetime
    nutrition_actual: Optional[NutritionInfo] = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True 