from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from datetime import datetime
from typing import List, Optional
import logging

from ..database import get_db
from ..schemas.food import (
    FoodAnalysisRequest, FoodAnalysisResponse, FoodRecommendationRequest,
    FoodRecommendationResponse, FoodComparisonRequest, FoodComparisonResponse
)
from ..config import settings
from ..dependencies import get_current_user, get_optional_user_no_auth
from ..services.llm_service import LLMService
from ..services.qloo_service import QlooService
from ..services.food_detection_service import FoodAnalysisService

router = APIRouter()
logger = logging.getLogger(__name__)

class FoodService:
    def __init__(self, db):
        self.db = db
        self.llm_service = LLMService()
        self.qloo_service = QlooService()
        self.food_analysis_service = FoodAnalysisService(self.llm_service, self.qloo_service)

    async def analyze_food_by_name(self, food_name: str, user_id: Optional[int] = None) -> FoodAnalysisResponse:
        """Analyze food by name using LLM and Qloo services"""
        try:
            # Analyze food using the new service
            analysis_result = await self.food_analysis_service.analyze_food_by_name(food_name, user_id)
            
            # Convert to FoodAnalysisResponse format
            return FoodAnalysisResponse(
                food_name=analysis_result["food_name"],
                confidence_score=analysis_result["confidence_score"],
                category=analysis_result["category"],
                cuisine_type=analysis_result["cuisine_type"],
                nutrition=analysis_result["nutrition"],
                cultural_context=analysis_result["cultural_context"],
                ingredients=analysis_result["ingredients"],
                recipe=analysis_result["recipe"],
                recommendations=analysis_result["recommendations"],
                health_benefits=analysis_result["health_benefits"],
                dietary_restrictions=analysis_result["dietary_restrictions"],
                allergens=analysis_result["allergens"],
                analysis_date=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Food analysis failed: {str(e)}"
            )

    async def get_food_recommendations(self, request: FoodRecommendationRequest) -> FoodRecommendationResponse:
        """Get personalized food recommendations"""
        try:
            # Get cultural preferences from Qloo
            cultural_preferences = await self.qloo_service.get_user_cultural_preferences(request.user_id)
            
            # Generate recommendations with LLM
            llm_prompt = f"""
            Generate food recommendations based on:
            Preferences: {request.preferences}
            Cuisine Preference: {request.cuisine_preference}
            Dietary Restrictions: {request.dietary_restrictions}
            Nutrition Goals: {request.nutrition_goals}
            Skill Level: {request.skill_level}
            Time Constraint: {request.time_constraint}
            
            Cultural Preferences: {cultural_preferences}
            
            Provide:
            1. Food recommendations with reasons
            2. Cultural insights
            3. Nutrition insights
            4. Cooking tips
            """
            
            llm_response = await self.llm_service.generate_response(llm_prompt)
            recommendation_data = self._parse_recommendations(llm_response, cultural_preferences)
            
            return FoodRecommendationResponse(
                recommendations=recommendation_data["recommendations"],
                cultural_insights=recommendation_data["cultural_insights"],
                nutrition_insights=recommendation_data["nutrition_insights"],
                cooking_tips=recommendation_data["cooking_tips"],
                recommendation_date=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Food recommendations failed: {str(e)}"
            )

    async def compare_foods(self, request: FoodComparisonRequest) -> FoodComparisonResponse:
        """Compare multiple foods"""
        try:
            comparisons = []
            
            for food in request.foods:
                # Get data for each food
                cultural_data = await self.qloo_service.get_food_cultural_context(food)
                nutrition_data = await self.qloo_service.get_nutritional_info(food)
                
                comparison = {
                    "food_name": food,
                    "nutrition_score": nutrition_data.get("overall_score", 0.5),
                    "cultural_relevance": cultural_data.get("relevance_score", 0.5),
                    "taste_profile": nutrition_data.get("taste_profile", {}),
                    "health_benefits": nutrition_data.get("health_benefits", []),
                    "preparation_complexity": nutrition_data.get("complexity", "medium")
                }
                comparisons.append(comparison)
            
            # Generate comparative insights
            comparison_prompt = f"""
            Compare these foods: {', '.join(request.foods)}
            
            Generate:
            1. Comparative insights
            2. Nutritional differences
            3. Cultural significance
            4. Recommendations
            """
            
            llm_response = await self.llm_service.generate_response(comparison_prompt)
            insights = self._parse_comparison_insights(llm_response)
            
            return FoodComparisonResponse(
                comparison_date=datetime.utcnow(),
                comparison_type=request.comparison_type,
                foods=comparisons,
                insights=insights,
                recommendations=self._generate_food_recommendations(comparisons)
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Food comparison failed: {str(e)}"
            )

    def _parse_recommendations(self, llm_response: str, cultural_preferences: dict) -> dict:
        """Parse LLM response into recommendation data"""
        return {
            "recommendations": [
                {
                    "food_name": "Recommended Food",
                    "reason": "Matches your preferences",
                    "similarity_score": 0.8,
                    "cultural_connection": "Connects to your cultural background",
                    "nutritional_benefit": "High in protein"
                }
            ],
            "cultural_insights": ["insight1", "insight2"],
            "nutrition_insights": ["insight1", "insight2"],
            "cooking_tips": ["tip1", "tip2"]
        }

    def _parse_comparison_insights(self, llm_response: str) -> List[str]:
        """Parse comparison insights from LLM response"""
        return ["insight1", "insight2", "insight3"]

    def _generate_food_recommendations(self, comparisons: List[dict]) -> List[str]:
        """Generate recommendations based on comparisons"""
        return ["recommendation1", "recommendation2", "recommendation3"]

# API Endpoints
@router.post("/analyze", response_model=FoodAnalysisResponse)
async def analyze_food(
    request: FoodAnalysisRequest,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Analyze food by name"""
    food_service = FoodService(db)
    
    # Validate that food_name is provided
    if not request.food_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="food_name is required"
        )
    
    # Track event
    if current_user:
        db.analytics.create(
            data={
                "event_type": "feature_use",
                "event_name": "food_analysis",
                "event_data": {"food_name": request.food_name},
                "user_id": current_user.id,
                "timestamp": datetime.utcnow()
            }
        )
    
    return await food_service.analyze_food_by_name(request.food_name, current_user.id if current_user else None)

@router.post("/recommendations", response_model=FoodRecommendationResponse)
async def get_food_recommendations(
    request: FoodRecommendationRequest,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Get food recommendations"""
    food_service = FoodService(db)
    return await food_service.get_food_recommendations(request)

@router.post("/compare", response_model=FoodComparisonResponse)
async def compare_foods(
    request: FoodComparisonRequest,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Compare foods"""
    food_service = FoodService(db)
    return await food_service.compare_foods(request)

@router.get("/trends")
async def get_food_trends(
    timeframe: str = "week",
    db = Depends(get_db)
):
    """Get food trends"""
    return {
        "trends": [
            {"food_name": "plant-based meat", "trend_score": 0.9, "popularity_change": "rising"},
            {"food_name": "fermented foods", "trend_score": 0.8, "popularity_change": "rising"},
            {"food_name": "ancient grains", "trend_score": 0.7, "popularity_change": "stable"}
        ],
        "timeframe": timeframe
    } 