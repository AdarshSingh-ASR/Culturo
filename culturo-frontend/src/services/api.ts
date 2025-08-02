import axios from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 90000, // 90 seconds - increased for travel planning
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Types for API responses

export interface StoryGenerationRequest {
  story_prompt: string;
  genre?: string;
  target_audience?: string;
}

export interface StoryGenerationResponse {
  title: string;
  summary: string;
  plot_outline: string;
  tone_suggestions: string[];
  characters: Array<{
    name: string;
    description: string;
    role: string;
    personality_traits: string[];
  }>;
  scenes: Array<{
    scene_number: number;
    title: string;
    description: string;
    setting: string;
    characters_involved: string[];
  }>;
  themes: string[];
  cultural_context: string;
  writing_style: string;
  estimated_word_count: number;
  audience_analysis: {
    target_demographics: string[];
    cultural_interests: string[];
    reading_preferences: string[];
  };
}

export interface FoodAnalysisRequest {
  food_name: string;
  cuisine_type?: string;
  include_nutrition?: boolean;
  include_cultural_context?: boolean;
  include_recommendations?: boolean;
}

export interface FoodAnalysisResponse {
  food_name: string;
  confidence_score: number;
  category: string;
  cuisine_type: string;
  nutrition: {
    calories: number;
    protein: number;
    carbohydrates: number;
    fat: number;
    fiber?: number;
    sugar?: number;
    sodium?: number;
    cholesterol?: number;
    vitamins?: Record<string, number>;
    minerals?: Record<string, number>;
  };
  cultural_context: {
    origin_country: string;
    origin_region?: string;
    historical_significance?: string;
    traditional_occasions: string[];
    cultural_symbolism?: string;
    preparation_methods: string[];
    serving_traditions: string[];
  };
  ingredients: Array<{
    name: string;
    quantity?: string;
    category: string;
    nutritional_contribution?: string;
  }>;
  recipe?: {
    title: string;
    description: string;
    ingredients: Array<{
      name: string;
      quantity?: string;
      category: string;
      nutritional_contribution?: string;
    }>;
    instructions: string[];
    cooking_time: string;
    difficulty_level: string;
    servings: number;
    cuisine_type: string;
  };
  recommendations: Array<{
    food_name: string;
    reason: string;
    similarity_score: number;
    cultural_connection?: string;
    nutritional_benefit?: string;
  }>;
  health_benefits: string[];
  dietary_restrictions: string[];
  allergens: string[];
  analysis_date: string;
}

export interface TravelPlanningRequest {
  destination: string;
  travel_style?: string;
  duration?: string;
  group_size?: number;
  budget_level?: string;
  cultural_interests?: string[];
}

export interface TravelPlanningResponse {
  destination: string;
  duration: string;
  travel_style: string;
  budget_estimate: string;
  cultural_insights: string;
  itinerary: Array<{
    day: number;
    activity: string;
    cultural_context: string;
    places?: Array<{
      name: string;
      properties?: {
        address?: string;
        website?: string;
        phone?: string;
        business_rating?: number;
        description?: string;
      };
    }>;
    morning_activity?: string;
    afternoon_activity?: string;
    evening_activity?: string;
  }>;
  local_experiences: Array<{
    name: string;
    description: string;
    cultural_value: number;
    duration: string;
    cost: string;
    location: string;
    local_contact?: string;
    cultural_context: string;
  }>;
  accommodation_recommendations: Array<{
    name: string;
    type: string;
    description: string;
    cultural_authenticity: number;
    price_range: string;
    location: string;
    amenities: string[];
    cultural_features: string[];
  }>;
  cultural_activities: Array<{
    name: string;
    description: string;
    cultural_significance: string;
    duration: string;
    cost_range: string;
    location: string;
    best_time: string;
    difficulty_level: string;
    cultural_insights: string[];
  }>;
  practical_information: Record<string, any>;
  safety_considerations: string[];
  cultural_etiquette: string[];
  planning_date: string;
  llm_summary?: string;
  qloo_places?: Array<{
    name: string;
    properties?: {
      address?: string;
      website?: string;
      phone?: string;
      business_rating?: number;
      description?: string;
    };
  }>;
}

export interface RecommendationRequest {
  preferences: string;
  category?: string;
  limit?: number;
  age?: string;
  gender?: string;
  movie_name?: string;
  book_name?: string;
  place_name?: string;
}

export interface RecommendationResponse {
  category: string;
  items: Array<{
    name: string;
    type: string;
    rating: number;
    cultural_context: string;
  }>;
  cultural_insights: Array<{
    insight_type: string;
    description: string;
    confidence: number;
    supporting_evidence: string[];
    cultural_relevance: number;
  }>;
  recommendation_reasoning?: string[];
  user_preference_summary?: string;
  cultural_profile?: Record<string, number>;
  recommendation_date?: string;
}

export interface AnalyticsResponse {
  user_profile: {
    total_sessions: number;
    total_requests: number;
    engagement_score: number;
    cultural_profile: string;
  };
  feature_usage: {
    stories: number;
    food: number;
    travel: number;
    recommendations: number;
  };
  cultural_insights: {
    top_interests: string[];
    taste_evolution: string;
  };
}

// API Service Functions
export const apiService = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Authentication
  login: async (email: string, password: string) => {
    const response = await api.post('/api/v1/auth/login', { email, password });
    return response.data;
  },

  register: async (userData: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }) => {
    const response = await api.post('/api/v1/auth/register', userData);
    return response.data;
  },

  // Story Development
  generateStory: async (data: StoryGenerationRequest): Promise<StoryGenerationResponse> => {
    const response = await api.post('/api/v1/stories/generate', data);
    return response.data;
  },

  analyzeStory: async (storyPrompt: string) => {
    const response = await api.post('/api/v1/stories/analyze', { story_prompt: storyPrompt });
    return response.data;
  },

  getRandomStory: async () => {
    const response = await api.post('/api/v1/stories/surprise');
    return response.data;
  },

  // Food Analysis
  analyzeFood: async (data: FoodAnalysisRequest): Promise<FoodAnalysisResponse> => {
    const response = await api.post('/api/v1/food/analyze', data);
    return response.data;
  },

  getFoodRecommendations: async (preferences: string) => {
    const response = await api.post('/api/v1/food/recommendations', { preferences });
    return response.data;
  },

  // Travel Planning
  planTravel: async (data: TravelPlanningRequest): Promise<TravelPlanningResponse> => {
    const response = await api.post('/api/v1/travel/plan', data, {
      timeout: 90000, // 90 seconds for travel planning
    });
    return response.data;
  },

  getDestinations: async (interests: string[]) => {
    const response = await api.post('/api/v1/travel/destinations', { interests });
    return response.data;
  },

  getCulturalInsights: async (destination: string) => {
    const response = await api.post('/api/v1/travel/cultural-insights', { destination });
    return response.data;
  },

  // Recommendations
  getRecommendations: async (data: RecommendationRequest): Promise<RecommendationResponse> => {
    const response = await api.post('/api/v1/recommendations/personalized', data);
    return response.data;
  },

  getCulturalRecommendations: async (preferences: string) => {
    const response = await api.post('/api/v1/recommendations/cultural', { preferences });
    return response.data;
  },

  getTrendingItems: async () => {
    const response = await api.get('/api/v1/recommendations/trending');
    return response.data;
  },

  // Analytics
  getUserAnalytics: async (): Promise<AnalyticsResponse> => {
    const response = await api.get('/api/v1/analytics/user');
    return response.data;
  },

  trackEvent: async (eventData: {
    event_type: string;
    event_name: string;
    event_data?: any;
  }) => {
    const response = await api.post('/api/v1/analytics/events', eventData);
    return response.data;
  },

  // User Profile
  getUserProfile: async () => {
    const response = await api.get('/api/v1/auth/profile');
    return response.data;
  },

  updateUserPreferences: async (preferences: {
    music_preferences?: string[];
    food_preferences?: string[];
    fashion_preferences?: string[];
    book_preferences?: string[];
    movie_preferences?: string[];
    travel_preferences?: string[];
  }) => {
    const response = await api.put('/api/v1/auth/preferences', preferences);
    return response.data;
  },
};

// Error handling utility
export const handleApiError = (error: any): string => {
  // Handle timeout errors specifically
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return 'Request timed out. The travel planning service is taking longer than expected. Please try again.';
  }
  
  // Handle network errors
  if (error.code === 'NETWORK_ERROR' || !error.response) {
    return 'Network error. Please check your connection and try again.';
  }
  
  // Handle specific HTTP errors
  if (error.response?.status === 408) {
    return 'Request timeout - the operation took too long to complete. Please try again.';
  }
  
  if (error.response?.status === 500) {
    return 'Server error. Please try again later.';
  }
  
  if (error.response?.status === 503) {
    return 'Service temporarily unavailable. Please try again later.';
  }
  
  // Handle response data errors
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  // Handle general error messages
  if (error.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred. Please try again.';
};

export default apiService; 