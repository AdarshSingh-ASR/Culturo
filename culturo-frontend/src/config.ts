// Frontend Configuration
export const config = {
  // API Configuration
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  API_TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  
  // Feature Flags
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS !== 'false',
  ENABLE_AUTH: import.meta.env.VITE_ENABLE_AUTH !== 'false',
  ENABLE_FILE_UPLOAD: import.meta.env.VITE_ENABLE_FILE_UPLOAD !== 'false',
  
  // Environment
  ENV: import.meta.env.VITE_ENV || 'development',
  IS_DEVELOPMENT: import.meta.env.DEV,
  IS_PRODUCTION: import.meta.env.PROD,
  
  // App Configuration
  APP_NAME: 'Culturo',
  APP_VERSION: '1.0.0',
  
  // File Upload Limits
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  
  // Pagination
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  
  // Cache Configuration
  CACHE_TTL: 5 * 60 * 1000, // 5 minutes
  
  // Error Messages
  ERROR_MESSAGES: {
    NETWORK_ERROR: 'Network error. Please check your connection.',
    SERVER_ERROR: 'Server error. Please try again later.',
    VALIDATION_ERROR: 'Please check your input and try again.',
    UNAUTHORIZED: 'You are not authorized to perform this action.',
    NOT_FOUND: 'The requested resource was not found.',
    TIMEOUT: 'Request timed out. Please try again.',
    FILE_TOO_LARGE: 'File is too large. Maximum size is 10MB.',
    INVALID_FILE_TYPE: 'Invalid file type. Please upload an image.',
  },
  
  // Success Messages
  SUCCESS_MESSAGES: {
    ANALYSIS_COMPLETE: 'Analysis completed successfully!',
    STORY_GENERATED: 'Story generated successfully!',
    RECOMMENDATIONS_READY: 'Recommendations are ready!',
    TRAVEL_PLANNED: 'Travel itinerary created!',
    FOOD_ANALYZED: 'Food analysis completed!',
    PROFILE_UPDATED: 'Profile updated successfully!',
  },
};

export default config; 