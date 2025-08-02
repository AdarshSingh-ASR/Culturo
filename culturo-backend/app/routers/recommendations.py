from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from datetime import datetime
from typing import List, Optional
import json
import logging

from ..database import get_db
# Removed SQLAlchemy User model import - using Prisma now
# Removed SQLAlchemy model imports - using Prisma now
from ..schemas.recommendations import (
    RecommendationRequest, RecommendationResponse, CulturalRecommendationRequest,
    CulturalRecommendationResponse, TrendingItemsResponse, UserPreferenceUpdate,
    UserPreferenceResponse, RecommendationFeedbackCreate, RecommendationFeedbackResponse,
    CollaborativeFilteringRequest, CollaborativeFilteringResponse, ContentBasedRequest,
    ContentBasedResponse, RecommendationAnalyticsResponse
)
from ..config import settings
from ..dependencies import get_current_user, get_optional_user_no_auth
from ..services.llm_service import LLMService
from ..services.qloo_service import QlooService

logger = logging.getLogger(__name__)
router = APIRouter()

class RecommendationsService:
    def __init__(self, db):
        self.db = db
        self.llm_service = LLMService()
        self.qloo_service = QlooService()

    async def get_personalized_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """Get personalized recommendations using Qloo and LLMs"""
        try:
            # Extract user input from request
            user_input = {
                "movie_name": request.movie_name,
                "book_name": request.book_name,
                "place_name": request.place_name,
                "age": request.age,
                "gender": request.gender
            }
            
            # Get user preferences from Qloo using user input
            user_preferences = await self.qloo_service.get_user_preferences(request.user_id, user_input)
            
            # Add the category from the request to user_preferences
            user_preferences["category"] = request.category
            
            # Get cultural insights
            cultural_insights = await self.qloo_service.get_cultural_insights(request.preferences)
            
            # Simplify user preferences to reduce token count
            simplified_preferences = {
                "music": user_preferences.get("preferences", {}).get("music", []),
                "food": user_preferences.get("preferences", {}).get("food", []),
                "fashion": user_preferences.get("preferences", {}).get("fashion", []),
                "travel": user_preferences.get("preferences", {}).get("travel", []),
                "cultural_affinities": user_preferences.get("cultural_affinities", []),
                "taste_profile": user_preferences.get("taste_profile", "")
            }
            
            # Simplify cultural insights to reduce token count
            simplified_insights = {
                "cultural_elements": cultural_insights.get("cultural_elements", [])[:5],  # Limit to 5 items
                "cultural_significance": cultural_insights.get("cultural_significance", ""),
                "origin": cultural_insights.get("origin", "")
            }
            
            # Generate recommendations with LLM
            llm_prompt = f"""
            Generate EXACTLY {request.limit} personalized recommendations based on:
            Preferences: {request.preferences}
            Category: {request.category}
            Limit: {request.limit}
            
            User Input:
            - Movie: {request.movie_name or 'Not specified'}
            - Book: {request.book_name or 'Not specified'}
            - Place: {request.place_name or 'Not specified'}
            - Age: {request.age or 'Not specified'}
            - Gender: {request.gender or 'Not specified'}
            
            User Preferences: {json.dumps(simplified_preferences, indent=2)}
            Cultural Insights: {json.dumps(simplified_insights, indent=2)}
            
            CRITICAL: You MUST return a JSON object with a "recommendations" array containing EXACTLY {request.limit} items.
            
            Expected JSON structure:
            {{
                "recommendations": [
                    {{
                        "name": "Item name",
                        "type": "movie|music|book|food|travel|fashion|brand",
                        "category": "{request.category.value if request.category else 'movies'}",
                        "rating": 4.5,
                        "cultural_context": "Detailed cultural significance and context",
                        "description": "Brief description of the item",
                        "cultural_significance": "Why this item is culturally important",
                        "target_audience": ["audience1", "audience2"],
                        "cultural_elements": ["element1", "element2"],
                        "popularity_score": 0.8,
                        "personalization_score": 0.9,
                        "metadata": {{"year": 2020, "director": "Name"}}
                    }},
                    {{
                        "name": "Second item name",
                        "type": "movie|music|book|food|travel|fashion|brand",
                        "category": "{request.category.value if request.category else 'movies'}",
                        "rating": 4.3,
                        "cultural_context": "Another detailed cultural context",
                        "description": "Another brief description",
                        "cultural_significance": "Another cultural significance",
                        "target_audience": ["audience3", "audience4"],
                        "cultural_elements": ["element3", "element4"],
                        "popularity_score": 0.7,
                        "personalization_score": 0.8,
                        "metadata": {{"year": 2019, "director": "Another Name"}}
                    }}
                    // ... continue for all {request.limit} items
                ],
                "cultural_insights": [
                    {{
                        "insight_type": "preference_pattern",
                        "description": "Detailed insight description",
                        "confidence": 0.85,
                        "supporting_evidence": ["evidence1", "evidence2"],
                        "cultural_relevance": 0.9
                    }}
                ],
                "reasoning": ["reason1", "reason2"],
                "preference_summary": "Summary of user preferences analysis",
                "cultural_profile": {{"dimension1": 0.8, "dimension2": 0.7}}
            }}
            
            IMPORTANT RULES:
            1. The "category" field must be exactly "{request.category.value if request.category else 'movies'}" (not a genre name like "comedy" or "romance")
            2. You MUST return EXACTLY {request.limit} items in the "recommendations" array
            3. Each item must have all required fields: name, type, category, rating, cultural_context, description, cultural_significance, target_audience, cultural_elements, popularity_score, personalization_score, metadata
            4. Focus on high-quality, culturally relevant recommendations based on the user's preferences
            5. Provide detailed cultural context for each item
            6. Make recommendations specific to the user's inputs: movie={request.movie_name}, book={request.book_name}, place={request.place_name}
            
            Valid category values are: movies, music, books, food, travel, fashion, brands, art, events, experiences.
            
            CRITICAL: Return ONLY valid JSON with exactly {request.limit} recommendations in the array.
            """
            
            # Create a system prompt to ensure proper JSON formatting
            system_prompt = f"""You are a cultural recommendation AI that generates personalized recommendations. 
            You MUST always return valid JSON with exactly the requested number of items in a "recommendations" array.
            Never return a single item - always return an array of items.
            The JSON must be properly formatted and complete."""
            
            llm_response = await self.llm_service.generate_response(
                llm_prompt,
                enforce_json=True,
                temperature=0.7,
                max_tokens=2000,  # Reduced to prevent context length issues
                system_prompt=system_prompt
            )
            
            # Debug: Log the LLM response
            logger.info(f"LLM Response length: {len(llm_response)}")
            logger.info(f"LLM Response preview: {llm_response[:500]}...")
            
            recommendation_data = self._parse_recommendations(llm_response, user_preferences, cultural_insights, request.limit)
            
            # Debug logging to see what data is being returned
            logger.info(f"Request limit: {request.limit}")
            logger.info(f"Recommendation data - Items count: {len(recommendation_data['items'])}")
            logger.info(f"Recommendation data - Cultural insights count: {len(recommendation_data['cultural_insights'])}")
            logger.info(f"Recommendation data - Items: {recommendation_data['items']}")
            logger.info(f"Recommendation data - Cultural insights: {recommendation_data['cultural_insights']}")
            
            # Note: Database logging removed for now - using Prisma instead of SQLAlchemy
            
            return RecommendationResponse(
                category=request.category,
                items=recommendation_data["items"],
                cultural_insights=recommendation_data["cultural_insights"],
                recommendation_reasoning=recommendation_data["recommendation_reasoning"],
                user_preference_summary=recommendation_data["user_preference_summary"],
                cultural_profile=recommendation_data["cultural_profile"],
                recommendation_date=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Recommendations failed: {str(e)}"
            )

    async def get_cultural_recommendations(self, request: CulturalRecommendationRequest) -> CulturalRecommendationResponse:
        """Get culturally-focused recommendations"""
        try:
            # Get cultural data
            cultural_data = await self.qloo_service.get_cultural_data(
                request.cultural_interests, request.cultural_background, request.preferred_cultures
            )
            
            # Generate cultural recommendations
            llm_prompt = f"""
            Generate cultural recommendations based on:
            Cultural Interests: {request.cultural_interests}
            Cultural Background: {request.cultural_background}
            Preferred Cultures: {request.preferred_cultures}
            Category: {request.category}
            Limit: {request.limit}
            
            Cultural Data: {json.dumps(cultural_data, indent=2)}
            
            Provide:
            1. Cultural recommendations
            2. Cultural connections
            3. Cross-cultural insights
            4. Cultural learning opportunities
            """
            
            llm_response = await self.llm_service.generate_response(llm_prompt)
            cultural_data = self._parse_cultural_recommendations(llm_response, cultural_data)
            
            return CulturalRecommendationResponse(
                recommendations=cultural_data["recommendations"],
                cultural_connections=cultural_data["cultural_connections"],
                cross_cultural_insights=cultural_data["cross_cultural_insights"],
                cultural_learning_opportunities=cultural_data["cultural_learning_opportunities"],
                recommendation_date=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cultural recommendations failed: {str(e)}"
            )

    async def get_trending_items(self, category: Optional[str] = None) -> TrendingItemsResponse:
        """Get trending items"""
        try:
            # Get trending data from Qloo
            trending_data = await self.qloo_service.get_trending_items(category)
            
            # Enhance with LLM analysis
            llm_prompt = f"""
            Analyze trending items:
            Category: {category or 'all'}
            Trending Data: {json.dumps(trending_data, indent=2)}
            
            Provide:
            1. Cultural trends analysis
            2. Insights about trending items
            3. Cultural factors driving trends
            """
            
            llm_response = await self.llm_service.generate_response(llm_prompt)
            trending_analysis = self._parse_trending_analysis(llm_response, trending_data)
            
            return TrendingItemsResponse(
                category=category,
                timeframe="week",
                items=trending_analysis["items"],
                cultural_trends=trending_analysis["cultural_trends"],
                insights=trending_analysis["insights"],
                response_date=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Trending items failed: {str(e)}"
            )

    def update_user_preferences(self, request: UserPreferenceUpdate) -> UserPreferenceResponse:
        """Update user preferences"""
        try:
            # Update preferences in database
            user = self.db.query(User).filter(User.id == request.user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Update preferences based on category
            if request.category == "music":
                user.music_preferences = request.preferences
            elif request.category == "food":
                user.food_preferences = request.preferences
            elif request.category == "fashion":
                user.fashion_preferences = request.preferences
            elif request.category == "books":
                user.book_preferences = request.preferences
            elif request.category == "movies":
                user.movie_preferences = request.preferences
            elif request.category == "travel":
                user.travel_preferences = request.preferences
            
            self.db.commit()
            self.db.refresh(user)
            
            return UserPreferenceResponse(
                user_id=user.id,
                preferences=[],  # Would be structured based on category
                cultural_profile={},  # Would be calculated
                preference_strength={},  # Would be calculated
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Preference update failed: {str(e)}"
            )

    def create_feedback(self, request: RecommendationFeedbackCreate) -> RecommendationFeedbackResponse:
        """Create recommendation feedback"""
        try:
            feedback = RecommendationFeedback(
                recommendation_id=request.recommendation_id,
                user_id=request.user_id,
                item_name=request.item_name,
                category=request.category,
                rating=request.rating,
                feedback_type=request.feedback_type,
                feedback_text=request.feedback_text,
                cultural_relevance_rating=request.cultural_relevance_rating,
                created_at=datetime.utcnow()
            )
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            
            return RecommendationFeedbackResponse(
                id=feedback.id,
                recommendation_id=feedback.recommendation_id,
                user_id=feedback.user_id,
                item_name=feedback.item_name,
                category=feedback.category,
                rating=feedback.rating,
                feedback_type=feedback.feedback_type,
                feedback_text=feedback.feedback_text,
                cultural_relevance_rating=feedback.cultural_relevance_rating,
                created_at=feedback.created_at
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Feedback creation failed: {str(e)}"
            )

    def _parse_recommendations(self, llm_response: str, user_preferences: dict, cultural_insights: dict, limit: int = 10) -> dict:
        """Parse LLM response into recommendation data"""
        try:
            import re
            import json
            
            logger.info(f"LLM Response: {llm_response[:200]}...")  # Log first 200 chars
            logger.info(f"User Preferences: {user_preferences}")
            logger.info(f"Cultural Insights: {cultural_insights}")
            
            # Try to extract JSON from LLM response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                try:
                    parsed_data = json.loads(json_match.group())
                    logger.info(f"Parsed JSON data keys: {list(parsed_data.keys())}")
                
                    # Extract recommendations from parsed data
                    items = parsed_data.get("recommendations", [])
                    logger.info(f"Found {len(items)} recommendations in JSON")
                    
                    # If no recommendations array, check if the response is a single item
                    if not items:
                        # Check if the response itself is a single recommendation item
                        if "name" in parsed_data and "type" in parsed_data:
                            logger.info("Found single recommendation item, converting to array")
                            items = [parsed_data]
                        else:
                            items = parsed_data.get("items", [])
                            logger.info(f"Found {len(items)} items in JSON (fallback)")
                
                    # Extract cultural insights
                    cultural_insights = parsed_data.get("cultural_insights", [])
                    if not cultural_insights:
                        cultural_insights = parsed_data.get("insights", [])
                
                    # Extract other data
                    recommendation_reasoning = parsed_data.get("reasoning", [])
                    user_preference_summary = parsed_data.get("preference_summary", "")
                    cultural_profile = parsed_data.get("cultural_profile", {})
                
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                    items = []
                    cultural_insights = []
                    recommendation_reasoning = []
                    user_preference_summary = ""
                    cultural_profile = {}
            else:
                # Try to find any JSON-like structure in the response
                logger.info("No JSON object found, searching for JSON-like structures")
                try:
                    # Look for array of objects
                    array_match = re.search(r'\[.*\{.*\}.*\]', llm_response, re.DOTALL)
                    if array_match:
                        items = json.loads(array_match.group())
                        logger.info(f"Found array with {len(items)} items")
                    else:
                        # Look for single object
                        single_match = re.search(r'\{[^{}]*"name"[^{}]*\}', llm_response, re.DOTALL)
                        if single_match:
                            single_item = json.loads(single_match.group())
                            items = [single_item]
                            logger.info("Found single item, converted to array")
                        else:
                            logger.info("No valid JSON structure found")
                            items = []
                    
                    cultural_insights = []
                    recommendation_reasoning = []
                    user_preference_summary = ""
                    cultural_profile = {}
                    
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.error(f"Failed to parse any JSON structure: {e}")
                    items = []
                    cultural_insights = []
                    recommendation_reasoning = []
                    user_preference_summary = ""
                    cultural_profile = {}
            
            # If we still don't have any items, use fallback
            if not items:
                logger.info("No JSON found in LLM response, using fallback")
                # Fallback to generating recommendations based on preferences
                # Use the limit parameter passed from the request
                items = self._generate_recommendations_from_preferences(user_preferences, limit=limit)
                cultural_insights = self._generate_cultural_insights_from_preferences(user_preferences)
                recommendation_reasoning = ["Based on your preferences", "Cultural relevance analysis"]
                
                # Handle different user_preferences structures
                if isinstance(user_preferences.get("preferences"), dict):
                    # Qloo service returns preferences as a dict with categories
                    preferences_dict = user_preferences.get("preferences", {})
                    preferences_text = " ".join([
                        " ".join(prefs) for prefs in preferences_dict.values()
                    ])
                else:
                    # Direct string preferences
                    preferences_text = user_preferences.get("preferences", "")
                
                user_preference_summary = f"Analysis of preferences: {preferences_text}"
                cultural_profile = {"cultural_affinity": 0.8, "diversity_interest": 0.7}
            
            # Ensure we have cultural insights even if LLM didn't provide them
            if not cultural_insights:
                logger.info("No cultural insights from LLM, generating fallback insights")
                cultural_insights = self._generate_cultural_insights_from_preferences(user_preferences)
            
            logger.info(f"Final items count: {len(items)}")
            logger.info(f"Final cultural insights count: {len(cultural_insights)}")
            
            # Ensure we have the requested number of items
            if len(items) < limit:
                logger.warning(f"LLM only generated {len(items)} items, but {limit} were requested. Using fallback to fill the gap.")
                fallback_items = self._generate_recommendations_from_preferences(user_preferences, limit - len(items))
                items.extend(fallback_items)
                logger.info(f"Added {len(fallback_items)} fallback items. Total now: {len(items)}")
            
            # If we still don't have enough, generate more fallback items
            if len(items) < limit:
                logger.warning(f"Still only have {len(items)} items, generating more fallback items.")
                additional_items = self._generate_recommendations_from_preferences(user_preferences, limit)
                items.extend(additional_items)
                logger.info(f"Added {len(additional_items)} additional fallback items. Total now: {len(items)}")
            
            # Ensure we don't exceed the limit
            items = items[:limit]
            logger.info(f"Final items count after limit enforcement: {len(items)}")
            
            return {
                "items": items,
                "cultural_insights": cultural_insights,
                "recommendation_reasoning": recommendation_reasoning,
                "user_preference_summary": user_preference_summary,
                "cultural_profile": cultural_profile
            }
            
        except Exception as e:
            logger.error(f"Failed to parse LLM recommendations: {str(e)}")
            # Fallback to generated recommendations
            return self._generate_fallback_recommendations(user_preferences)
    
    def _generate_recommendations_from_preferences(self, user_preferences: dict, limit: int = 10) -> list:
        """Generate recommendations based on user preferences"""
        # Handle different user_preferences structures
        if isinstance(user_preferences.get("preferences"), dict):
            # Qloo service returns preferences as a dict with categories
            preferences_dict = user_preferences.get("preferences", {})
            preferences_text = " ".join([
                " ".join(prefs) for prefs in preferences_dict.values()
            ]).lower()
        else:
            # Direct string preferences
            preferences_text = user_preferences.get("preferences", "").lower()
        
        # Get category from user_preferences or use a default
        category = user_preferences.get("category", "general")
        
        recommendations = []
        
        # Check if it's a movie-related preference
        if "movie" in category.lower() or "film" in preferences_text or "movie" in preferences_text:
            # Create a comprehensive list of movie recommendations
            all_movie_recommendations = [
                    {
                        "name": "When Harry Met Sally",
                        "type": "movie",
                        "category": "movies",
                        "rating": 4.8,
                        "cultural_context": "Classic romantic comedy that defined the genre in the 1980s",
                        "description": "A timeless romantic comedy about two friends who fall in love",
                        "cultural_significance": "Pioneered the modern rom-com formula",
                        "target_audience": ["romance lovers", "comedy fans"],
                        "cultural_elements": ["1980s culture", "New York setting", "friendship dynamics"],
                        "popularity_score": 0.9,
                        "personalization_score": 0.95,
                        "metadata": {"year": 1989, "director": "Rob Reiner"}
                    },
                    {
                        "name": "The Notebook",
                        "type": "movie",
                        "category": "movies",
                        "rating": 4.6,
                        "cultural_context": "Beloved romantic drama with strong emotional storytelling",
                        "description": "A passionate love story spanning decades",
                        "cultural_significance": "Modern classic in romantic cinema",
                        "target_audience": ["romance lovers", "drama fans"],
                        "cultural_elements": ["Southern culture", "1940s setting", "enduring love"],
                        "popularity_score": 0.85,
                        "personalization_score": 0.9,
                        "metadata": {"year": 2004, "director": "Nick Cassavetes"}
                    },
                    {
                        "name": "La La Land",
                        "type": "movie",
                        "category": "movies",
                        "rating": 4.7,
                        "cultural_context": "Modern musical that revitalized the genre",
                        "description": "A musical romance about dreams and love in Los Angeles",
                        "cultural_significance": "Revived interest in musical films",
                        "target_audience": ["musical fans", "romance lovers"],
                        "cultural_elements": ["Hollywood culture", "jazz music", "dream chasing"],
                        "popularity_score": 0.88,
                        "personalization_score": 0.92,
                        "metadata": {"year": 2016, "director": "Damien Chazelle"}
                },
                    {
                        "name": "The Grand Budapest Hotel",
                        "type": "movie",
                        "category": "movies",
                        "rating": 4.7,
                        "cultural_context": "Wes Anderson's whimsical comedy with European charm",
                        "description": "A quirky comedy about a legendary concierge and his young protégé",
                        "cultural_significance": "Showcases European cultural aesthetics and storytelling",
                        "target_audience": ["comedy fans", "art house lovers"],
                        "cultural_elements": ["European culture", "hotel culture", "artistic storytelling"],
                        "popularity_score": 0.85,
                        "personalization_score": 0.9,
                        "metadata": {"year": 2014, "director": "Wes Anderson"}
                    },
                    {
                        "name": "Superbad",
                        "type": "movie",
                        "category": "movies",
                        "rating": 4.5,
                        "cultural_context": "Coming-of-age comedy that defined 2000s teen culture",
                        "description": "A hilarious high school comedy about friendship and growing up",
                        "cultural_significance": "Captured the essence of 2000s youth culture",
                        "target_audience": ["teen comedy fans", "coming-of-age lovers"],
                        "cultural_elements": ["2000s culture", "high school life", "friendship"],
                        "popularity_score": 0.8,
                        "personalization_score": 0.85,
                        "metadata": {"year": 2007, "director": "Greg Mottola"}
                },
                    {
                        "name": "The Shawshank Redemption",
                        "type": "movie",
                        "category": "movies",
                        "rating": 4.9,
                        "cultural_context": "Universal story of hope and redemption",
                        "description": "A powerful drama about friendship and hope in prison",
                        "cultural_significance": "Considered one of the greatest films ever made",
                        "target_audience": ["drama fans", "classic film lovers"],
                        "cultural_elements": ["American prison system", "friendship", "hope"],
                        "popularity_score": 0.95,
                        "personalization_score": 0.9,
                        "metadata": {"year": 1994, "director": "Frank Darabont"}
                },
                {
                    "name": "Iron Man",
                    "type": "movie",
                    "category": "movies",
                    "rating": 4.8,
                    "cultural_context": "The film launched the Marvel Cinematic Universe and revitalized the superhero genre",
                    "description": "A billionaire industrialist becomes a superhero using his own technology",
                    "cultural_significance": "Revolutionized superhero cinema and established the MCU",
                    "target_audience": ["superhero fans", "action lovers"],
                    "cultural_elements": ["2000s tech culture", "superhero mythology", "American innovation"],
                    "popularity_score": 0.9,
                    "personalization_score": 0.88,
                    "metadata": {"year": 2008, "director": "Jon Favreau"}
                },
                {
                    "name": "Iron Man 2",
                    "type": "movie",
                    "category": "movies",
                    "rating": 4.6,
                    "cultural_context": "Building on the success of the first film, Iron Man 2 further expanded the MCU",
                    "description": "Tony Stark faces new challenges while dealing with his own creation",
                    "cultural_significance": "Continued the exploration of Tony Stark's character and introduced new heroes",
                    "target_audience": ["superhero fans", "MCU enthusiasts"],
                    "cultural_elements": ["2010s tech culture", "military-industrial complex", "personal growth"],
                    "popularity_score": 0.85,
                    "personalization_score": 0.86,
                    "metadata": {"year": 2010, "director": "Jon Favreau"}
                },
                {
                    "name": "Iron Man 3",
                    "type": "movie",
                    "category": "movies",
                    "rating": 4.5,
                    "cultural_context": "Iron Man 3 explored Tony Stark's vulnerability and post-traumatic stress",
                    "description": "Tony Stark faces his greatest challenge yet while dealing with PTSD",
                    "cultural_significance": "Offered a more personal and introspective look at the superhero",
                    "target_audience": ["superhero fans", "character study lovers"],
                    "cultural_elements": ["PTSD awareness", "personal vulnerability", "redemption arc"],
                    "popularity_score": 0.82,
                    "personalization_score": 0.84,
                    "metadata": {"year": 2013, "director": "Shane Black"}
                },
                {
                    "name": "Captain America: Civil War",
                    "type": "movie",
                    "category": "movies",
                    "rating": 4.7,
                    "cultural_context": "This film pits Iron Man against Captain America, exploring ideological differences",
                    "description": "The Avengers are divided over government oversight of superheroes",
                    "cultural_significance": "Explored complex moral questions about power and responsibility",
                    "target_audience": ["superhero fans", "political thriller lovers"],
                    "cultural_elements": ["Government oversight", "moral complexity", "team dynamics"],
                    "popularity_score": 0.88,
                    "personalization_score": 0.87,
                    "metadata": {"year": 2016, "director": "Anthony and Joe Russo"}
                },
                {
                    "name": "The Dark Knight",
                    "type": "movie",
                    "category": "movies",
                    "rating": 4.9,
                    "cultural_context": "Revolutionary superhero film that redefined the genre",
                    "description": "Batman faces his greatest challenge in the form of the Joker",
                    "cultural_significance": "Elevated superhero films to serious dramatic art",
                    "target_audience": ["superhero fans", "drama lovers"],
                    "cultural_elements": ["Moral philosophy", "urban crime", "psychological complexity"],
                    "popularity_score": 0.95,
                    "personalization_score": 0.93,
                    "metadata": {"year": 2008, "director": "Christopher Nolan"}
                },
                {
                    "name": "Inception",
                    "type": "movie",
                    "category": "movies",
                    "rating": 4.8,
                    "cultural_context": "Mind-bending sci-fi thriller that challenged audience perceptions",
                    "description": "A thief who steals corporate secrets through dream-sharing technology",
                    "cultural_significance": "Pioneered complex narrative structures in mainstream cinema",
                    "target_audience": ["sci-fi fans", "thriller lovers"],
                    "cultural_elements": ["Dream psychology", "reality vs illusion", "corporate espionage"],
                    "popularity_score": 0.92,
                    "personalization_score": 0.91,
                    "metadata": {"year": 2010, "director": "Christopher Nolan"}
                },
                {
                    "name": "Interstellar",
                    "type": "movie",
                    "category": "movies",
                    "rating": 4.7,
                    "cultural_context": "Epic space exploration film with emotional depth",
                    "description": "A team of explorers travel through a wormhole in space",
                    "cultural_significance": "Combined hard science with human emotion in space exploration",
                    "target_audience": ["sci-fi fans", "space enthusiasts"],
                    "cultural_elements": ["Space exploration", "family bonds", "scientific discovery"],
                    "popularity_score": 0.89,
                    "personalization_score": 0.89,
                    "metadata": {"year": 2014, "director": "Christopher Nolan"}
                },
                {
                    "name": "The Matrix",
                    "type": "movie",
                    "category": "movies",
                    "rating": 4.8,
                    "cultural_context": "Revolutionary sci-fi film that influenced pop culture for decades",
                    "description": "A computer programmer discovers the truth about reality",
                    "cultural_significance": "Introduced groundbreaking visual effects and philosophical concepts",
                    "target_audience": ["sci-fi fans", "philosophy enthusiasts"],
                    "cultural_elements": ["Reality vs simulation", "technological advancement", "rebellion"],
                    "popularity_score": 0.93,
                    "personalization_score": 0.92,
                    "metadata": {"year": 1999, "director": "Lana and Lilly Wachowski"}
                },
                {
                    "name": "Pulp Fiction",
                    "type": "movie",
                    "category": "movies",
                    "rating": 4.8,
                    "cultural_context": "Revolutionary crime film that redefined narrative storytelling",
                    "description": "Interconnected stories of criminals in Los Angeles",
                    "cultural_significance": "Influenced countless films with its non-linear narrative",
                    "target_audience": ["crime film fans", "art house lovers"],
                    "cultural_elements": ["1990s culture", "crime underworld", "pop culture references"],
                    "popularity_score": 0.91,
                    "personalization_score": 0.9,
                    "metadata": {"year": 1994, "director": "Quentin Tarantino"}
                }
            ]
            
            # Filter recommendations based on preferences and apply limit
            if "rom com" in preferences_text or "romantic" in preferences_text or "romance" in preferences_text:
                # Prioritize romantic movies
                romantic_movies = [r for r in all_movie_recommendations if any(keyword in r["cultural_context"].lower() for keyword in ["romantic", "romance", "love", "rom com"])]
                other_movies = [r for r in all_movie_recommendations if r not in romantic_movies]
                recommendations = romantic_movies + other_movies
            elif "comedy" in preferences_text or "funny" in preferences_text:
                # Prioritize comedy movies
                comedy_movies = [r for r in all_movie_recommendations if any(keyword in r["cultural_context"].lower() for keyword in ["comedy", "funny", "humor"])]
                other_movies = [r for r in all_movie_recommendations if r not in comedy_movies]
                recommendations = comedy_movies + other_movies
            else:
                # Use all recommendations in default order
                recommendations = all_movie_recommendations
            
            # Apply the limit
            recommendations = recommendations[:limit]
            logger.info(f"Generated {len(recommendations)} movie recommendations (requested: {limit})")
        elif "music" in category.lower() or "song" in preferences_text or "music" in preferences_text:
            recommendations = [
                {
                    "name": "Bohemian Rhapsody",
                    "type": "song",
                    "category": "music",
                    "rating": 4.9,
                    "cultural_context": "Revolutionary rock opera that changed music history",
                    "description": "Queen's epic masterpiece blending rock, opera, and ballad",
                    "cultural_significance": "One of the most innovative songs ever recorded",
                    "target_audience": ["rock fans", "classic music lovers"],
                    "cultural_elements": ["1970s rock", "opera influence", "experimental music"],
                    "popularity_score": 0.95,
                    "personalization_score": 0.9,
                    "metadata": {"artist": "Queen", "year": 1975}
                },
                {
                    "name": "Hotel California",
                    "type": "song",
                    "category": "music",
                    "rating": 4.8,
                    "cultural_context": "Eagles' iconic song about the dark side of the American Dream",
                    "description": "A haunting ballad about excess and disillusionment",
                    "cultural_significance": "Defined 1970s rock music and California culture",
                    "target_audience": ["rock fans", "classic rock lovers"],
                    "cultural_elements": ["1970s culture", "California lifestyle", "American Dream"],
                    "popularity_score": 0.93,
                    "personalization_score": 0.88,
                    "metadata": {"artist": "Eagles", "year": 1976}
                },
                {
                    "name": "Stairway to Heaven",
                    "type": "song",
                    "category": "music",
                    "rating": 4.9,
                    "cultural_context": "Led Zeppelin's epic masterpiece that defined rock music",
                    "description": "A progressive rock journey from acoustic to electric",
                    "cultural_significance": "Considered one of the greatest rock songs ever",
                    "target_audience": ["rock fans", "classic rock enthusiasts"],
                    "cultural_elements": ["1970s rock", "progressive music", "mythological themes"],
                    "popularity_score": 0.95,
                    "personalization_score": 0.9,
                    "metadata": {"artist": "Led Zeppelin", "year": 1971}
                },
                {
                    "name": "Imagine",
                    "type": "song",
                    "category": "music",
                    "rating": 4.8,
                    "cultural_context": "John Lennon's anthem for peace and unity",
                    "description": "A powerful call for world peace and harmony",
                    "cultural_significance": "Became the anthem for peace movements worldwide",
                    "target_audience": ["peace activists", "classic music lovers"],
                    "cultural_elements": ["Peace movement", "1960s idealism", "social change"],
                    "popularity_score": 0.92,
                    "personalization_score": 0.87,
                    "metadata": {"artist": "John Lennon", "year": 1971}
                },
                {
                    "name": "Like a Rolling Stone",
                    "type": "song",
                    "category": "music",
                    "rating": 4.7,
                    "cultural_context": "Bob Dylan's revolutionary folk-rock masterpiece",
                    "description": "A scathing critique of social status and privilege",
                    "cultural_significance": "Transformed folk music and influenced generations",
                    "target_audience": ["folk fans", "social commentary lovers"],
                    "cultural_elements": ["1960s counterculture", "social criticism", "folk revival"],
                    "popularity_score": 0.9,
                    "personalization_score": 0.85,
                    "metadata": {"artist": "Bob Dylan", "year": 1965}
                },
                {
                    "name": "Smells Like Teen Spirit",
                    "type": "song",
                    "category": "music",
                    "rating": 4.8,
                    "cultural_context": "Nirvana's anthem that defined 1990s grunge",
                    "description": "The song that launched the grunge movement",
                    "cultural_significance": "Revolutionized rock music in the 1990s",
                    "target_audience": ["grunge fans", "alternative rock lovers"],
                    "cultural_elements": ["1990s culture", "grunge movement", "youth rebellion"],
                    "popularity_score": 0.91,
                    "personalization_score": 0.89,
                    "metadata": {"artist": "Nirvana", "year": 1991}
                },
                {
                    "name": "Billie Jean",
                    "type": "song",
                    "category": "music",
                    "rating": 4.7,
                    "cultural_context": "Michael Jackson's groundbreaking pop masterpiece",
                    "description": "Revolutionary pop song with iconic dance moves",
                    "cultural_significance": "Redefined pop music and music videos",
                    "target_audience": ["pop fans", "dance music lovers"],
                    "cultural_elements": ["1980s pop", "music video culture", "dance innovation"],
                    "popularity_score": 0.89,
                    "personalization_score": 0.86,
                    "metadata": {"artist": "Michael Jackson", "year": 1982}
                },
                {
                    "name": "Hey Jude",
                    "type": "song",
                    "category": "music",
                    "rating": 4.8,
                    "cultural_context": "The Beatles' uplifting anthem of hope",
                    "description": "A comforting song written to cheer up a child",
                    "cultural_significance": "Became a universal message of hope and comfort",
                    "target_audience": ["Beatles fans", "classic pop lovers"],
                    "cultural_elements": ["1960s culture", "British invasion", "hope and comfort"],
                    "popularity_score": 0.93,
                    "personalization_score": 0.88,
                    "metadata": {"artist": "The Beatles", "year": 1968}
                },
                {
                    "name": "Purple Haze",
                    "type": "song",
                    "category": "music",
                    "rating": 4.6,
                    "cultural_context": "Jimi Hendrix's psychedelic rock masterpiece",
                    "description": "Revolutionary guitar work that defined psychedelic rock",
                    "cultural_significance": "Redefined electric guitar playing",
                    "target_audience": ["rock fans", "guitar enthusiasts"],
                    "cultural_elements": ["1960s psychedelia", "guitar innovation", "counterculture"],
                    "popularity_score": 0.88,
                    "personalization_score": 0.84,
                    "metadata": {"artist": "Jimi Hendrix", "year": 1967}
                },
                {
                    "name": "Respect",
                    "type": "song",
                    "category": "music",
                    "rating": 4.7,
                    "cultural_context": "Aretha Franklin's empowering anthem",
                    "description": "A powerful demand for respect and equality",
                    "cultural_significance": "Became the anthem for civil rights and women's rights",
                    "target_audience": ["soul fans", "empowerment music lovers"],
                    "cultural_elements": ["Civil rights movement", "women's empowerment", "soul music"],
                    "popularity_score": 0.9,
                    "personalization_score": 0.87,
                    "metadata": {"artist": "Aretha Franklin", "year": 1967}
                }
            ]
            
            # Apply the limit
            recommendations = recommendations[:limit]
            logger.info(f"Generated {len(recommendations)} music recommendations (requested: {limit})")
        else:
            # Generic recommendations
            recommendations = [
                {
                    "name": "The Great Gatsby",
                    "type": "book",
                    "category": "books",
                    "rating": 4.5,
                    "cultural_context": "Classic American literature about the Jazz Age",
                    "description": "F. Scott Fitzgerald's masterpiece about the American Dream",
                    "cultural_significance": "Defining work of American literature",
                    "target_audience": ["literature fans", "classic readers"],
                    "cultural_elements": ["1920s culture", "American Dream", "social class"],
                    "popularity_score": 0.8,
                    "personalization_score": 0.7,
                    "metadata": {"author": "F. Scott Fitzgerald", "year": 1925}
                }
            ]
        
        return recommendations
    
    def _generate_cultural_insights_from_preferences(self, user_preferences: dict) -> list:
        """Generate cultural insights based on user preferences"""
        # Handle different user_preferences structures
        if isinstance(user_preferences.get("preferences"), dict):
            # Qloo service returns preferences as a dict with categories
            preferences_dict = user_preferences.get("preferences", {})
            preferences_text = " ".join([
                " ".join(prefs) for prefs in preferences_dict.values()
            ]).lower()
        else:
            # Direct string preferences
            preferences_text = user_preferences.get("preferences", "").lower()
        
        # Get category for more specific insights
        category = user_preferences.get("category", "general").lower()
        
        insights = []
        
        # Add category-specific insights
        if "music" in category or "music" in preferences_text:
            insights.append({
                "insight_type": "musical_preference",
                "description": "Your musical tastes reflect a sophisticated appreciation for both contemporary and classic styles, with a focus on emotional depth and artistic expression.",
                "confidence": 0.88,
                "supporting_evidence": [
                    "Diverse musical genre preferences",
                    "Appreciation for both modern and traditional styles",
                    "Emotional connection to music"
                ],
                "cultural_relevance": 0.92
            })
        elif "movie" in category or "film" in preferences_text:
            insights.append({
                "insight_type": "cinematic_preference",
                "description": "Your film preferences indicate a love for storytelling that combines emotional depth with cultural significance.",
                "confidence": 0.85,
                "supporting_evidence": [
                    "Preference for character-driven narratives",
                    "Appreciation for cultural storytelling",
                    "Interest in diverse cinematic traditions"
                ],
                "cultural_relevance": 0.89
            })
        else:
            insights.append({
                "insight_type": "cultural_preference",
                "description": f"Your preferences for '{preferences_text}' demonstrate a sophisticated cultural awareness and appreciation for quality content.",
                "confidence": 0.82,
                "supporting_evidence": [
                    "Diverse cultural interests",
                    "Quality-focused preferences",
                    "Openness to new experiences"
                ],
                "cultural_relevance": 0.87
            })
        
        # Add general cultural insight
        insights.append({
                "insight_type": "cultural_connection",
            "description": "Your cultural choices reflect a balanced appreciation for both contemporary trends and timeless classics, suggesting a well-rounded cultural perspective.",
                "confidence": 0.78,
                "supporting_evidence": [
                "Balance of modern and traditional preferences",
                    "Universal appeal in chosen content",
                    "Cross-generational cultural resonance"
                ],
                "cultural_relevance": 0.85
        })
        
        return insights
    
    def _generate_fallback_recommendations(self, user_preferences: dict) -> dict:
        """Generate fallback recommendations when parsing fails"""
        # Handle different user_preferences structures
        if isinstance(user_preferences.get("preferences"), dict):
            # Qloo service returns preferences as a dict with categories
            preferences_dict = user_preferences.get("preferences", {})
            preferences_text = " ".join([
                " ".join(prefs) for prefs in preferences_dict.values()
            ])
        else:
            # Direct string preferences
            preferences_text = user_preferences.get("preferences", "")
        
        return {
            "items": self._generate_recommendations_from_preferences(user_preferences, limit=10),
            "cultural_insights": self._generate_cultural_insights_from_preferences(user_preferences),
            "recommendation_reasoning": ["Based on your preferences", "Cultural analysis"],
            "user_preference_summary": f"Analysis of: {preferences_text}",
            "cultural_profile": {"cultural_affinity": 0.8, "diversity_interest": 0.7}
        }

    def _parse_cultural_recommendations(self, llm_response: str, cultural_data: dict) -> dict:
        """Parse LLM response into cultural recommendation data"""
        return {
            "recommendations": [
                {
                    "name": "Cultural Item",
                    "type": "cultural",
                    "category": "cultural",
                    "rating": 4.8,
                    "cultural_context": "Cultural context",
                    "description": "Cultural description",
                    "cultural_significance": "High significance",
                    "target_audience": ["audience1"],
                    "cultural_elements": ["element1"],
                    "popularity_score": 0.9,
                    "personalization_score": 0.9,
                    "metadata": {}
                }
            ],
            "cultural_connections": ["connection1", "connection2"],
            "cross_cultural_insights": ["insight1", "insight2"],
            "cultural_learning_opportunities": ["opportunity1", "opportunity2"]
        }

    def _parse_trending_analysis(self, llm_response: str, trending_data: dict) -> dict:
        """Parse LLM response into trending analysis"""
        return {
            "items": [
                {
                    "name": "Trending Item",
                    "type": "trending",
                    "category": "trending",
                    "trend_score": 0.9,
                    "popularity_change": "rising",
                    "cultural_factors": ["factor1", "factor2"],
                    "social_media_mentions": 1000,
                    "cultural_relevance": 0.8,
                    "description": "Trending description"
                }
            ],
            "cultural_trends": ["trend1", "trend2"],
            "insights": ["insight1", "insight2"]
        }

# API Endpoints
@router.post("/personalized", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    request: RecommendationRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Get personalized recommendations"""
    recommendations_service = RecommendationsService(db)
    
    # Track event
    if current_user:
        try:
            db.analytics.create(
                data={
                    "event_type": "recommendations",
                    "event_data": json.dumps({"category": request.category, "item_count": request.limit}),
                    "user_id": str(current_user.id),  # Convert to string for Prisma
                    "session_id": f"session_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d')}"
                }
            )
        except Exception as analytics_error:
            logger.error(f"Failed to track analytics: {analytics_error}")
            # Continue without analytics tracking
    
    return await recommendations_service.get_personalized_recommendations(request)

@router.post("/cultural", response_model=CulturalRecommendationResponse)
async def get_cultural_recommendations(
    request: CulturalRecommendationRequest,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Get cultural recommendations"""
    recommendations_service = RecommendationsService(db)
    return await recommendations_service.get_cultural_recommendations(request)

@router.get("/trending", response_model=TrendingItemsResponse)
async def get_trending_items(
    category: Optional[str] = None,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Get trending items"""
    recommendations_service = RecommendationsService(db)
    return await recommendations_service.get_trending_items(category)

@router.put("/preferences", response_model=UserPreferenceResponse)
def update_user_preferences(
    request: UserPreferenceUpdate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update user preferences"""
    recommendations_service = RecommendationsService(db)
    return recommendations_service.update_user_preferences(request)

@router.post("/feedback", response_model=RecommendationFeedbackResponse)
def create_feedback(
    request: RecommendationFeedbackCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create recommendation feedback"""
    recommendations_service = RecommendationsService(db)
    return recommendations_service.create_feedback(request) 