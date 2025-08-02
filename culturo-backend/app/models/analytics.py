"""
Analytics model for tracking user behavior and generating insights
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Integer, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class UserAnalytics(Base):
    """User behavior analytics and insights"""
    
    __tablename__ = "user_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Usage statistics
    total_sessions = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    last_active = Column(DateTime(timezone=True))
    
    # Feature usage
    feature_usage = Column(JSON, default=dict)  # {feature: count}
    preferred_features = Column(JSON, default=list)
    
    # Cultural insights
    cultural_profile = Column(JSON, default=dict)
    taste_evolution = Column(JSON, default=list)
    recommendation_accuracy = Column(Float, default=0.0)
    
    # Engagement metrics
    engagement_score = Column(Float, default=0.0)
    retention_rate = Column(Float, default=0.0)
    satisfaction_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analytics")
    events = relationship("AnalyticsEvent", back_populates="analytics", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert analytics to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "total_sessions": self.total_sessions,
            "total_requests": self.total_requests,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "feature_usage": self.feature_usage,
            "preferred_features": self.preferred_features,
            "cultural_profile": self.cultural_profile,
            "taste_evolution": self.taste_evolution,
            "recommendation_accuracy": self.recommendation_accuracy,
            "engagement_score": self.engagement_score,
            "retention_rate": self.retention_rate,
            "satisfaction_score": self.satisfaction_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AnalyticsEvent(Base):
    """Individual analytics events"""
    
    __tablename__ = "analytics_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analytics_id = Column(UUID(as_uuid=True), ForeignKey("user_analytics.id"), nullable=False)
    
    # Event details
    event_type = Column(String(100), nullable=False)  # page_view, feature_use, recommendation_click, etc.
    event_name = Column(String(255), nullable=False)
    event_data = Column(JSON, default=dict)
    
    # Context
    session_id = Column(String(255))
    page_url = Column(String(500))
    user_agent = Column(Text)
    ip_address = Column(String(45))
    
    # Performance
    response_time = Column(Float)  # milliseconds
    success = Column(String(10), default="yes")  # yes, no, partial
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analytics = relationship("UserAnalytics", back_populates="events")
    
    def to_dict(self):
        """Convert event to dictionary"""
        return {
            "id": str(self.id),
            "analytics_id": str(self.analytics_id),
            "event_type": self.event_type,
            "event_name": self.event_name,
            "event_data": self.event_data,
            "session_id": self.session_id,
            "page_url": self.page_url,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "response_time": self.response_time,
            "success": self.success,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class TrendAnalysis(Base):
    """Trend analysis and forecasting data"""
    
    __tablename__ = "trend_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Analysis details
    topic = Column(String(255), nullable=False)
    industry = Column(String(100))
    timeframe = Column(String(50))  # short_term, medium_term, long_term
    
    # Analysis results
    trend_data = Column(JSON, default=dict)
    forecast_data = Column(JSON, default=dict)
    confidence_score = Column(Float, default=0.0)
    
    # Cultural context
    cultural_factors = Column(JSON, default=list)
    audience_insights = Column(JSON, default=dict)
    market_opportunities = Column(JSON, default=list)
    
    # Metadata
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert trend analysis to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "topic": self.topic,
            "industry": self.industry,
            "timeframe": self.timeframe,
            "trend_data": self.trend_data,
            "forecast_data": self.forecast_data,
            "confidence_score": self.confidence_score,
            "cultural_factors": self.cultural_factors,
            "audience_insights": self.audience_insights,
            "market_opportunities": self.market_opportunities,
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class RecommendationLog(Base):
    """Log of recommendations given to users"""
    
    __tablename__ = "recommendation_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Recommendation details
    recommendation_type = Column(String(100), nullable=False)  # food, travel, story, trend, etc.
    recommendation_data = Column(JSON, default=dict)
    source = Column(String(100))  # qloo, llm, hybrid, etc.
    
    # User interaction
    user_feedback = Column(String(50))  # like, dislike, neutral, no_response
    click_through = Column(Boolean, default=False)
    conversion = Column(Boolean, default=False)
    
    # Performance metrics
    relevance_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    feedback_at = Column(DateTime(timezone=True))
    
    def to_dict(self):
        """Convert recommendation log to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "recommendation_type": self.recommendation_type,
            "recommendation_data": self.recommendation_data,
            "source": self.source,
            "user_feedback": self.user_feedback,
            "click_through": self.click_through,
            "conversion": self.conversion,
            "relevance_score": self.relevance_score,
            "engagement_score": self.engagement_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "feedback_at": self.feedback_at.isoformat() if self.feedback_at else None
        } 