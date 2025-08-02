"""
Trip model for travel planning and cultural itineraries
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Integer, Float
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class Trip(Base):
    """Trip model for travel planning"""
    
    __tablename__ = "trips"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    duration_days = Column(Integer)
    
    # Trip preferences
    travel_style = Column(String(100))  # relaxing, adventurous, cultural, etc.
    budget_range = Column(String(50))   # low, medium, high
    group_size = Column(Integer, default=1)
    
    # Cultural preferences for the trip
    cultural_interests = Column(JSON, default=list)
    food_preferences = Column(JSON, default=list)
    activity_preferences = Column(JSON, default=list)
    
    # Generated content
    itinerary = Column(JSON, default=dict)
    cultural_insights = Column(JSON, default=dict)
    recommendations = Column(JSON, default=list)
    
    # Status
    status = Column(String(50), default="planning")  # planning, active, completed, cancelled
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trips")
    activities = relationship("TripActivity", back_populates="trip", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert trip to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "destination": self.destination,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "duration_days": self.duration_days,
            "travel_style": self.travel_style,
            "budget_range": self.budget_range,
            "group_size": self.group_size,
            "cultural_interests": self.cultural_interests,
            "food_preferences": self.food_preferences,
            "activity_preferences": self.activity_preferences,
            "itinerary": self.itinerary,
            "cultural_insights": self.cultural_insights,
            "recommendations": self.recommendations,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class TripActivity(Base):
    """Individual activities within a trip"""
    
    __tablename__ = "trip_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    activity_type = Column(String(100))  # food, culture, entertainment, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    start_time = Column(String(10))  # HH:MM format
    end_time = Column(String(10))    # HH:MM format
    duration_hours = Column(Float)
    
    # Cultural context
    cultural_context = Column(Text)
    local_tips = Column(Text)
    cultural_significance = Column(Text)
    
    # Additional info
    cost_estimate = Column(Float)
    booking_required = Column(String(10), default="no")  # yes, no, recommended
    weather_dependent = Column(String(10), default="no")  # yes, no
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    trip = relationship("Trip", back_populates="activities")
    
    def to_dict(self):
        """Convert activity to dictionary"""
        return {
            "id": str(self.id),
            "trip_id": str(self.trip_id),
            "day_number": self.day_number,
            "activity_type": self.activity_type,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_hours": self.duration_hours,
            "cultural_context": self.cultural_context,
            "local_tips": self.local_tips,
            "cultural_significance": self.cultural_significance,
            "cost_estimate": self.cost_estimate,
            "booking_required": self.booking_required,
            "weather_dependent": self.weather_dependent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 