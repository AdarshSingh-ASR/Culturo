"""
Story model for story development and creative content
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class Story(Base):
    """Story model for creative content development"""
    
    __tablename__ = "stories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    genre = Column(String(100))
    target_audience = Column(String(100))
    
    # Story content
    original_prompt = Column(Text, nullable=False)
    story_summary = Column(Text)
    plot_outline = Column(Text)
    
    # AI-generated enhancements
    tone_suggestions = Column(JSON, default=dict)
    plot_twists = Column(JSON, default=list)
    pacing_tips = Column(JSON, default=list)
    emotional_arcs = Column(JSON, default=list)
    
    # Visual and style elements
    visual_scenes = Column(JSON, default=list)
    character_styles = Column(JSON, default=list)
    mood_boards = Column(JSON, default=list)
    
    # Audience analysis
    audience_analysis = Column(JSON, default=dict)
    market_insights = Column(JSON, default=dict)
    cultural_context = Column(JSON, default=dict)
    
    # Status and metadata
    status = Column(String(50), default="draft")  # draft, in_progress, completed, published
    is_public = Column(Boolean, default=False)
    tags = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="stories")
    scenes = relationship("StoryScene", back_populates="story", cascade="all, delete-orphan")
    characters = relationship("StoryCharacter", back_populates="story", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert story to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "genre": self.genre,
            "target_audience": self.target_audience,
            "original_prompt": self.original_prompt,
            "story_summary": self.story_summary,
            "plot_outline": self.plot_outline,
            "tone_suggestions": self.tone_suggestions,
            "plot_twists": self.plot_twists,
            "pacing_tips": self.pacing_tips,
            "emotional_arcs": self.emotional_arcs,
            "visual_scenes": self.visual_scenes,
            "character_styles": self.character_styles,
            "mood_boards": self.mood_boards,
            "audience_analysis": self.audience_analysis,
            "market_insights": self.market_insights,
            "cultural_context": self.cultural_context,
            "status": self.status,
            "is_public": self.is_public,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class StoryScene(Base):
    """Individual scenes within a story"""
    
    __tablename__ = "story_scenes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id"), nullable=False)
    scene_number = Column(String(10), nullable=False)
    title = Column(String(255))
    
    # Scene content
    description = Column(Text)
    mood = Column(String(100))
    visual_style = Column(String(100))
    music_genre = Column(String(100))
    
    # Technical details
    location = Column(String(255))
    time_of_day = Column(String(50))
    weather = Column(String(50))
    
    # Cultural elements
    cultural_elements = Column(JSON, default=list)
    symbolism = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    story = relationship("Story", back_populates="scenes")
    
    def to_dict(self):
        """Convert scene to dictionary"""
        return {
            "id": str(self.id),
            "story_id": str(self.story_id),
            "scene_number": self.scene_number,
            "title": self.title,
            "description": self.description,
            "mood": self.mood,
            "visual_style": self.visual_style,
            "music_genre": self.music_genre,
            "location": self.location,
            "time_of_day": self.time_of_day,
            "weather": self.weather,
            "cultural_elements": self.cultural_elements,
            "symbolism": self.symbolism,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class StoryCharacter(Base):
    """Characters within a story"""
    
    __tablename__ = "story_characters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id"), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(100))  # protagonist, antagonist, supporting, etc.
    
    # Character details
    description = Column(Text)
    personality = Column(JSON, default=dict)
    background = Column(Text)
    
    # Style and appearance
    style_description = Column(Text)
    outfits = Column(JSON, default=list)
    physical_description = Column(Text)
    
    # Cultural elements
    cultural_background = Column(String(255))
    cultural_significance = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    story = relationship("Story", back_populates="characters")
    
    def to_dict(self):
        """Convert character to dictionary"""
        return {
            "id": str(self.id),
            "story_id": str(self.story_id),
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "personality": self.personality,
            "background": self.background,
            "style_description": self.style_description,
            "outfits": self.outfits,
            "physical_description": self.physical_description,
            "cultural_background": self.cultural_background,
            "cultural_significance": self.cultural_significance,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 