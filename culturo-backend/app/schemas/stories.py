from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class GenreEnum(str, Enum):
    drama = "drama"
    comedy = "comedy"
    romance = "romance"
    thriller = "thriller"
    fantasy = "fantasy"
    sci_fi = "sci-fi"
    historical = "historical"
    mystery = "mystery"
    horror = "horror"
    action = "action"
    adventure = "adventure"
    biography = "biography"
    documentary = "documentary"

class AudienceEnum(str, Enum):
    children = "children"  # 5-12
    teens = "teens"  # 13-17
    young_adults = "young_adults"  # 18-25
    adults = "adults"  # 25-45
    seniors = "seniors"  # 65+

class StoryGenerationRequest(BaseModel):
    story_prompt: str = Field(..., min_length=10, max_length=2000)
    genre: Optional[GenreEnum] = None
    target_audience: Optional[AudienceEnum] = None
    tone: Optional[str] = None  # serious, humorous, dark, uplifting, etc.
    length: Optional[str] = None  # short, medium, long
    include_cultural_elements: bool = True
    user_id: Optional[int] = None

class Character(BaseModel):
    name: str
    description: str
    role: str  # protagonist, antagonist, supporting
    personality_traits: List[str]
    background: str
    motivations: List[str]
    character_arc: str

class Scene(BaseModel):
    scene_number: int
    title: str
    description: str
    characters: List[str]
    setting: str
    action: str
    dialogue: Optional[str] = None
    emotional_beat: str

class StoryElement(BaseModel):
    element_type: str  # theme, symbol, motif, etc.
    name: str
    description: str
    significance: str

class AudienceAnalysis(BaseModel):
    target_demographics: List[str]
    cultural_interests: List[str]
    reading_preferences: List[str]
    engagement_factors: List[str]
    potential_appeal: float
    market_size_estimate: str

class StoryGenerationResponse(BaseModel):
    title: str
    summary: str
    plot_outline: str
    characters: List[Character]
    scenes: List[Scene]
    themes: List[StoryElement]
    tone_suggestions: List[str]
    audience_analysis: AudienceAnalysis
    cultural_context: str
    writing_style: str
    estimated_word_count: int
    generation_date: datetime

class StoryAnalysisRequest(BaseModel):
    story_prompt: str = Field(..., min_length=10, max_length=2000)
    analysis_type: str = "comprehensive"  # basic, comprehensive, detailed
    include_market_analysis: bool = True
    include_cultural_insights: bool = True
    user_id: Optional[int] = None

class StoryAnalysis(BaseModel):
    plot_strength: float
    character_development: float
    originality: float
    market_potential: float
    cultural_relevance: float
    technical_quality: float
    overall_score: float

class MarketAnalysis(BaseModel):
    target_market: str
    competition_level: str
    market_size: str
    monetization_potential: str
    distribution_channels: List[str]
    marketing_strategies: List[str]

class CulturalInsight(BaseModel):
    cultural_elements: List[str]
    cultural_sensitivity: str
    global_appeal: float
    localization_notes: List[str]
    cultural_opportunities: List[str]

class StoryAnalysisResponse(BaseModel):
    story_prompt: str
    analysis: StoryAnalysis
    market_analysis: Optional[MarketAnalysis] = None
    cultural_insights: Optional[CulturalInsight] = None
    recommendations: List[str]
    improvement_suggestions: List[str]
    analysis_date: datetime

class StoryCollaboration(BaseModel):
    id: int
    story_id: int
    user_id: int
    collaboration_type: str  # co_writer, editor, reviewer
    contribution: str
    created_at: datetime
    status: str  # active, completed, archived

class StoryCollaborationCreate(BaseModel):
    story_id: int
    user_id: int
    collaboration_type: str
    contribution: str

class StoryCollaborationResponse(BaseModel):
    id: int
    story_id: int
    user_id: int
    collaboration_type: str
    contribution: str
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

class StoryFeedback(BaseModel):
    id: int
    story_id: int
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    feedback_text: str
    feedback_type: str  # plot, character, style, overall
    created_at: datetime

class StoryFeedbackCreate(BaseModel):
    story_id: int
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    feedback_text: str
    feedback_type: str

class StoryFeedbackResponse(BaseModel):
    id: int
    story_id: int
    user_id: int
    rating: int
    feedback_text: str
    feedback_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class StoryExport(BaseModel):
    format: str  # pdf, docx, txt, epub
    include_metadata: bool = True
    include_analysis: bool = False
    include_collaborations: bool = False

class StoryExportResponse(BaseModel):
    export_url: str
    format: str
    file_size: int
    expires_at: datetime 