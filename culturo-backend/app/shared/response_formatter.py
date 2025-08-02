"""
Response formatter utilities for consistent API responses
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel


class ResponseFormatter:
    """Utility class for formatting API responses"""
    
    @staticmethod
    def format_trend_analysis_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format trend analysis response to match frontend expectations"""
        return {
            "trend_data": {
                "current_trends": data.get("current_trends", []),
                "growth_rate": data.get("growth_rate", 0.0),
                "confidence_score": data.get("confidence_score", 0.0)
            },
            "audience_insights": {
                "target_demographics": data.get("target_demographics", []),
                "interests": data.get("interests", [])
            }
        }
    
    @staticmethod
    def format_story_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format story generation response to match frontend expectations"""
        return {
            "title": data.get("title", "Generated Story"),
            "summary": data.get("summary", ""),
            "plot_outline": data.get("plot_outline", ""),
            "tone_suggestions": data.get("tone_suggestions", []),
            "audience_analysis": {
                "target_demographics": data.get("target_demographics", []),
                "cultural_interests": data.get("cultural_interests", [])
            }
        }
    
    @staticmethod
    def format_food_analysis_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format food analysis response to match frontend expectations"""
        return {
            "food_name": data.get("food_name", "Unknown Food"),
            "confidence": data.get("confidence", 0.0),
            "nutrition": {
                "calories": data.get("calories", 0),
                "protein": data.get("protein", 0.0),
                "carbs": data.get("carbs", 0.0),
                "fat": data.get("fat", 0.0)
            },
            "cultural_context": data.get("cultural_context", ""),
            "recommendations": data.get("recommendations", [])
        }
    
    @staticmethod
    def format_travel_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format travel planning response to match frontend expectations"""
        # Format itinerary to match frontend structure
        formatted_itinerary = []
        for day in data.get("itinerary", []):
            formatted_day = {
                "day": day.get("day_number", 1),
                "activity": f"Day {day.get('day_number', 1)}: {day.get('theme', 'Cultural Experience')}",
                "cultural_context": ", ".join(day.get("cultural_notes", []))
            }
            formatted_itinerary.append(formatted_day)
        
        return {
            "destination": data.get("destination", ""),
            "duration": data.get("duration", "1 week"),
            "cultural_insights": data.get("cultural_insights", ""),
            "activities": formatted_itinerary
        }
    
    @staticmethod
    def format_recommendation_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format recommendation response to match frontend expectations"""
        return {
            "category": data.get("category", "general"),
            "items": [
                {
                    "name": item.get("name", ""),
                    "type": item.get("type", ""),
                    "rating": item.get("rating", 0.0),
                    "cultural_context": item.get("cultural_context", "")
                }
                for item in data.get("items", [])
            ],
            "cultural_insights": data.get("cultural_insights", "")
        }
    
    @staticmethod
    def format_analytics_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format analytics response to match frontend expectations"""
        return {
            "user_profile": {
                "total_sessions": data.get("total_sessions", 0),
                "total_requests": data.get("total_requests", 0),
                "engagement_score": data.get("engagement_score", 0.0),
                "cultural_profile": data.get("cultural_profile", "")
            },
            "feature_usage": {
                "trends": data.get("trends_usage", 0),
                "stories": data.get("stories_usage", 0),
                "food": data.get("food_usage", 0),
                "travel": data.get("travel_usage", 0),
                "recommendations": data.get("recommendations_usage", 0)
            },
            "cultural_insights": {
                "top_interests": data.get("top_interests", []),
                "taste_evolution": data.get("taste_evolution", "")
            }
        }
    
    @staticmethod
    def format_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
        """Format a generic success response"""
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def format_error_response(error: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format a generic error response"""
        return {
            "success": False,
            "error": error,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def format_paginated_response(
        items: List[Any], 
        page: int, 
        page_size: int, 
        total: int,
        message: str = "Success"
    ) -> Dict[str, Any]:
        """Format a paginated response"""
        return {
            "success": True,
            "message": message,
            "data": {
                "items": items,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size,
                    "has_next": page * page_size < total,
                    "has_prev": page > 1
                }
            },
            "timestamp": datetime.now().isoformat()
        }


# Convenience functions for common response types
def format_trend_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format trend analysis response"""
    return ResponseFormatter.format_trend_analysis_response(data)


def format_story_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format story generation response"""
    return ResponseFormatter.format_story_response(data)


def format_food_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format food analysis response"""
    return ResponseFormatter.format_food_analysis_response(data)


def format_travel_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format travel planning response"""
    return ResponseFormatter.format_travel_response(data)


def format_recommendation_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format recommendation response"""
    return ResponseFormatter.format_recommendation_response(data)


def format_analytics_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format analytics response"""
    return ResponseFormatter.format_analytics_response(data) 