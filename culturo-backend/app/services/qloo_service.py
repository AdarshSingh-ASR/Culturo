import httpx
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from ..config import settings
from ..shared.errors import QlooServiceError, ExternalServiceError

logger = logging.getLogger(__name__)

class QlooService:
    def __init__(self):
        self.api_key = settings.qloo_api_key
        self.base_url = settings.qloo_api_url
        self.timeout = 30.0
        
    async def get_taste_insights(self, topic: str) -> Dict[str, Any]:
        """Get taste insights for a topic using available hackathon API"""
        try:
            # First, try to get relevant entities based on the topic
            # For AI/tech topics, we need to be more specific about the query
            query_topic = self._optimize_query_for_topic(topic)
            
            # Use the available /v2/insights endpoint with optimized query
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={query_topic}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        
                        # If we got generic places, try to provide more relevant data
                        if self._are_entities_relevant(topic, entities):
                            return {
                                "topic": topic,
                                "taste_score": 0.75,
                                "cultural_relevance": 0.8,
                                "related_topics": [entity.get("name", "") for entity in entities[:3]],
                                "demographics": {"18-25": 0.3, "26-35": 0.4, "36-45": 0.2, "45+": 0.1},
                                "geographic_distribution": {"US": 0.4, "EU": 0.3, "Asia": 0.2, "Other": 0.1},
                                "trending": True,
                                "growth_rate": 0.15,
                                "entities": entities[:5]  # Include actual entities
                            }
                        else:
                            # If entities are not relevant, use topic-specific data
                            return self._get_topic_specific_insights(topic)
                    else:
                        return self._get_topic_specific_insights(topic)
                elif response.status_code == 401:
                    raise QlooServiceError("taste/insights", "Unauthorized - Invalid API key", response.status_code)
                elif response.status_code == 429:
                    raise QlooServiceError("taste/insights", "Rate limit exceeded", response.status_code)
                else:
                    logger.error(f"Qloo API error: {response.status_code} - {response.text}")
                    return self._get_topic_specific_insights(topic)
                    
        except QlooServiceError:
            raise
        except Exception as e:
            logger.error(f"Qloo taste insights failed: {str(e)}")
            return self._get_topic_specific_insights(topic)
    
    async def get_historical_data(self, topic: str) -> Dict[str, Any]:
        """Get historical data for a topic using available hackathon API"""
        try:
            # Use the available /v2/insights endpoint with topic as query
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={topic}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "topic": topic,
                            "historical_trends": [
                                {"month": "2024-01", "score": 0.6},
                                {"month": "2024-02", "score": 0.65},
                                {"month": "2024-03", "score": 0.7}
                            ],
                            "seasonal_patterns": ["spring_peak", "summer_dip"],
                            "growth_trajectory": "increasing",
                            "entities": entities[:5]  # Include actual entities
                        }
                    else:
                        return data
                else:
                    logger.error(f"Qloo historical data error: {response.status_code} - {response.text}")
                    return self._get_mock_historical_data(topic)
                    
        except Exception as e:
            logger.error(f"Qloo historical data failed: {str(e)}")
            return self._get_mock_historical_data(topic)
    
    async def get_user_preferences(self, user_id: int, user_input: dict = None) -> Dict[str, Any]:
        """Get user preferences from Qloo using available hackathon API"""
        try:
            # Use user input if provided, otherwise use defaults
            if user_input:
                movie_name = user_input.get("movie_name")
                book_name = user_input.get("book_name") 
                place_name = user_input.get("place_name")
                age = user_input.get("age", "25_to_29")
                gender = user_input.get("gender", "male")
            else:
                # Fallback to default entities if no user input
                movie_name = "The Shawshank Redemption"
                book_name = "To Kill a Mockingbird"
                place_name = "Paris"
                age = "25_to_29"
                gender = "male"
            
            entity_ids = []
            
            # Search for movie entity ID
            if movie_name:
                try:
                    movie_id = await self._fetch_entity_id(movie_name, "movie")
                    if movie_id:
                        entity_ids.append(movie_id)
                        logger.info(f"Found movie entity ID: {movie_id} for '{movie_name}'")
                except Exception as e:
                    logger.warning(f"Failed to search for movie '{movie_name}': {str(e)}")
            
            # Search for book entity ID
            if book_name:
                try:
                    book_id = await self._fetch_entity_id(book_name, "book")
                    if book_id:
                        entity_ids.append(book_id)
                        logger.info(f"Found book entity ID: {book_id} for '{book_name}'")
                except Exception as e:
                    logger.warning(f"Failed to search for book '{book_name}': {str(e)}")
            
            # Search for place entity ID
            if place_name:
                try:
                    place_id = await self._fetch_entity_id(place_name, "place")
                    if place_id:
                        entity_ids.append(place_id)
                        logger.info(f"Found place entity ID: {place_id} for '{place_name}'")
                except Exception as e:
                    logger.warning(f"Failed to search for place '{place_name}': {str(e)}")
            
            if not entity_ids:
                logger.warning("No entity IDs found, using fallback")
                return self._get_mock_user_preferences(user_id)
            
            # Now use the entity IDs to get personalized insights
            joined_ids = ",".join(entity_ids)
            
            params = {
                "filter.type": "urn:entity:movie",  # Get movie recommendations
                "signal.interests.entities": joined_ids,
                "signal.demographics.age": age,
                "signal.demographics.gender": gender,
                "feature.explainability": "true",
                "take": "10"
            }
            
            headers = {
                "x-api-key": self.api_key,
                "accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v2/insights",
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Handle the nested structure: {success: true, results: {entities: [...]}}
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "user_id": user_id,
                            "preferences": {
                                "music": ["jazz", "classical"],
                                "food": ["italian", "japanese"],
                                "fashion": ["minimalist", "sustainable"],
                                "travel": ["cultural", "adventure"]
                            },
                            "cultural_affinities": ["european", "asian"],
                            "taste_profile": "sophisticated",
                            "entities": entities[:5],  # Include actual entities
                            "signal_entities": entity_ids,  # Include the signal entities used
                            "demographics": {"age": age, "gender": gender},
                            "user_input": {
                                "movie_name": movie_name,
                                "book_name": book_name,
                                "place_name": place_name
                            }
                        }
                    else:
                        return data
                else:
                    logger.error(f"Qloo user preferences error: {response.status_code} - {response.text}")
                    return self._get_mock_user_preferences(user_id)
                    
        except Exception as e:
            logger.error(f"Qloo user preferences failed: {str(e)}")
            return self._get_mock_user_preferences(user_id)
    
    async def _fetch_entity_id(self, name: str, entity_type: str) -> Optional[str]:
        """Helper method to fetch entity ID from Qloo search API"""
        try:
            search_url = f"{self.base_url}/search"
            search_params = {
                "query": name,
                "types": f"urn:entity:{entity_type}"
            }
            
            headers = {
                "x-api-key": self.api_key,
                "accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                search_response = await client.get(
                    search_url,
                    params=search_params,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    # Check if the response has 'results' key (new format)
                    if 'results' in search_data and len(search_data['results']) > 0:
                        entity_id = search_data['results'][0].get('entity_id')
                        if entity_id:
                            return entity_id
                    # Check if the response is a direct array (old format)
                    elif isinstance(search_data, list) and len(search_data) > 0 and "entity_id" in search_data[0]:
                        entity_id = search_data[0]["entity_id"]
                        if entity_id:
                            return entity_id
                            
        except Exception as e:
            logger.warning(f"Failed to search for entity {name} ({entity_type}): {str(e)}")
        
        return None
    
    async def get_cultural_insights(self, text: str) -> Dict[str, Any]:
        """Get cultural insights for text using available hackathon API"""
        try:
            # First, search for entities related to the text
            # Determine the appropriate entity types based on the text
            text_lower = text.lower()
            
            if "movie" in text_lower or "film" in text_lower:
                entity_types = "urn:entity:movie"
                search_terms = ["The Shawshank Redemption", "The Godfather", "Pulp Fiction"]
            elif "music" in text_lower or "song" in text_lower:
                entity_types = "urn:entity:artist"
                search_terms = ["Queen", "The Beatles", "Bob Dylan"]
            elif "book" in text_lower or "reading" in text_lower:
                entity_types = "urn:entity:book"
                search_terms = ["To Kill a Mockingbird", "1984", "The Great Gatsby"]
            else:
                # Default to movies
                entity_types = "urn:entity:movie"
                search_terms = ["The Shawshank Redemption", "The Godfather", "Pulp Fiction"]
            
            entity_ids = []
            
            # Search for entities to get their IDs
            for search_term in search_terms:
                try:
                    search_url = f"{self.base_url}/search"
                    search_params = {
                        "query": search_term,
                        "types": entity_types
                    }
                    
                    headers = {
                        "x-api-key": self.api_key,
                        "accept": "application/json"
                    }
                    
                    async with httpx.AsyncClient() as client:
                        search_response = await client.get(
                            search_url,
                            params=search_params,
                            headers=headers,
                            timeout=self.timeout
                        )
                        
                        if search_response.status_code == 200:
                            search_data = search_response.json()
                            # Check if the response has 'results' key (new format)
                            if 'results' in search_data and len(search_data['results']) > 0:
                                entity_id = search_data['results'][0].get('entity_id')
                                if entity_id:
                                    entity_ids.append(entity_id)
                            # Check if the response is a direct array (old format)
                            elif isinstance(search_data, list) and len(search_data) > 0 and "entity_id" in search_data[0]:
                                entity_id = search_data[0]["entity_id"]
                                if entity_id:
                                    entity_ids.append(entity_id)
                                    
                except Exception as e:
                    logger.warning(f"Failed to search for entity {search_term}: {str(e)}")
                    continue
            
            if not entity_ids:
                logger.warning("No entity IDs found, using fallback")
                return self._get_mock_cultural_insights(text)
            
            # Now use the entity IDs to get cultural insights
            joined_ids = ",".join(entity_ids)
            
            # Use default demographics
            age = "25_to_29"  # Fixed: Use correct Qloo API format
            gender = "male"
            
            # Determine the target entity type for recommendations
            if "movie" in text_lower or "film" in text_lower:
                target_entity_type = "urn:entity:movie"
            elif "music" in text_lower or "song" in text_lower:
                target_entity_type = "urn:entity:artist"
            elif "book" in text_lower or "reading" in text_lower:
                target_entity_type = "urn:entity:book"
            else:
                target_entity_type = "urn:entity:movie"
            
            params = {
                "filter.type": target_entity_type,
                "signal.interests.entities": joined_ids,
                "signal.demographics.age": age,
                "signal.demographics.gender": gender,
                "feature.explainability": "true",
                "take": "10"
            }
            
            headers = {
                "x-api-key": self.api_key,
                "accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v2/insights",
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Handle the nested structure: {success: true, results: {entities: [...]}}
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "cultural_elements": [entity.get("name", "") for entity in entities[:3]],
                            "cultural_significance": "High cultural value",
                            "traditional_occasions": ["Family gatherings", "Cultural celebrations"],
                            "preparation_methods": ["Traditional methods", "Modern techniques"],
                            "origin": "Various cultural origins",
                            "entities": entities[:5],
                            "signal_entities": entity_ids,
                            "target_entity_type": target_entity_type
                        }
                    else:
                        return data
                else:
                    logger.error(f"Qloo cultural insights error: {response.status_code} - {response.text}")
                    return self._get_mock_cultural_insights(text)
                    
        except Exception as e:
            logger.error(f"Qloo cultural insights failed: {str(e)}")
            return self._get_mock_cultural_insights(text)
    
    async def get_cultural_context(self, topic: str) -> Dict[str, Any]:
        """Get cultural context for a topic using available hackathon API"""
        try:
            # Use the available /v2/insights endpoint with topic as query
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={topic}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "topic": topic,
                            "origin": "Various origins",
                            "historical_significance": "Significant historical value",
                            "geographic_spread": [entity.get("name", "") for entity in entities[:3]],
                            "cultural_evolution": "Evolving cultural significance",
                            "entities": entities[:5]  # Include actual entities
                        }
                    else:
                        return data
                else:
                    logger.error(f"Qloo cultural context error: {response.status_code} - {response.text}")
                    return self._get_mock_cultural_context(topic)
                    
        except Exception as e:
            logger.error(f"Qloo cultural context failed: {str(e)}")
            return self._get_mock_cultural_context(topic)
    
    async def get_user_cultural_insights(self, user_id: int) -> Dict[str, Any]:
        """Get user cultural insights using available hackathon API"""
        try:
            # Use the available /v2/insights endpoint with a general query
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query=culture"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "user_id": user_id,
                            "top_interests": [entity.get("name", "") for entity in entities[:3]],
                            "taste_evolution": "Evolving",
                            "cultural_affinities": ["affinity1", "affinity2"],
                            "learning_patterns": ["pattern1", "pattern2"],
                            "exposure_score": 0.7,
                            "diversity_index": 0.6,
                            "entities": entities[:5]  # Include actual entities
                        }
                    else:
                        return data
                else:
                    logger.error(f"Qloo user cultural insights error: {response.status_code} - {response.text}")
                    return self._get_mock_user_cultural_insights(user_id)
                    
        except Exception as e:
            logger.error(f"Qloo user cultural insights failed: {str(e)}")
            return self._get_mock_user_cultural_insights(user_id)
    
    async def get_user_cultural_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user cultural preferences using available hackathon API"""
        try:
            # Use the available /v2/insights endpoint with a general query
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query=culture"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "user_id": user_id,
                            "cultural_preferences": [entity.get("name", "") for entity in entities[:3]],
                            "cultural_affinities": ["affinity1", "affinity2"],
                            "cultural_exposure": 0.7,
                            "entities": entities[:5]  # Include actual entities
                        }
                    else:
                        return data
                else:
                    logger.error(f"Qloo user cultural preferences error: {response.status_code} - {response.text}")
                    return self._get_mock_user_cultural_preferences(user_id)
                    
        except Exception as e:
            logger.error(f"Qloo user cultural preferences failed: {str(e)}")
            return self._get_mock_user_cultural_preferences(user_id)
    
    async def get_food_cultural_context(self, food_name: str) -> Dict[str, Any]:
        """Get cultural context for food using available hackathon API"""
        try:
            # For food items, we need to use a more generic location query since Qloo expects places
            # Try to find a related location or use a generic food-friendly location
            food_related_location = self._get_food_related_location(food_name)
            
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={food_related_location}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "food_name": food_name,
                            "origin": self._get_food_origin(food_name),
                            "cultural_significance": "High cultural value",
                            "traditional_occasions": self._get_food_occasions(food_name),
                            "preparation_methods": self._get_food_preparation_methods(food_name),
                            "entities": entities[:3]  # Include actual entities
                        }
                    else:
                        return self._get_mock_food_cultural_context(food_name)
                else:
                    logger.error(f"Qloo food cultural context error: {response.status_code} - {response.text}")
                    return self._get_mock_food_cultural_context(food_name)
                    
        except Exception as e:
            logger.error(f"Qloo food cultural context failed: {str(e)}")
            return self._get_mock_food_cultural_context(food_name)
    
    async def get_nutritional_info(self, food_name: str) -> Dict[str, Any]:
        """Get nutritional information for food using available hackathon API"""
        try:
            # For food items, we need to use a more generic location query since Qloo expects places
            # Try to find a related location or use a generic food-friendly location
            food_related_location = self._get_food_related_location(food_name)
            
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={food_related_location}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "food_name": food_name,
                            "calories": self._get_food_calories(food_name),
                            "protein": self._get_food_protein(food_name),
                            "carbohydrates": self._get_food_carbs(food_name),  # Fixed field name
                            "fat": self._get_food_fat(food_name),
                            "fiber": self._get_food_fiber(food_name),
                            "sugar": self._get_food_sugar(food_name),
                            "sodium": self._get_food_sodium(food_name),
                            "allergens": self._get_food_allergens(food_name),
                            "health_benefits": self._get_food_health_benefits(food_name),
                            "entities": entities[:3]  # Include actual entities
                        }
                    else:
                        return self._get_mock_nutritional_info(food_name)
                else:
                    logger.error(f"Qloo nutritional info error: {response.status_code} - {response.text}")
                    return self._get_mock_nutritional_info(food_name)
                    
        except Exception as e:
            logger.error(f"Qloo nutritional info failed: {str(e)}")
            return self._get_mock_nutritional_info(food_name)
    
    async def get_destination_cultural_insights(self, destination: str) -> Dict[str, Any]:
        """Get cultural insights for a destination"""
        try:
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={destination}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        return {"data": data["results"]["entities"]}
                    else:
                        return data
                else:
                    logger.error(f"Qloo destination cultural insights error: {response.status_code} - {response.text}")
                    return self._get_mock_destination_cultural_insights(destination)
                    
        except Exception as e:
            logger.error(f"Qloo destination cultural insights failed: {str(e)}")
            return self._get_mock_destination_cultural_insights(destination)
    
    async def get_travel_recommendations(self, destination: str, travel_style: str, cultural_interests: List[str]) -> Dict[str, Any]:
        """Get travel recommendations"""
        try:
            # For now, we'll use the same endpoint as cultural insights since the hackathon API doesn't have a specific recommendations endpoint
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={destination}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        return {"data": data["results"]["entities"]}
                    else:
                        return data
                else:
                    logger.error(f"Qloo travel recommendations error: {response.status_code} - {response.text}")
                    return self._get_mock_travel_recommendations(destination, travel_style, cultural_interests)
                    
        except Exception as e:
            logger.error(f"Qloo travel recommendations failed: {str(e)}")
            return self._get_mock_travel_recommendations(destination, travel_style, cultural_interests)
    
    async def get_cultural_events(self, destination: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get cultural events for a destination using available hackathon API"""
        try:
            # Use the available /v2/insights endpoint with destination as query
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={destination}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "destination": destination,
                            "events": [
                                {
                                    "name": entity.get("name", f"Cultural Event in {destination}"),
                                    "description": entity.get("properties", {}).get("description", f"Cultural event in {destination}"),
                                    "date": "2024-12-01",
                                    "location": entity.get("properties", {}).get("address", destination),
                                    "cultural_significance": "High",
                                    "duration": "2-4 hours",
                                    "cost": "$20-50",
                                    "participation_level": "spectator"
                                }
                                for entity in entities[:3]
                            ],
                            "entities": entities[:5]  # Include actual entities
                        }
                    else:
                        return data
                else:
                    logger.error(f"Qloo cultural events error: {response.status_code} - {response.text}")
                    return self._get_mock_cultural_events(destination)
                    
        except Exception as e:
            logger.error(f"Qloo cultural events failed: {str(e)}")
            return self._get_mock_cultural_events(destination)
    
    async def get_local_guides(self, destination: str, specialization: str = None, languages: List[str] = None) -> Dict[str, Any]:
        """Get local guides for a destination using available hackathon API"""
        try:
            # Use the available /v2/insights endpoint with destination as query
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={destination}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "destination": destination,
                            "guides": [
                                {
                                    "name": f"Local Guide {i+1}",
                                    "specialization": specialization or "Cultural Tours",
                                    "languages": languages or ["English"],
                                    "experience_years": 5 + i,
                                    "cultural_expertise": [entity.get("name", "") for entity in entities[:2]],
                                    "rating": 4.5 + (i * 0.1),
                                    "contact_info": {"email": f"guide{i+1}@{destination.lower()}.com", "phone": f"+1-555-{1000+i}"},
                                    "availability": "Available"
                                }
                                for i, entity in enumerate(entities[:3])
                            ],
                            "entities": entities[:5]  # Include actual entities
                        }
                    else:
                        return data
                else:
                    logger.error(f"Qloo local guides error: {response.status_code} - {response.text}")
                    return self._get_mock_local_guides(destination)
                    
        except Exception as e:
            logger.error(f"Qloo local guides failed: {str(e)}")
            return self._get_mock_local_guides(destination)
    
    async def get_cultural_data(self, cultural_interests: List[str], cultural_background: str = None, preferred_cultures: List[str] = None) -> Dict[str, Any]:
        """Get cultural data based on interests and background using available hackathon API"""
        try:
            # Use the available /v2/insights endpoint with cultural interests as query
            query = " ".join(cultural_interests) if cultural_interests else "culture"
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={query}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "cultural_interests": cultural_interests,
                            "cultural_background": cultural_background,
                            "preferred_cultures": preferred_cultures,
                            "cultural_insights": [entity.get("name", "") for entity in entities[:5]],
                            "cultural_affinities": ["affinity1", "affinity2"],
                            "cultural_exposure": 0.7,
                            "entities": entities[:5]  # Include actual entities
                        }
                    else:
                        return data
                else:
                    logger.error(f"Qloo cultural data error: {response.status_code} - {response.text}")
                    return self._get_mock_cultural_data(cultural_interests, cultural_background, preferred_cultures)
                    
        except Exception as e:
            logger.error(f"Qloo cultural data failed: {str(e)}")
            return self._get_mock_cultural_data(cultural_interests, cultural_background, preferred_cultures)
    
    async def get_trending_items(self, category: str = None) -> Dict[str, Any]:
        """Get trending items using available hackathon API"""
        try:
            # Use the available /v2/insights endpoint with category as query
            query = category or "trending"
            url = f"{self.base_url}/v2/insights/?filter.type=urn:entity:place&filter.location.query={query}"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform the response to match expected format
                    if data.get("success") and "results" in data and "entities" in data["results"]:
                        entities = data["results"]["entities"]
                        return {
                            "category": category,
                            "trending_items": [
                                {
                                    "name": entity.get("name", f"Trending Item {i+1}"),
                                    "description": entity.get("properties", {}).get("description", f"Trending item in {category or 'general'}"),
                                    "trend_score": 0.8 + (i * 0.05),
                                    "growth_rate": 0.15 + (i * 0.02),
                                    "cultural_relevance": 0.7 + (i * 0.03),
                                    "category": category or "general"
                                }
                                for i, entity in enumerate(entities[:5])
                            ],
                            "entities": entities[:5]  # Include actual entities
                        }
                    else:
                        return data
                else:
                    logger.error(f"Qloo trending items error: {response.status_code} - {response.text}")
                    return self._get_mock_trending_items(category)
                    
        except Exception as e:
            logger.error(f"Qloo trending items failed: {str(e)}")
            return self._get_mock_trending_items(category)
    
    # Mock data methods for when API is unavailable
    def _get_mock_taste_insights(self, topic: str) -> Dict[str, Any]:
        return self._get_topic_specific_insights(topic)
    
    def _get_topic_specific_insights(self, topic: str) -> Dict[str, Any]:
        """Get topic-specific insights based on the search term"""
        topic_lower = topic.lower()
        
        # AI and Technology related topics
        if "ai" in topic_lower or "artificial intelligence" in topic_lower:
            if "entertainment" in topic_lower or "media" in topic_lower:
                return {
                    "topic": topic,
                    "taste_score": 0.88,
                    "cultural_relevance": 0.92,
                    "related_topics": ["AI Content Creation", "Deep Learning", "Machine Learning"],
                    "demographics": {"18-25": 0.4, "26-35": 0.45, "36-45": 0.12, "45+": 0.03},
                    "geographic_distribution": {"US": 0.45, "EU": 0.25, "Asia": 0.25, "Other": 0.05},
                    "trending": True,
                    "growth_rate": 0.25,
                    "entities": [
                        {"name": "AI Content Creation", "properties": {"description": "AI-powered content generation for entertainment"}},
                        {"name": "Deep Learning", "properties": {"description": "Advanced AI algorithms for media processing"}},
                        {"name": "Machine Learning", "properties": {"description": "Automated learning systems for entertainment"}},
                        {"name": "Neural Networks", "properties": {"description": "AI systems mimicking human brain function"}},
                        {"name": "Computer Vision", "properties": {"description": "AI technology for visual content analysis"}}
                    ]
                }
            else:
                return {
                    "topic": topic,
                    "taste_score": 0.85,
                    "cultural_relevance": 0.89,
                    "related_topics": ["Machine Learning", "Deep Learning", "Neural Networks"],
                    "demographics": {"18-25": 0.35, "26-35": 0.42, "36-45": 0.18, "45+": 0.05},
                    "geographic_distribution": {"US": 0.42, "EU": 0.28, "Asia": 0.25, "Other": 0.05},
                    "trending": True,
                    "growth_rate": 0.22,
                    "entities": [
                        {"name": "Machine Learning", "properties": {"description": "AI systems that learn from data"}},
                        {"name": "Deep Learning", "properties": {"description": "Advanced neural network architectures"}},
                        {"name": "Neural Networks", "properties": {"description": "AI systems inspired by human brain"}},
                        {"name": "Data Science", "properties": {"description": "Scientific approach to data analysis"}},
                        {"name": "Automation", "properties": {"description": "AI-powered process automation"}}
                    ]
                }
        
        # Fashion related topics
        elif "fashion" in topic_lower or "clothing" in topic_lower:
            return {
                "topic": topic,
                "taste_score": 0.82,
                "cultural_relevance": 0.85,
                "related_topics": ["Sustainable Fashion", "Digital Fashion", "Fast Fashion"],
                "demographics": {"18-25": 0.45, "26-35": 0.35, "36-45": 0.15, "45+": 0.05},
                "geographic_distribution": {"US": 0.35, "EU": 0.30, "Asia": 0.30, "Other": 0.05},
                "trending": True,
                "growth_rate": 0.18,
                "entities": [
                    {"name": "Sustainable Fashion", "properties": {"description": "Environmentally conscious clothing design"}},
                    {"name": "Digital Fashion", "properties": {"description": "Virtual and augmented reality fashion"}},
                    {"name": "Fast Fashion", "properties": {"description": "Quick-turnaround fashion trends"}},
                    {"name": "Vintage Clothing", "properties": {"description": "Retro and classic fashion styles"}},
                    {"name": "Streetwear", "properties": {"description": "Casual urban fashion culture"}}
                ]
            }
        
        # Entertainment and Media topics
        elif "entertainment" in topic_lower or "media" in topic_lower:
            return {
                "topic": topic,
                "taste_score": 0.87,
                "cultural_relevance": 0.90,
                "related_topics": ["Streaming Services", "Social Media", "Content Creation"],
                "demographics": {"18-25": 0.50, "26-35": 0.35, "36-45": 0.12, "45+": 0.03},
                "geographic_distribution": {"US": 0.40, "EU": 0.25, "Asia": 0.30, "Other": 0.05},
                "trending": True,
                "growth_rate": 0.20,
                "entities": [
                    {"name": "Streaming Services", "properties": {"description": "Digital content delivery platforms"}},
                    {"name": "Social Media", "properties": {"description": "Online social networking platforms"}},
                    {"name": "Content Creation", "properties": {"description": "User-generated media content"}},
                    {"name": "Gaming", "properties": {"description": "Interactive entertainment industry"}},
                    {"name": "Podcasts", "properties": {"description": "Digital audio content series"}}
                ]
            }
        
        # Food and Culinary topics
        elif "food" in topic_lower or "cuisine" in topic_lower:
            return {
                "topic": topic,
                "taste_score": 0.84,
                "cultural_relevance": 0.88,
                "related_topics": ["Plant-Based", "Fusion Cuisine", "Food Technology"],
                "demographics": {"18-25": 0.30, "26-35": 0.40, "36-45": 0.25, "45+": 0.05},
                "geographic_distribution": {"US": 0.35, "EU": 0.30, "Asia": 0.30, "Other": 0.05},
                "trending": True,
                "growth_rate": 0.16,
                "entities": [
                    {"name": "Plant-Based", "properties": {"description": "Vegetarian and vegan food options"}},
                    {"name": "Fusion Cuisine", "properties": {"description": "Combination of different culinary traditions"}},
                    {"name": "Food Technology", "properties": {"description": "Innovation in food production and delivery"}},
                    {"name": "Farm-to-Table", "properties": {"description": "Direct sourcing from local farms"}},
                    {"name": "Molecular Gastronomy", "properties": {"description": "Scientific approach to cooking"}}
                ]
            }
        
        # Default for other topics
        else:
            return {
                "topic": topic,
                "taste_score": 0.75,
                "cultural_relevance": 0.80,
                "related_topics": ["Digital Transformation", "Innovation", "Cultural Trends"],
                "demographics": {"18-25": 0.35, "26-35": 0.40, "36-45": 0.20, "45+": 0.05},
                "geographic_distribution": {"US": 0.40, "EU": 0.30, "Asia": 0.25, "Other": 0.05},
                "trending": True,
                "growth_rate": 0.15,
                "entities": [
                    {"name": "Digital Transformation", "properties": {"description": "Technology-driven change in industries"}},
                    {"name": "Innovation", "properties": {"description": "Creative solutions and new approaches"}},
                    {"name": "Cultural Trends", "properties": {"description": "Evolving social and cultural patterns"}},
                    {"name": "Sustainability", "properties": {"description": "Environmentally conscious practices"}},
                    {"name": "Globalization", "properties": {"description": "Worldwide interconnectedness"}}
                ]
            }
    
    def _optimize_query_for_topic(self, topic: str) -> str:
        """Optimize the query for better Qloo API results"""
        topic_lower = topic.lower()
        
        # For AI/tech topics, try to get more specific entities
        if "ai" in topic_lower or "artificial intelligence" in topic_lower:
            if "entertainment" in topic_lower or "media" in topic_lower:
                return "AI entertainment technology"
            else:
                return "artificial intelligence technology"
        
        # For fashion topics
        elif "fashion" in topic_lower:
            return "fashion industry"
        
        # For entertainment topics
        elif "entertainment" in topic_lower or "media" in topic_lower:
            return "entertainment industry"
        
        # For food topics
        elif "food" in topic_lower or "cuisine" in topic_lower:
            return "food industry"
        
        # Default: return the original topic
        return topic
    
    def _are_entities_relevant(self, topic: str, entities: List[Dict[str, Any]]) -> bool:
        """Check if the returned entities are relevant to the search topic"""
        if not entities:
            return False
        
        topic_lower = topic.lower()
        
        # For AI topics, check if entities contain AI-related terms
        if "ai" in topic_lower or "artificial intelligence" in topic_lower:
            ai_keywords = ["ai", "artificial", "intelligence", "machine", "learning", "neural", "deep", "tech", "technology"]
            for entity in entities[:3]:  # Check first 3 entities
                entity_name = entity.get("name", "").lower()
                if any(keyword in entity_name for keyword in ai_keywords):
                    return True
            return False
        
        # For entertainment topics
        elif "entertainment" in topic_lower or "media" in topic_lower:
            entertainment_keywords = ["entertainment", "media", "streaming", "content", "gaming", "podcast", "social"]
            for entity in entities[:3]:
                entity_name = entity.get("name", "").lower()
                if any(keyword in entity_name for keyword in entertainment_keywords):
                    return True
            return False
        
        # For fashion topics
        elif "fashion" in topic_lower:
            fashion_keywords = ["fashion", "clothing", "style", "design", "wear", "apparel"]
            for entity in entities[:3]:
                entity_name = entity.get("name", "").lower()
                if any(keyword in entity_name for keyword in fashion_keywords):
                    return True
            return False
        
        # For other topics, be more lenient
        return True
    
    def _get_mock_historical_data(self, topic: str) -> Dict[str, Any]:
        return {
            "topic": topic,
            "historical_trends": [
                {"month": "2024-01", "score": 0.6},
                {"month": "2024-02", "score": 0.65},
                {"month": "2024-03", "score": 0.7}
            ],
            "seasonal_patterns": ["spring_peak", "summer_dip"],
            "growth_trajectory": "increasing"
        }
    
    def _get_mock_user_preferences(self, user_id: int) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "preferences": {
                "music": ["jazz", "classical"],
                "food": ["italian", "japanese"],
                "fashion": ["minimalist", "sustainable"],
                "travel": ["cultural", "adventure"]
            },
            "cultural_affinities": ["european", "asian"],
            "taste_profile": "sophisticated"
        }
    
    def _get_mock_cultural_insights(self, text: str) -> Dict[str, Any]:
        return {
            "cultural_elements": ["element1", "element2"],
            "cultural_significance": "High cultural value",
            "historical_context": "Rich historical background",
            "cross_cultural_appeal": "Universal appeal",
            "cultural_sensitivity": "high"
        }
    
    def _get_mock_cultural_context(self, topic: str) -> Dict[str, Any]:
        return {
            "topic": topic,
            "origin": "Various origins",
            "historical_significance": "Significant historical value",
            "geographic_spread": ["region1", "region2"],
            "cultural_evolution": "Evolving cultural significance"
        }
    
    def _get_mock_user_cultural_insights(self, user_id: int) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "top_interests": ["interest1", "interest2"],
            "taste_evolution": "Evolving",
            "cultural_affinities": ["affinity1", "affinity2"],
            "learning_patterns": ["pattern1", "pattern2"],
            "exposure_score": 0.7,
            "diversity_index": 0.6
        }
    
    def _get_mock_user_cultural_preferences(self, user_id: int) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "cultural_preferences": ["preference1", "preference2"],
            "cultural_affinities": ["affinity1", "affinity2"],
            "cultural_exposure": 0.7
        }
    
    def _get_mock_food_cultural_context(self, food_name: str) -> Dict[str, Any]:
        return {
            "food_name": food_name,
            "origin": "Various origins",
            "cultural_significance": "High cultural value",
            "traditional_occasions": ["occasion1", "occasion2"],
            "preparation_methods": ["method1", "method2"]
        }
    
    def _get_mock_nutritional_info(self, food_name: str) -> Dict[str, Any]:
        return {
            "food_name": food_name,
            "calories": 250,
            "protein": 10,
            "carbs": 30,
            "fat": 8,
            "health_benefits": ["benefit1", "benefit2"],
            "allergens": ["allergen1", "allergen2"],
            "overall_score": 0.8
        }
    
    def _get_mock_destination_cultural_insights(self, destination: str) -> Dict[str, Any]:
        return {
            "destination": destination,
            "cultural_customs": ["custom1", "custom2"],
            "traditions": ["tradition1", "tradition2"],
            "cultural_significance": "High cultural value",
            "local_practices": ["practice1", "practice2"]
        }
    
    def _get_mock_travel_recommendations(self, destination: str, travel_style: str, cultural_interests: List[str]) -> Dict[str, Any]:
        return {
            "destination": destination,
            "travel_style": travel_style,
            "cultural_interests": cultural_interests,
            "recommendations": [
                {"type": "activity", "name": "Cultural Activity", "description": "Cultural activity description"},
                {"type": "accommodation", "name": "Cultural Hotel", "description": "Cultural hotel description"}
            ]
        }
    
    def _get_mock_cultural_events(self, destination: str) -> Dict[str, Any]:
        return {
            "destination": destination,
            "events": [
                {"name": "Cultural Event", "date": "2024-01-01", "description": "Event description"}
            ]
        }
    
    def _get_mock_local_guides(self, destination: str) -> Dict[str, Any]:
        return {
            "destination": destination,
            "guides": [
                {"name": "Local Guide", "specialization": "Cultural History", "rating": 4.8}
            ]
        }
    
    def _get_mock_cultural_data(self, cultural_interests: List[str], cultural_background: str = None, preferred_cultures: List[str] = None) -> Dict[str, Any]:
        return {
            "cultural_interests": cultural_interests,
            "cultural_background": cultural_background,
            "preferred_cultures": preferred_cultures,
            "insights": ["insight1", "insight2"]
        }
    
    def _get_mock_trending_items(self, category: str = None) -> Dict[str, Any]:
        return {
            "category": category,
            "trending_items": [
                {"name": "Trending Item", "trend_score": 0.9, "category": category or "general"}
            ]
        }
    
    # Food-specific helper methods
    def _get_food_related_location(self, food_name: str) -> str:
        """Get a location related to the food for Qloo API queries"""
        food_name_lower = food_name.lower()
        
        # Map food types to related locations
        if any(word in food_name_lower for word in ['pizza', 'pasta', 'italian']):
            return 'Italy'
        elif any(word in food_name_lower for word in ['sushi', 'ramen', 'japanese']):
            return 'Japan'
        elif any(word in food_name_lower for word in ['taco', 'burrito', 'mexican']):
            return 'Mexico'
        elif any(word in food_name_lower for word in ['curry', 'naan', 'indian']):
            return 'India'
        elif any(word in food_name_lower for word in ['croissant', 'baguette', 'french']):
            return 'France'
        elif any(word in food_name_lower for word in ['cheese', 'dairy']):
            return 'Switzerland'
        elif any(word in food_name_lower for word in ['rice', 'asian']):
            return 'China'
        else:
            return 'New York'  # Default to a food-friendly city
    
    def _get_food_origin(self, food_name: str) -> str:
        """Get the origin of a food item"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['pizza', 'pasta']):
            return 'Italy'
        elif any(word in food_name_lower for word in ['sushi', 'ramen']):
            return 'Japan'
        elif any(word in food_name_lower for word in ['taco', 'burrito']):
            return 'Mexico'
        elif any(word in food_name_lower for word in ['curry', 'naan']):
            return 'India'
        elif any(word in food_name_lower for word in ['croissant', 'baguette']):
            return 'France'
        else:
            return 'Various origins'
    
    def _get_food_occasions(self, food_name: str) -> List[str]:
        """Get traditional occasions for a food item"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['pizza']):
            return ['Family gatherings', 'Casual dining', 'Parties']
        elif any(word in food_name_lower for word in ['sushi']):
            return ['Special occasions', 'Business meetings', 'Celebrations']
        elif any(word in food_name_lower for word in ['curry']):
            return ['Family meals', 'Festivals', 'Daily dining']
        else:
            return ['Various occasions', 'Daily meals']
    
    def _get_food_preparation_methods(self, food_name: str) -> List[str]:
        """Get preparation methods for a food item"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['pizza']):
            return ['Baking', 'Grilling', 'Wood-fired cooking']
        elif any(word in food_name_lower for word in ['sushi']):
            return ['Raw preparation', 'Rice cooking', 'Rolling']
        elif any(word in food_name_lower for word in ['curry']):
            return ['Slow cooking', 'Spice blending', 'Simmering']
        else:
            return ['Various methods', 'Traditional preparation']
    
    def _get_food_calories(self, food_name: str) -> int:
        """Get estimated calories for a food item"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['pizza']):
            return 300
        elif any(word in food_name_lower for word in ['sushi']):
            return 200
        elif any(word in food_name_lower for word in ['curry']):
            return 250
        elif any(word in food_name_lower for word in ['cheese']):
            return 400
        else:
            return 250
    
    def _get_food_protein(self, food_name: str) -> float:
        """Get estimated protein content for a food item"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['cheese', 'dairy']):
            return 25.0
        elif any(word in food_name_lower for word in ['meat', 'chicken']):
            return 30.0
        elif any(word in food_name_lower for word in ['fish', 'sushi']):
            return 20.0
        else:
            return 12.0
    
    def _get_food_carbs(self, food_name: str) -> float:
        """Get estimated carbs content for a food item"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['pizza', 'pasta']):
            return 45.0
        elif any(word in food_name_lower for word in ['rice']):
            return 50.0
        elif any(word in food_name_lower for word in ['bread']):
            return 40.0
        else:
            return 30.0
    
    def _get_food_fat(self, food_name: str) -> float:
        """Get estimated fat content for a food item"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['cheese', 'dairy']):
            return 30.0
        elif any(word in food_name_lower for word in ['pizza']):
            return 15.0
        else:
            return 10.0
    
    def _get_food_fiber(self, food_name: str) -> float:
        """Get estimated fiber content for a food item"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['vegetables', 'salad']):
            return 8.0
        elif any(word in food_name_lower for word in ['whole grain']):
            return 6.0
        else:
            return 3.0
    
    def _get_food_sugar(self, food_name: str) -> float:
        """Get estimated sugar content for a food item"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['dessert', 'cake']):
            return 25.0
        elif any(word in food_name_lower for word in ['fruit']):
            return 15.0
        else:
            return 5.0
    
    def _get_food_sodium(self, food_name: str) -> int:
        """Get estimated sodium content for a food item"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['processed', 'canned']):
            return 800
        elif any(word in food_name_lower for word in ['cheese']):
            return 600
        else:
            return 300
    
    def _get_food_allergens(self, food_name: str) -> List[str]:
        """Get potential allergens for a food item"""
        food_name_lower = food_name.lower()
        
        allergens = []
        if any(word in food_name_lower for word in ['wheat', 'bread', 'pasta', 'pizza']):
            allergens.append('gluten')
        if any(word in food_name_lower for word in ['cheese', 'milk', 'dairy']):
            allergens.append('dairy')
        if any(word in food_name_lower for word in ['nuts', 'peanut']):
            allergens.append('nuts')
        if any(word in food_name_lower for word in ['shellfish', 'shrimp']):
            allergens.append('shellfish')
        
        return allergens if allergens else ['None detected']
    
    def _get_food_health_benefits(self, food_name: str) -> List[str]:
        """Get health benefits for a food item"""
        food_name_lower = food_name.lower()
        
        benefits = []
        if any(word in food_name_lower for word in ['vegetables', 'salad']):
            benefits.extend(['Rich in vitamins', 'High in fiber', 'Low in calories'])
        elif any(word in food_name_lower for word in ['fish', 'sushi']):
            benefits.extend(['Rich in omega-3', 'High in protein', 'Heart healthy'])
        elif any(word in food_name_lower for word in ['cheese', 'dairy']):
            benefits.extend(['High in calcium', 'Good source of protein'])
        else:
            benefits.extend(['Nutritious', 'Provides energy'])
        
        return benefits 