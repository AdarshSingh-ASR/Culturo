import { useState } from 'react';
import { Sparkles, Heart, Filter, Star } from 'lucide-react';
import { apiService, handleApiError } from '../services/api';
import type { RecommendationRequest, RecommendationResponse } from '../services/api';

const Recommendations = () => {
  const [preferences, setPreferences] = useState('');
  const [category, setCategory] = useState('');
  const [movieName, setMovieName] = useState('');
  const [bookName, setBookName] = useState('');
  const [placeName, setPlaceName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [limit, setLimit] = useState(10);
  const [isLoading, setIsLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const ageOptions = [
    "24_and_younger",
    "25_to_29",
    "30_to_34",
    "35_and_younger",
    "35_to_44",
    "36_to_55",
    "45_to_54",
    "55_and_older",
  ];

  const handleGetRecommendations = async () => {
    if (!preferences.trim()) {
      setError('Please describe your preferences');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const requestData: RecommendationRequest = {
        preferences: preferences.trim(),
        category: category || undefined,
        limit: limit,
        age: age || undefined,
        gender: gender || undefined,
        movie_name: movieName || undefined,
        book_name: bookName || undefined,
        place_name: placeName || undefined
      };

      const response = await apiService.getRecommendations(requestData);
      console.log('Frontend received recommendations:', response);
      console.log('Number of items received:', response.items.length);
      console.log('Items:', response.items);
      setRecommendations(response);
      
      // Track the event
      await apiService.trackEvent({
        event_type: 'feature_use',
        event_name: 'recommendations',
        event_data: { category, item_count: response.items.length }
      });
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error('Recommendations error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="section">
      <div className="container">
        <div className="hero">
          <h1>AI-Powered Recommendations</h1>
          <p>
            Get personalized recommendations across multiple domains using Qloo's Taste AI™ 
            and advanced LLMs. Discover content that matches your cultural preferences.
          </p>
        </div>

        <div className="features-grid" style={{ gap: '2rem', marginBottom: '2rem' }}>
          <div className="card" style={{ padding: '2rem' }}>
            <h3 className="text-accent" style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Get Recommendations</h3>
            {error && (
              <div style={{ 
                padding: '0.75rem', 
                marginBottom: '1.5rem', 
                backgroundColor: '#FEE2E2', 
                border: '1px solid #FCA5A5', 
                borderRadius: '0.5rem',
                color: '#DC2626'
              }}>
                {error}
              </div>
            )}
            
            {/* General Preferences */}
            <div className="form-group" style={{ marginBottom: '1.5rem' }}>
              <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>Your Preferences</label>
              <textarea
                className="form-input"
                placeholder="Describe what you like: movies, music, books, etc."
                value={preferences}
                onChange={(e) => setPreferences(e.target.value)}
                rows={3}
                disabled={isLoading}
                style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
              />
            </div>

            {/* Specific Preferences */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: '1fr 1fr', 
              gap: '1rem', 
              marginBottom: '1.5rem' 
            }}>
              <div className="form-group">
                <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>Favorite Movie</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., The Shawshank Redemption"
                  value={movieName}
                  onChange={(e) => setMovieName(e.target.value)}
                  disabled={isLoading}
                  style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
                />
              </div>
              <div className="form-group">
                <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>Favorite Book</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., To Kill a Mockingbird"
                  value={bookName}
                  onChange={(e) => setBookName(e.target.value)}
                  disabled={isLoading}
                  style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '1.5rem' }}>
              <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>Favorite Place</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Paris, Tokyo, New York"
                value={placeName}
                onChange={(e) => setPlaceName(e.target.value)}
                disabled={isLoading}
                style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
              />
            </div>

            {/* Demographics */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: '1fr 1fr 1fr', 
              gap: '1rem', 
              marginBottom: '1.5rem' 
            }}>
              <div className="form-group">
                <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>Age Range</label>
                <select
                  className="form-input"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  disabled={isLoading}
                  style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
                >
                  <option value="">Select age range</option>
                  {ageOptions.map((option) => (
                    <option key={option} value={option}>
                      {option.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>Gender</label>
                <select
                  className="form-input"
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  disabled={isLoading}
                  style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>Number of Recommendations</label>
                <select
                  className="form-input"
                  value={limit}
                  onChange={(e) => setLimit(Number(e.target.value))}
                  disabled={isLoading}
                  style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={15}>15</option>
                  <option value={20}>20</option>
                </select>
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '2rem' }}>
              <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>Category</label>
              <select
                className="form-input"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                disabled={isLoading}
                style={{ padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #d1d5db' }}
              >
                <option value="">Select Category</option>
                <option value="movies">Movies</option>
                <option value="music">Music</option>
                <option value="books">Books</option>
                <option value="food">Food & Dining</option>
                <option value="travel">Travel Destinations</option>
                <option value="fashion">Fashion</option>
                <option value="brands">Brands</option>
              </select>
            </div>
            
            <button
              className="btn btn-primary"
              onClick={handleGetRecommendations}
              disabled={isLoading || !preferences.trim()}
              style={{ 
                width: '100%', 
                padding: '0.875rem 1.5rem', 
                fontSize: '1rem',
                fontWeight: '500',
                borderRadius: '0.5rem',
                border: 'none',
                cursor: isLoading || !preferences.trim() ? 'not-allowed' : 'pointer',
                opacity: isLoading || !preferences.trim() ? 0.6 : 1
              }}
            >
              {isLoading ? (
                <>
                  <div className="spinner"></div>
                  Finding Recommendations...
                </>
              ) : (
                <>
                  <Sparkles size={18} style={{ marginRight: '0.5rem' }} />
                  Get Recommendations
                </>
              )}
            </button>
          </div>

          <div className="card" style={{ padding: '2rem' }}>
            <h3 className="text-accent" style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Recommendation Features</h3>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.25rem' }}>
              <Heart size={20} style={{ marginRight: '0.75rem', color: 'var(--accent-color)' }} />
              <span style={{ fontSize: '1rem' }}>Personalized Matching</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.25rem' }}>
              <Filter size={20} style={{ marginRight: '0.75rem', color: 'var(--accent-color)' }} />
              <span style={{ fontSize: '1rem' }}>Multi-Domain Analysis</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.25rem' }}>
              <Star size={20} style={{ marginRight: '0.75rem', color: 'var(--accent-color)' }} />
              <span style={{ fontSize: '1rem' }}>Cultural Context</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.25rem' }}>
              <Sparkles size={20} style={{ marginRight: '0.75rem', color: 'var(--accent-color)' }} />
              <span style={{ fontSize: '1rem' }}>AI-Powered Insights</span>
            </div>
          </div>
        </div>

        {recommendations && (
          <div className="section">
            <h2>Your Recommendations ({recommendations.items.length} items)</h2>
            <div className="card">
              <h3 className="text-accent">Cultural Insights</h3>
              {recommendations.cultural_insights && recommendations.cultural_insights.length > 0 ? (
                <div>
                  {recommendations.cultural_insights.map((insight, index) => (
                    <div key={index} style={{ marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#f8f9fa', borderRadius: '0.5rem' }}>
                      <h4 style={{ marginBottom: '0.5rem', color: 'var(--accent-color)' }}>
                        {insight.insight_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </h4>
                      <p style={{ marginBottom: '0.5rem' }}>{insight.description}</p>
                      <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                        <span style={{ marginRight: '1rem' }}>
                          <strong>Confidence:</strong> {(insight.confidence * 100).toFixed(0)}%
                        </span>
                        <span>
                          <strong>Cultural Relevance:</strong> {(insight.cultural_relevance * 100).toFixed(0)}%
                        </span>
                      </div>
                      {insight.supporting_evidence && insight.supporting_evidence.length > 0 && (
                        <div style={{ marginTop: '0.5rem' }}>
                          <strong>Supporting Evidence:</strong>
                          <ul style={{ marginTop: '0.25rem', marginLeft: '1.5rem' }}>
                            {insight.supporting_evidence.map((evidence, evIndex) => (
                              <li key={evIndex}>{evidence}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p>No cultural insights available.</p>
              )}
            </div>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
              gap: '1.5rem',
              marginTop: '2rem',
              width: '100%'
            }}>
              {(() => {
                console.log('Rendering recommendations.items:', recommendations.items);
                console.log('Number of items to render:', recommendations.items.length);
                console.log('Cultural insights:', recommendations.cultural_insights);
                return null;
              })()}
              {recommendations.items.map((item, index) => {
                console.log(`Rendering item ${index}:`, item.name);
                return (
                  <div key={index} className="card" style={{ 
                    padding: '1.5rem',
                    backgroundColor: 'var(--background-secondary)',
                    borderRadius: '0.75rem',
                    border: '1px solid var(--border-color)',
                    boxShadow: '0 2px 8px var(--shadow-color)'
                  }}>
                    <h4 style={{ marginBottom: '0.75rem', color: 'var(--accent-color)' }}>{item.name}</h4>
                    <p style={{ marginBottom: '0.5rem' }}><strong>Type:</strong> {item.type}</p>
                    <p style={{ marginBottom: '0.5rem' }}><strong>Rating:</strong> {item.rating}/5.0</p>
                    <p style={{ marginBottom: '0.5rem' }}><strong>Cultural Context:</strong></p>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.5' }}>{item.cultural_context}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations; 