from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from datetime import datetime
from typing import List, Optional
import json
import logging

logger = logging.getLogger(__name__)

from ..database import get_db
# Removed SQLAlchemy User model import - using Prisma now
# Removed SQLAlchemy model imports - using Prisma now
from ..schemas.travel import (
    TravelPlanningRequest, TravelPlanningResponse, DestinationRecommendationRequest,
    DestinationRecommendationResponse, CulturalEventsRequest, CulturalEventsResponse,
    LocalGuidesRequest, LocalGuidesResponse, TravelBudgetRequest, TravelBudgetResponse,
    TravelSafetyRequest, TravelSafetyResponse, TravelReviewCreate, TravelReviewResponse
)
from ..config import settings
from ..dependencies import get_current_user, get_optional_user, get_optional_user_no_auth
from ..services.llm_service import LLMService
from ..services.qloo_service import QlooService
from ..shared.errors import ValidationError, ExternalServiceError
from ..shared.response_formatter import format_travel_response

router = APIRouter()

class TravelService:
    def __init__(self, db):
        self.db = db
        self.llm_service = LLMService()
        self.qloo_service = QlooService()

    async def plan_travel(self, request: TravelPlanningRequest, user_id: Optional[int] = None) -> TravelPlanningResponse:
        """Plan culturally-aware travel itinerary"""
        try:
            # Get cultural insights for destination
            logger.info(f"Fetching Qloo data for destination: {request.destination}")
            cultural_data = await self.qloo_service.get_destination_cultural_insights(request.destination)
            travel_data = await self.qloo_service.get_travel_recommendations(
                request.destination, request.travel_style, request.cultural_interests
            )
            logger.info(f"Qloo cultural data keys: {list(cultural_data.keys()) if isinstance(cultural_data, dict) else 'Not a dict'}")
            logger.info(f"Qloo travel data keys: {list(travel_data.keys()) if isinstance(travel_data, dict) else 'Not a dict'}")
            
            # Generate itinerary with LLM
            try:
                # Truncate large data to prevent token limit issues
                cultural_summary = self._summarize_cultural_data(cultural_data)
                travel_summary = self._summarize_travel_data(travel_data)
                
                llm_prompt = f"""
You are a culturally intelligent travel planner.

Create a personalized **{request.duration or '1 week'}** itinerary for a trip to **{request.destination}**. The traveler prefers:

**Travel Style**: {request.travel_style or 'cultural'}
**Cultural Interests**: {', '.join(request.cultural_interests) if request.cultural_interests else 'cultural exploration'}
**Budget Level**: {request.budget_level or 'moderate'}
**Group Size**: {request.group_size} people

**Cultural Insights from Qloo API:**
{cultural_summary}

**Travel Recommendations from Qloo API:**
{travel_summary}

**Instructions:**
Create a rich, engaging, and culturally-authentic travel itinerary. For each day:

- Suggest **morning**, **afternoon**, and **evening** activities
- Use specific details from the Qloo data when available
- Include **cultural context** and **local insights**
- Mention **cost estimates** and **budget considerations**
- Suggest **ideal times** for different activities
- Add **practical tips** and **cultural etiquette**

**Make it fun, detailed, and personalized!** Focus on creating an experience that helps travelers truly connect with the local culture of {request.destination}.

End with a short, stylish **trip summary** that captures the essence of the cultural journey.
"""
                
                # Use natural language response like other repositories (qloo-llm-hackathon-2025 style)
                system_prompt = """You are a culturally intelligent travel planner that creates rich, fun, and personalized itineraries. Focus on creating engaging, detailed descriptions that help travelers truly experience the local culture."""
                
                logger.info("Calling LLM service...")
                llm_response = await self.llm_service.generate_response(
                    llm_prompt, 
                    enforce_json=False,  # Use natural language like other repos
                    system_prompt=system_prompt,
                    temperature=0.8  # More creative and engaging responses
                )
                logger.info(f"LLM response received, length: {len(llm_response)}")
                
                # Create rich itinerary data with natural language response
                itinerary_data = self._create_rich_itinerary_response(llm_response, request, cultural_data, travel_data)
                logger.info(f"Created itinerary with {len(itinerary_data.get('qloo_places', []))} Qloo places and LLM summary length: {len(itinerary_data.get('llm_summary', ''))}")
            except Exception as llm_error:
                logger.error(f"LLM service failed: {llm_error}")
                # Use fallback itinerary data
                itinerary_data = self._parse_itinerary_data("", cultural_data, travel_data, request.destination)
                logger.warning("Using fallback itinerary data due to LLM failure")
            
            # Ensure itinerary_data is a proper dict for JSON storage
            if not isinstance(itinerary_data, dict):
                itinerary_data = {"raw_data": str(itinerary_data)}
            
            # Convert to proper JSON format for Prisma
            try:
                # Test if the data can be serialized to JSON
                json.dumps(itinerary_data)
            except (TypeError, ValueError):
                # If not, convert to a safe format
                itinerary_data = {"data": str(itinerary_data)}
            
            # Save trip to database (only if user_id is provided)
            trip = None
            if user_id:
                try:
                    trip = self.db.trip.create(
                        data={
                            "title": f"Trip to {request.destination}",
                            "description": f"Cultural travel to {request.destination} - {request.travel_style or 'cultural'} style",
                            "destination": request.destination,
                            "cultural_focus": request.cultural_interests or [],
                            "itinerary": itinerary_data,
                            "user": {
                                "connect": {
                                    "id": str(user_id)  # Convert to string for Prisma
                                }
                            }
                        }
                    )
                except Exception as db_error:
                    logger.error(f"Failed to save trip to database: {db_error}")
                    # Continue without saving to database
            
            # Format response to match frontend expectations
            formatted_itinerary = []
            for day in itinerary_data.get("itinerary", []):
                # Use the correct field names from the itinerary data
                day_number = day.get("day", day.get("day_number", 1))
                activity_name = day.get("activity", f"Day {day_number}: Cultural Experience")
                cultural_context = day.get("cultural_context", "Discover the rich cultural heritage")
                
                formatted_day = {
                    "day": day_number,
                    "activity": activity_name,
                    "cultural_context": cultural_context
                }
                formatted_itinerary.append(formatted_day)
            
            # Clean up budget estimate - remove enum values and format properly
            budget_estimate = itinerary_data.get("budget_estimate", "$1000-2000")
            if "BudgetLevelEnum" in str(budget_estimate):
                # Extract the budget level and format it properly
                if "moderate" in str(budget_estimate).lower():
                    budget_estimate = "$1500-3000"
                elif "budget" in str(budget_estimate).lower():
                    budget_estimate = "$800-1500"
                elif "luxury" in str(budget_estimate).lower():
                    budget_estimate = "$3000-6000"
                else:
                    budget_estimate = "$1500-3000"
            
            # Clean up cultural insights - remove markdown and truncate properly
            cultural_insights_text = ""
            raw_insights = itinerary_data.get("cultural_insights", "")
            
            if isinstance(raw_insights, list):
                cultural_insights_text = "\n".join([
                    f"• {insight.get('aspect', 'Cultural Aspect')}: {insight.get('description', '')}"
                    for insight in raw_insights
                ])
            else:
                # Clean up the text by removing markdown and truncating
                import re
                # Remove markdown formatting
                cleaned_text = re.sub(r'[#*`]+', '', str(raw_insights))
                # Remove extra whitespace
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                # Truncate to reasonable length
                if len(cleaned_text) > 300:
                    cleaned_text = cleaned_text[:300] + "..."
                cultural_insights_text = cleaned_text or f"Discover the rich cultural heritage of {request.destination}"
            
            return TravelPlanningResponse(
                destination=request.destination,
                duration=request.duration or "1 week",
                travel_style=request.travel_style or "cultural",
                budget_estimate=budget_estimate,
                cultural_insights=cultural_insights_text,
                itinerary=formatted_itinerary,
                local_experiences=itinerary_data.get("local_experiences", []),
                accommodation_recommendations=itinerary_data.get("accommodation_recommendations", []),
                cultural_activities=itinerary_data.get("cultural_activities", []),
                practical_information=itinerary_data.get("practical_information", {}),
                safety_considerations=itinerary_data.get("safety_considerations", []),
                cultural_etiquette=itinerary_data.get("cultural_etiquette", []),
                planning_date=datetime.utcnow(),
                llm_summary=itinerary_data.get("llm_summary"),
                qloo_places=itinerary_data.get("qloo_places")
            )
            
        except ValidationError:
            raise
        except ExternalServiceError:
            raise
        except Exception as e:
            raise ExternalServiceError(
                service="Travel Planning",
                message="Failed to plan travel itinerary",
                original_error=str(e)
            )

    async def get_destination_recommendations(self, request: DestinationRecommendationRequest) -> DestinationRecommendationResponse:
        """Get destination recommendations based on interests"""
        try:
            # Get cultural preferences
            cultural_preferences = await self.qloo_service.get_user_cultural_preferences(request.user_id)
            
            # Generate recommendations with LLM
            llm_prompt = f"""
            Recommend travel destinations based on:
            Interests: {request.interests}
            Travel Style: {request.travel_style}
            Budget Level: {request.budget_level}
            Duration Range: {request.duration_range}
            Preferred Climate: {request.preferred_climate}
            Cultural Preferences: {request.cultural_preferences}
            
            Cultural Preferences: {cultural_preferences}
            
            Provide:
            1. Destination recommendations with reasons
            2. Cultural highlights for each destination
            3. Best time to visit
            4. Cultural events and festivals
            """
            
            llm_response = await self.llm_service.generate_response(llm_prompt)
            recommendation_data = self._parse_destination_recommendations(llm_response, cultural_preferences)
            
            return DestinationRecommendationResponse(
                recommendations=recommendation_data["recommendations"],
                insights=recommendation_data["insights"],
                cultural_themes=recommendation_data["cultural_themes"],
                recommendation_date=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Destination recommendations failed: {str(e)}"
            )

    async def get_cultural_events(self, request: CulturalEventsRequest) -> CulturalEventsResponse:
        """Get cultural events for a destination"""
        try:
            # Get events data
            events_data = await self.qloo_service.get_cultural_events(
                request.destination, request.start_date, request.end_date
            )
            
            # Enhance with LLM analysis
            llm_prompt = f"""
            Analyze cultural events for: {request.destination}
            Date Range: {request.start_date} to {request.end_date}
            Event Types: {request.event_types}
            
            Events Data: {json.dumps(events_data, indent=2)}
            
            Provide:
            1. Cultural significance of events
            2. Planning tips
            3. Cultural calendar insights
            """
            
            llm_response = await self.llm_service.generate_response(llm_prompt)
            events_analysis = self._parse_events_analysis(llm_response, events_data)
            
            return CulturalEventsResponse(
                destination=request.destination,
                events=events_analysis["events"],
                cultural_calendar=events_analysis["cultural_calendar"],
                insights=events_analysis["insights"],
                planning_tips=events_analysis["planning_tips"],
                response_date=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cultural events failed: {str(e)}"
            )

    async def get_local_guides(self, request: LocalGuidesRequest) -> LocalGuidesResponse:
        """Get local guides for a destination"""
        try:
            # Get guides data
            guides_data = await self.qloo_service.get_local_guides(
                request.destination, request.specialization, request.languages
            )
            
            # Enhance with LLM analysis
            llm_prompt = f"""
            Analyze local guides for: {request.destination}
            Specialization: {request.specialization}
            Languages: {request.languages}
            
            Guides Data: {json.dumps(guides_data, indent=2)}
            
            Provide:
            1. Booking tips
            2. Cultural insights
            3. Guide selection recommendations
            """
            
            llm_response = await self.llm_service.generate_response(llm_prompt)
            guides_analysis = self._parse_guides_analysis(llm_response, guides_data)
            
            return LocalGuidesResponse(
                destination=request.destination,
                guides=guides_analysis["guides"],
                insights=guides_analysis["insights"],
                booking_tips=guides_analysis["booking_tips"],
                response_date=datetime.utcnow()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Local guides failed: {str(e)}"
            )

    def _parse_itinerary_data(self, llm_response: str, cultural_data: dict, travel_data: dict, request_destination: str = "Unknown") -> dict:
        """Parse LLM response into itinerary data - handles natural language like other repositories"""
        try:
            # Use the request destination as the primary source
            destination = request_destination
            
            # Create a rich itinerary based on the natural language response and Qloo data
            # Create a mock request object for the rich itinerary method
            class MockRequest:
                def __init__(self, destination, travel_style, duration, group_size, budget_level, cultural_interests):
                    self.destination = destination
                    self.travel_style = travel_style
                    self.duration = duration
                    self.group_size = group_size
                    self.budget_level = budget_level
                    self.cultural_interests = cultural_interests
            
            mock_request = MockRequest(destination, "cultural", "1 week", 1, "moderate", [])
            return self._create_rich_itinerary_response(llm_response, mock_request, cultural_data, travel_data)
            
        except Exception as e:
            logger.error(f"Error parsing itinerary data: {e}")
            return self._create_enhanced_fallback_itinerary(destination, cultural_data, travel_data)
    
    def _create_rich_itinerary_response(self, llm_response: str, request, cultural_data: dict, travel_data: dict) -> dict:
        """Create rich itinerary response like qloo-llm-hackathon-2025 and qloo-backend-AI"""
        destination = request.destination
        
        # Extract actual places from Qloo data
        qloo_places = []
        logger.info(f"Cultural data keys: {list(cultural_data.keys()) if isinstance(cultural_data, dict) else 'Not a dict'}")
        logger.info(f"Travel data keys: {list(travel_data.keys()) if isinstance(travel_data, dict) else 'Not a dict'}")
        
        if isinstance(cultural_data, dict) and "data" in cultural_data:
            qloo_places.extend(cultural_data["data"][:5])
            logger.info(f"Added {len(cultural_data['data'][:5])} places from cultural data")
        if isinstance(travel_data, dict) and "data" in travel_data:
            qloo_places.extend(travel_data["data"][:5])
            logger.info(f"Added {len(travel_data['data'][:5])} places from travel data")
        
        logger.info(f"Total Qloo places: {len(qloo_places)}")
        
        # Create cultural insights from Qloo data
        cultural_insights = f"Discover the rich cultural heritage of {destination}"
        if qloo_places:
            place_names = [place.get("name", "") for place in qloo_places if place.get("name")]
            if place_names:
                cultural_insights = f"Explore {destination}'s cultural landscape through authentic experiences at {', '.join(place_names[:3])} and other local gems"
        else:
            # If no Qloo data, create a clean cultural insight without raw LLM response
            cultural_insights = f"Experience the rich cultural heritage of {destination}. From historic landmarks to vibrant local traditions, immerse yourself in the authentic culture and discover the unique charm that makes {destination} a must-visit destination."
        
        # Create activities based on actual Qloo places (like qloo-backend-AI format_place function)
        activities = []
        for i, place in enumerate(qloo_places[:3]):
            name = place.get("name", f"Cultural Site {i+1}")
            properties = place.get("properties", {})
            address = properties.get("address", "City Center")
            rating = properties.get("business_rating", "")
            keywords = properties.get("keywords", [])
            keyword_names = [kw.get("name", "") for kw in keywords[:2]]
            
            activities.append({
                "name": name,
                "description": f"Visit {name} in {destination}",
                "cultural_significance": f"Explore the cultural significance of {name}",
                "duration": "2 hours",
                "cost_range": "$20-50",
                "location": address,
                "best_time": "Morning" if i == 0 else "Afternoon" if i == 1 else "Evening",
                "difficulty_level": "Easy",
                "cultural_insights": keyword_names if keyword_names else ["Local culture", "Traditional practices"]
            })
        
        # If no Qloo places, create generic activities
        if not activities:
            activities = [
                {
                    "name": f"Cultural Tour of {destination}",
                    "description": f"Guided cultural tour of {destination}",
                    "cultural_significance": f"Explore the rich cultural heritage of {destination}",
                    "duration": "2 hours",
                    "cost_range": "$30-50",
                    "location": "City Center",
                    "best_time": "Morning",
                    "difficulty_level": "Easy",
                    "cultural_insights": ["Local customs", "Traditional practices"]
                }
            ]
        
        # Create day-by-day itinerary based on Qloo places and LLM response
        itinerary = []  # Initialize the itinerary list
        
        # Parse duration to get number of days
        num_days = self._parse_duration_to_days(request.duration)
        logger.info(f"Creating itinerary for {num_days} days based on duration: {request.duration}")
        logger.info(f"Request duration: '{request.duration}', Parsed days: {num_days}")
        
        if qloo_places:
            # Group places by day
            places_per_day = 2
            for day_num in range(1, num_days + 1):
                day_places = qloo_places[(day_num - 1) * places_per_day:day_num * places_per_day]
                
                if day_places:
                    place_names = [place.get("name", "") for place in day_places if place.get("name")]
                    activity_name = f"Day {day_num}: Explore {', '.join(place_names)}"
                    cultural_context = f"Visit {', '.join(place_names)} to experience authentic {destination} culture"
                else:
                    # Create diverse daily themes
                    themes = [
                        f"Cultural Introduction to {destination}",
                        f"Local Markets and Cuisine",
                        f"Historic Sites and Museums",
                        f"Arts and Entertainment",
                        f"Nature and Parks",
                        f"Local Neighborhoods",
                        f"Hidden Gems of {destination}",
                        f"Cultural Workshops",
                        f"Local Festivals and Events",
                        f"Traditional Crafts",
                        f"Historical Walking Tour",
                        f"Modern {destination}",
                        f"Cultural Exchange",
                        f"Local Traditions"
                    ]
                    theme_index = (day_num - 1) % len(themes)
                    activity_name = f"Day {day_num}: {themes[theme_index]}"
                    cultural_context = f"Discover the rich cultural heritage of {destination} through {themes[theme_index].lower()}"
                
                itinerary.append({
                    "day": day_num,
                    "activity": activity_name,
                    "cultural_context": cultural_context,
                    "places": day_places,
                    "morning_activity": f"Morning cultural activity in {destination}",
                    "afternoon_activity": f"Afternoon exploration of local culture",
                    "evening_activity": f"Evening cultural experience"
                })
        else:
            # Create diverse themes for the specified number of days
            themes = [
                f"Cultural Introduction to {destination}",
                f"Local Markets and Cuisine", 
                f"Historic Sites and Museums",
                f"Arts and Entertainment",
                f"Nature and Parks",
                f"Local Neighborhoods",
                f"Hidden Gems of {destination}",
                f"Cultural Workshops",
                f"Local Festivals and Events",
                f"Traditional Crafts",
                f"Historical Walking Tour",
                f"Modern {destination}",
                f"Cultural Exchange",
                f"Local Traditions"
            ]
            
            for day_num in range(1, num_days + 1):
                theme_index = (day_num - 1) % len(themes)
                theme = themes[theme_index]
                itinerary.append({
                    "day": day_num,
                    "activity": f"Day {day_num}: {theme}",
                    "cultural_context": f"Discover the rich cultural heritage of {destination} through {theme.lower()}",
                    "morning_activity": f"Morning: Cultural tour of {destination}",
                    "afternoon_activity": f"Afternoon: Local market visit",
                    "evening_activity": f"Evening: Traditional dinner experience"
                })
        
        # Format budget estimate properly
        budget_level = request.budget_level or "moderate"
        if budget_level == "budget":
            budget_estimate = "$800-1500"
        elif budget_level == "moderate":
            budget_estimate = "$1500-3000"
        elif budget_level == "luxury":
            budget_estimate = "$3000-6000"
        else:
            budget_estimate = "$1500-3000"
        
        return {
            "destination": destination,
            "duration": request.duration or "1 week",
            "travel_style": request.travel_style or "cultural",
            "budget_estimate": budget_estimate,
            "cultural_insights": cultural_insights,
            "itinerary": itinerary,
            "local_experiences": self._create_local_experiences_from_qloo(qloo_places, destination),
            "accommodation_recommendations": [
                {
                    "name": f"Heritage Hotel in {destination}",
                    "type": "hotel",
                    "description": f"Historic accommodation in the heart of {destination} with authentic local charm",
                    "cultural_authenticity": 0.9,
                    "price_range": "$150-300",
                    "location": "Historic District",
                    "amenities": ["WiFi", "Cultural tours", "Local restaurant", "Garden"],
                    "cultural_features": ["Historic architecture", "Traditional decor", "Local cuisine", "Cultural events"]
                },
                {
                    "name": f"Boutique Guesthouse in {destination}",
                    "type": "guesthouse",
                    "description": f"Intimate family-run guesthouse offering authentic {destination} hospitality",
                    "cultural_authenticity": 0.95,
                    "price_range": "$80-150",
                    "location": "Residential neighborhood",
                    "amenities": ["WiFi", "Breakfast", "Local guidance", "Cultural activities"],
                    "cultural_features": ["Family atmosphere", "Home-cooked meals", "Local insights", "Cultural immersion"]
                }
            ],
            "cultural_activities": activities,
            "llm_summary": llm_response,  # Include the full natural language response
            "qloo_places": qloo_places[:5],  # Include Qloo data for reference
            "practical_information": {
                "best_time_to_visit": "Spring and Fall",
                "language": "Local language with English widely spoken",
                "currency": "Local currency",
                "transportation": "Public transport, walking, and guided tours",
                "weather": "Check local weather before your trip",
                "emergency_contacts": "Local emergency services: 112"
            },
            "safety_considerations": [
                "Keep valuables secure and be aware of your surroundings",
                "Respect local customs and dress codes",
                "Stay hydrated and protect yourself from the sun",
                "Follow local COVID-19 guidelines if applicable"
            ],
            "cultural_etiquette": [
                "Greet locals with respect and learn basic phrases",
                "Dress modestly when visiting religious sites",
                "Ask permission before taking photos of people",
                "Respect local dining customs and table manners",
                "Learn about local tipping customs"
            ]
        }
    
    def _create_local_experiences_from_qloo(self, qloo_places: list, destination: str) -> list:
        """Create local experiences based on real Qloo data"""
        local_experiences = []
        
        # Create experiences from actual Qloo places
        for i, place in enumerate(qloo_places[:3]):
            name = place.get("name", f"Cultural Site {i+1}")
            properties = place.get("properties", {})
            address = properties.get("address", "City Center")
            description = properties.get("description", f"Visit {name} in {destination}")
            rating = properties.get("business_rating", 4.0)
            
            # Create different types of experiences based on place type
            experience_types = [
                {
                    "name": f"Guided Tour of {name}",
                    "description": f"Explore {name} with a knowledgeable local guide",
                    "cultural_value": min(0.9 + (rating - 4.0) * 0.1, 1.0),
                    "duration": "2-3 hours",
                    "cost": "$30-60",
                    "location": address,
                    "local_contact": f"tours@{destination.lower().replace(' ', '')}.com",
                    "cultural_context": f"Discover the cultural significance and history of {name}"
                },
                {
                    "name": f"Cultural Workshop at {name}",
                    "description": f"Participate in hands-on cultural activities at {name}",
                    "cultural_value": min(0.95 + (rating - 4.0) * 0.05, 1.0),
                    "duration": "3-4 hours",
                    "cost": "$50-80",
                    "location": address,
                    "local_contact": f"workshops@{destination.lower().replace(' ', '')}.com",
                    "cultural_context": f"Immerse yourself in local traditions and crafts at {name}"
                }
            ]
            
            # Add one experience per place
            local_experiences.append(experience_types[i % len(experience_types)])
        
        # If no Qloo places, create generic experiences
        if not local_experiences:
            local_experiences = [
                {
                    "name": f"Local Market Experience in {destination}",
                    "description": f"Explore authentic local markets and interact with vendors in {destination}",
                    "cultural_value": 0.9,
                    "duration": "3 hours",
                    "cost": "$50",
                    "location": "Local markets",
                    "local_contact": "contact@example.com",
                    "cultural_context": f"Traditional market culture and local commerce in {destination}"
                },
                {
                    "name": f"Cooking Class in {destination}",
                    "description": f"Learn to cook traditional dishes from {destination} with local chefs",
                    "cultural_value": 0.95,
                    "duration": "4 hours",
                    "cost": "$80",
                    "location": "Local cooking school",
                    "local_contact": "cooking@example.com",
                    "cultural_context": f"Culinary traditions and food culture of {destination}"
                }
            ]
        
        return local_experiences
    
    def _create_enhanced_fallback_itinerary(self, destination: str, cultural_data: dict, travel_data: dict) -> dict:
        """Create an enhanced fallback itinerary using Qloo data"""
        # Extract actual places from Qloo data
        qloo_places = []
        if isinstance(cultural_data, dict) and "data" in cultural_data:
            qloo_places.extend(cultural_data["data"][:3])
        if isinstance(travel_data, dict) and "data" in travel_data:
            qloo_places.extend(travel_data["data"][:3])
        
        # Create activities based on actual Qloo places
        activities = []
        for i, place in enumerate(qloo_places[:3]):
            name = place.get("name", f"Cultural Site {i+1}")
            properties = place.get("properties", {})
            address = properties.get("address", "City Center")
            rating = properties.get("business_rating", "")
            keywords = properties.get("keywords", [])
            keyword_names = [kw.get("name", "") for kw in keywords[:2]]
            
            activities.append({
                "name": name,
                "description": f"Visit {name} in {destination}",
                "cultural_significance": f"Explore the cultural significance of {name}",
                            "duration": "2 hours",
                            "cost_range": "$20-50",
                "location": address,
                "best_time": "Morning" if i == 0 else "Afternoon" if i == 1 else "Evening",
                "difficulty_level": "Easy",
                "cultural_insights": keyword_names if keyword_names else ["Local culture", "Traditional practices"]
            })
        
        # If no Qloo places, create generic activities
        if not activities:
            activities = [
                {
                    "name": f"Cultural Tour of {destination}",
                    "description": f"Guided cultural tour of {destination}",
                    "cultural_significance": f"Explore the rich cultural heritage of {destination}",
                    "duration": "2 hours",
                    "cost_range": "$30-50",
                            "location": "City Center",
                            "best_time": "Morning",
                            "difficulty_level": "Easy",
                    "cultural_insights": ["Local customs", "Traditional practices"]
                }
            ]
        
        # Create cultural insights based on actual Qloo data
        cultural_insights = f"Discover the rich cultural heritage of {destination}"
        if qloo_places:
            place_names = [place.get("name", "") for place in qloo_places if place.get("name")]
            if place_names:
                cultural_insights = f"Explore {destination}'s cultural landscape through authentic experiences at {', '.join(place_names[:2])} and other local gems"
        
        # Create a proper multi-day itinerary
        itinerary = []
        # Use a reasonable default of 5 days for fallback itinerary
        num_days = 5
        
        themes = [
            f"Cultural Introduction to {destination}",
            f"Explore Local Markets and Cuisine",
            f"Historic Sites and Museums",
            f"Arts and Entertainment",
            f"Local Neighborhoods"
        ]
        
        for day_num in range(1, num_days + 1):
            theme_index = (day_num - 1) % len(themes)
            theme = themes[theme_index]
            
            if day_num == 1:
                cultural_context = f"Learn about {destination} culture and respect local traditions"
            elif day_num == 2:
                cultural_context = f"Discover {destination}'s culinary traditions and local markets"
            elif day_num == 3:
                cultural_context = f"Visit historic landmarks and cultural institutions in {destination}"
            elif day_num == 4:
                cultural_context = f"Experience {destination}'s vibrant arts and entertainment scene"
            else:
                cultural_context = f"Explore authentic local neighborhoods and daily life in {destination}"
            
            itinerary.append({
                "day": day_num,
                "activity": f"Day {day_num}: {theme}",
                "cultural_context": cultural_context
            })
        
        return {
            "destination": destination,
            "duration": "1 week",
            "travel_style": "cultural",
            "budget_estimate": "$2000-3000",
            "cultural_insights": cultural_insights,
            "itinerary": itinerary,
            "local_experiences": [
                {
                    "name": f"Local Market Experience in {destination}",
                    "description": f"Explore authentic local markets and interact with vendors in {destination}",
                    "cultural_value": 0.9,
                    "duration": "3 hours",
                    "cost": "$50",
                    "location": "Local markets",
                    "local_contact": "contact@example.com",
                    "cultural_context": f"Traditional market culture and local commerce in {destination}"
                },
                {
                    "name": f"Cooking Class in {destination}",
                    "description": f"Learn to cook traditional dishes from {destination} with local chefs",
                    "cultural_value": 0.95,
                    "duration": "4 hours",
                    "cost": "$80",
                    "location": "Local cooking school",
                    "local_contact": "cooking@example.com",
                    "cultural_context": f"Culinary traditions and food culture of {destination}"
                }
            ],
            "accommodation_recommendations": [
                {
                    "name": f"Heritage Hotel in {destination}",
                    "type": "hotel",
                    "description": f"Historic accommodation in the heart of {destination} with authentic local charm",
                    "cultural_authenticity": 0.9,
                    "price_range": "$150-300",
                    "location": "Historic District",
                    "amenities": ["WiFi", "Cultural tours", "Local restaurant", "Garden"],
                    "cultural_features": ["Historic architecture", "Traditional decor", "Local cuisine", "Cultural events"]
                },
                {
                    "name": f"Boutique Guesthouse in {destination}",
                    "type": "guesthouse",
                    "description": f"Intimate family-run guesthouse offering authentic {destination} hospitality",
                    "cultural_authenticity": 0.95,
                    "price_range": "$80-150",
                    "location": "Residential neighborhood",
                    "amenities": ["WiFi", "Breakfast", "Local guidance", "Cultural activities"],
                    "cultural_features": ["Family atmosphere", "Home-cooked meals", "Local insights", "Cultural immersion"]
                }
            ],
            "cultural_activities": activities,
            "practical_information": {
                "best_time_to_visit": "Spring and Fall",
                "language": "Local language with English widely spoken",
                "currency": "Local currency",
                "transportation": "Public transport, walking, and guided tours",
                "weather": "Check local weather before your trip",
                "emergency_contacts": "Local emergency services: 112"
            },
            "safety_considerations": [
                "Keep valuables secure and be aware of your surroundings",
                "Respect local customs and dress codes",
                "Stay hydrated and protect yourself from the sun",
                "Follow local COVID-19 guidelines if applicable"
            ],
            "cultural_etiquette": [
                "Greet locals with respect and learn basic phrases",
                "Dress modestly when visiting religious sites",
                "Ask permission before taking photos of people",
                "Respect local dining customs and table manners",
                "Learn about local tipping customs"
            ]
        }

    def _parse_destination_recommendations(self, llm_response: str, cultural_preferences: dict) -> dict:
        """Parse LLM response into destination recommendations"""
        return {
            "recommendations": [
                {
                    "destination": "Sample Destination",
                    "country": "Sample Country",
                    "region": "Sample Region",
                    "cultural_score": 0.9,
                    "match_score": 0.8,
                    "reasons": ["reason1", "reason2"],
                    "cultural_highlights": ["highlight1", "highlight2"],
                    "best_time_to_visit": "Spring",
                    "cultural_events": ["event1", "event2"]
                }
            ],
            "insights": ["insight1", "insight2"],
            "cultural_themes": ["theme1", "theme2"]
        }

    def _parse_events_analysis(self, llm_response: str, events_data: dict) -> dict:
        """Parse LLM response into events analysis"""
        return {
            "events": [
                {
                    "name": "Cultural Event",
                    "description": "Event description",
                    "date": "2024-01-01",
                    "location": "City Center",
                    "cultural_significance": "High cultural importance",
                    "duration": "1 day",
                    "cost": "Free",
                    "participation_level": "spectator"
                }
            ],
            "cultural_calendar": {"January": ["event1", "event2"]},
            "insights": ["insight1", "insight2"],
            "planning_tips": ["tip1", "tip2"]
        }

    def _parse_guides_analysis(self, llm_response: str, guides_data: dict) -> dict:
        """Parse LLM response into guides analysis"""
        return {
            "guides": [
                {
                    "name": "Local Guide",
                    "specialization": "Cultural History",
                    "languages": ["English", "Spanish"],
                    "experience_years": 5,
                    "cultural_expertise": ["expertise1", "expertise2"],
                    "rating": 4.8,
                    "contact_info": {"email": "guide@example.com"},
                    "availability": "Weekdays"
                }
            ],
            "insights": ["insight1", "insight2"],
            "booking_tips": ["tip1", "tip2"]
        }

    def _summarize_cultural_data(self, cultural_data: dict) -> str:
        """Summarize cultural data to reduce token count"""
        if not cultural_data:
            return "No cultural data available"
        
        try:
            # Extract key information only
            summary_parts = []
            
            if isinstance(cultural_data, dict):
                # Get destination name
                destination = cultural_data.get("destination", "Unknown")
                summary_parts.append(f"Destination: {destination}")
                
                # Get cultural insights (limit to first 3)
                insights = cultural_data.get("insights", [])
                if insights and isinstance(insights, list):
                    summary_parts.append(f"Key insights: {', '.join(insights[:3])}")
                
                # Get cultural events (limit to first 2)
                events = cultural_data.get("events", [])
                if events and isinstance(events, list):
                    event_names = [event.get("name", "Event") for event in events[:2]]
                    summary_parts.append(f"Cultural events: {', '.join(event_names)}")
                
                # Get customs/traditions (limit to first 3)
                customs = cultural_data.get("customs", [])
                if customs and isinstance(customs, list):
                    summary_parts.append(f"Customs: {', '.join(customs[:3])}")
                
                # Get Qloo API specific data
                if "data" in cultural_data:
                    qloo_data = cultural_data["data"]
                    if isinstance(qloo_data, list) and len(qloo_data) > 0:
                        # Extract entity names and properties
                        entities = []
                        for item in qloo_data[:5]:  # Limit to first 5 entities
                            name = item.get("name", "Unknown")
                            entity_type = item.get("type", "place")
                            properties = item.get("properties", {})
                            
                            # Get relevant properties
                            address = properties.get("address", "")
                            rating = properties.get("business_rating", "")
                            keywords = properties.get("keywords", [])
                            keyword_names = [kw.get("name", "") for kw in keywords[:3]]
                            
                            entity_info = f"{name} ({entity_type})"
                            if address:
                                entity_info += f" at {address}"
                            if rating:
                                entity_info += f" (Rating: {rating})"
                            if keyword_names:
                                entity_info += f" - {', '.join(keyword_names)}"
                            
                            entities.append(entity_info)
                        
                        if entities:
                            summary_parts.append(f"Qloo Recommendations: {'; '.join(entities)}")
            
            return "; ".join(summary_parts) if summary_parts else "Cultural data available"
            
        except Exception as e:
            logger.error(f"Failed to summarize cultural data: {e}")
            return "Cultural insights available"

    def _summarize_travel_data(self, travel_data: dict) -> str:
        """Summarize travel data to reduce token count"""
        if not travel_data:
            return "No travel data available"
        
        try:
            # Extract key information only
            summary_parts = []
            
            if isinstance(travel_data, dict):
                # Get recommendations (limit to first 3)
                recommendations = travel_data.get("recommendations", [])
                if recommendations and isinstance(recommendations, list):
                    rec_names = [rec.get("name", "Recommendation") for rec in recommendations[:3]]
                    summary_parts.append(f"Recommendations: {', '.join(rec_names)}")
                
                # Get attractions (limit to first 3)
                attractions = travel_data.get("attractions", [])
                if attractions and isinstance(attractions, list):
                    attr_names = [attr.get("name", "Attraction") for attr in attractions[:3]]
                    summary_parts.append(f"Attractions: {', '.join(attr_names)}")
                
                # Get activities (limit to first 3)
                activities = travel_data.get("activities", [])
                if activities and isinstance(activities, list):
                    act_names = [act.get("name", "Activity") for act in activities[:3]]
                    summary_parts.append(f"Activities: {', '.join(act_names)}")
                
                # Get Qloo API specific data
                if "data" in travel_data:
                    qloo_data = travel_data["data"]
                    if isinstance(qloo_data, list) and len(qloo_data) > 0:
                        # Extract entity names and properties
                        entities = []
                        for item in qloo_data[:5]:  # Limit to first 5 entities
                            name = item.get("name", "Unknown")
                            entity_type = item.get("type", "place")
                            properties = item.get("properties", {})
                            
                            # Get relevant properties
                            address = properties.get("address", "")
                            rating = properties.get("business_rating", "")
                            cost = properties.get("average_cost", "")
                            keywords = properties.get("keywords", [])
                            keyword_names = [kw.get("name", "") for kw in keywords[:3]]
                            
                            entity_info = f"{name} ({entity_type})"
                            if address:
                                entity_info += f" at {address}"
                            if rating:
                                entity_info += f" (Rating: {rating})"
                            if cost:
                                entity_info += f" (Cost: {cost})"
                            if keyword_names:
                                entity_info += f" - {', '.join(keyword_names)}"
                            
                            entities.append(entity_info)
                        
                        if entities:
                            summary_parts.append(f"Qloo Travel Data: {'; '.join(entities)}")
            
            return "; ".join(summary_parts) if summary_parts else "Travel recommendations available"
            
        except Exception as e:
            logger.error(f"Failed to summarize travel data: {e}")
            return "Travel recommendations available"
    
    def _parse_duration_to_days(self, duration: str) -> int:
        """Parse duration string to number of days"""
        if not duration:
            return 7  # Default to 1 week
        
        duration_lower = duration.lower().strip()
        
        # Extract number from duration string
        import re
        number_match = re.search(r'(\d+)', duration_lower)
        if not number_match:
            return 7  # Default if no number found
        
        num = int(number_match.group(1))
        
        # Determine multiplier based on time unit
        if 'day' in duration_lower:
            return num
        elif 'week' in duration_lower:
            return num * 7
        elif 'month' in duration_lower:
            return num * 30
        else:
            # Assume days if no unit specified
            return num

# API Endpoints
@router.post("/plan", response_model=TravelPlanningResponse)
async def plan_travel(
    request: TravelPlanningRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Plan travel itinerary"""
    travel_service = TravelService(db)
    
    # Track event
    if current_user:
        try:
            db.analytics.create(
                data={
                    "event_type": "travel",
                    "event_data": {"destination": request.destination, "travel_style": request.travel_style},
                    "user_id": str(current_user.id),  # Convert to string for Prisma
                    "session_id": f"session_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d')}"
                }
            )
        except Exception as analytics_error:
            logger.error(f"Failed to track analytics: {analytics_error}")
            # Continue without analytics tracking
    
    return await travel_service.plan_travel(request, current_user.id if current_user else None)

@router.post("/destinations", response_model=DestinationRecommendationResponse)
async def get_destination_recommendations(
    request: DestinationRecommendationRequest,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Get destination recommendations"""
    travel_service = TravelService(db)
    return await travel_service.get_destination_recommendations(request)

@router.post("/cultural-events", response_model=CulturalEventsResponse)
async def get_cultural_events(
    request: CulturalEventsRequest,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Get cultural events"""
    travel_service = TravelService(db)
    return await travel_service.get_cultural_events(request)

@router.post("/local-guides", response_model=LocalGuidesResponse)
async def get_local_guides(
    request: LocalGuidesRequest,
    current_user = Depends(get_optional_user_no_auth),
    db = Depends(get_db)
):
    """Get local guides"""
    travel_service = TravelService(db)
    return await travel_service.get_local_guides(request)

@router.get("/user-trips")
def get_user_trips(
    limit: int = 10,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's trips"""
    trips = db.trip.find_many(
        where={"user_id": current_user.id},
        order={"created_at": "desc"},
        take=limit
    )
    return trips 