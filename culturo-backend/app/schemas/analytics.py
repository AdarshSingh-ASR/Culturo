from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class EventTypeEnum(str, Enum):
    feature_use = "feature_use"
    page_view = "page_view"
    user_interaction = "user_interaction"
    error = "error"
    performance = "performance"
    conversion = "conversion"

class AnalyticsEvent(BaseModel):
    event_type: EventTypeEnum
    event_data: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None  # Changed to string to match Prisma schema
    session_id: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    page_url: Optional[str] = None
    referrer: Optional[str] = None

class AnalyticsEventCreate(BaseModel):
    event_type: EventTypeEnum
    event_data: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None  # Changed to string to match Prisma schema
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    page_url: Optional[str] = None
    referrer: Optional[str] = None

class UserProfile(BaseModel):
    total_sessions: int
    total_requests: int
    engagement_score: float
    cultural_profile: str
    feature_usage: Dict[str, int]
    average_session_duration: float
    last_active: datetime
    account_age_days: int

class FeatureUsage(BaseModel):
    feature_name: str
    usage_count: int
    last_used: datetime
    average_rating: Optional[float] = None
    success_rate: float
    cultural_relevance_score: float

class CulturalInsight(BaseModel):
    top_interests: List[str]
    taste_evolution: str
    cultural_affinities: List[str]
    learning_patterns: List[str]
    cultural_exposure_score: float
    diversity_index: float

class UserAnalyticsResponse(BaseModel):
    user_id: str  # Changed to string to match Prisma schema
    user_profile: UserProfile
    feature_usage: List[FeatureUsage]
    cultural_insights: CulturalInsight
    recommendations_performance: Dict[str, float]
    engagement_trends: List[Dict[str, Any]]
    response_date: datetime

class SystemAnalytics(BaseModel):
    total_users: int
    active_users: int
    total_requests: int
    average_response_time: float
    error_rate: float
    feature_popularity: Dict[str, int]
    cultural_insights_generated: int
    recommendations_delivered: int

class SystemAnalyticsResponse(BaseModel):
    timeframe: str
    analytics: SystemAnalytics
    top_features: List[str]
    performance_metrics: Dict[str, float]
    cultural_trends: List[str]
    system_health: Dict[str, Any]
    response_date: datetime

class PerformanceMetrics(BaseModel):
    endpoint: str
    average_response_time: float
    request_count: int
    error_count: int
    success_rate: float
    p95_response_time: float
    p99_response_time: float

class PerformanceAnalyticsResponse(BaseModel):
    timeframe: str
    metrics: List[PerformanceMetrics]
    overall_performance: Dict[str, float]
    slowest_endpoints: List[str]
    error_patterns: List[Dict[str, Any]]
    optimization_suggestions: List[str]
    response_date: datetime

class CulturalTrend(BaseModel):
    trend_name: str
    category: str
    growth_rate: float
    user_engagement: float
    cultural_significance: float
    geographic_distribution: Dict[str, float]
    demographic_breakdown: Dict[str, float]

class CulturalTrendsResponse(BaseModel):
    timeframe: str
    trends: List[CulturalTrend]
    insights: List[str]
    predictions: List[str]
    cultural_impact_assessment: Dict[str, Any]
    response_date: datetime

class UserBehavior(BaseModel):
    user_id: str  # Changed to string to match Prisma schema
    session_patterns: List[Dict[str, Any]]
    feature_adoption: Dict[str, Any]
    cultural_exploration: Dict[str, Any]
    engagement_patterns: Dict[str, Any]
    conversion_funnel: Dict[str, Any]

class UserBehaviorResponse(BaseModel):
    user_id: str  # Changed to string to match Prisma schema
    behavior: UserBehavior
    insights: List[str]
    recommendations: List[str]
    response_date: datetime

class ConversionAnalytics(BaseModel):
    conversion_type: str
    conversion_rate: float
    funnel_stages: List[Dict[str, Any]]
    drop_off_points: List[Dict[str, Any]]
    conversion_factors: List[str]
    cultural_influences: List[str]

class ConversionAnalyticsResponse(BaseModel):
    timeframe: str
    conversions: List[ConversionAnalytics]
    overall_conversion_rate: float
    top_conversion_paths: List[str]
    optimization_opportunities: List[str]
    response_date: datetime

class ErrorAnalytics(BaseModel):
    error_type: str
    error_count: int
    affected_users: int
    impact_score: float
    resolution_time: Optional[float] = None
    error_context: Dict[str, Any]

class ErrorAnalyticsResponse(BaseModel):
    timeframe: str
    errors: List[ErrorAnalytics]
    total_errors: int
    error_rate: float
    critical_errors: List[str]
    resolution_priorities: List[str]
    response_date: datetime

class ABTestResult(BaseModel):
    test_name: str
    variant: str
    conversion_rate: float
    engagement_rate: float
    cultural_relevance_score: float
    statistical_significance: float
    confidence_interval: List[float]

class ABTestResponse(BaseModel):
    test_name: str
    results: List[ABTestResult]
    winner: Optional[str] = None
    insights: List[str]
    recommendations: List[str]
    response_date: datetime

class RetentionAnalytics(BaseModel):
    cohort_period: str
    retention_rates: Dict[str, float]
    cultural_factors: List[str]
    engagement_correlation: Dict[str, float]
    churn_predictors: List[str]

class RetentionAnalyticsResponse(BaseModel):
    timeframe: str
    retention: RetentionAnalytics
    insights: List[str]
    improvement_suggestions: List[str]
    response_date: datetime

class CulturalImpact(BaseModel):
    metric_name: str
    cultural_dimension: str
    impact_score: float
    confidence_level: float
    supporting_evidence: List[str]
    recommendations: List[str]

class CulturalImpactResponse(BaseModel):
    timeframe: str
    impacts: List[CulturalImpact]
    overall_cultural_impact: float
    key_insights: List[str]
    strategic_recommendations: List[str]
    response_date: datetime

class AnalyticsExport(BaseModel):
    export_type: str  # user_analytics, system_analytics, performance, etc.
    date_range: str
    format: str  # json, csv, excel
    include_metadata: bool = True

class AnalyticsExportResponse(BaseModel):
    export_url: str
    format: str
    file_size: int
    expires_at: datetime
    record_count: int 