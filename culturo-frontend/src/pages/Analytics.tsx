import { useState } from 'react';
import { BarChart3, Users, TrendingUp, Activity } from 'lucide-react';
import { apiService, handleApiError } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { AnalyticsResponse } from '../services/api';

const Analytics = () => {
  const { isAuthenticated, user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleLoadAnalytics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.getUserAnalytics();
      setAnalytics(response);
      
      // Track the event only if user is authenticated
      if (isAuthenticated) {
        await apiService.trackEvent({
          event_type: 'feature_use',
          event_name: 'analytics_view',
          event_data: { 
            total_sessions: response.user_profile.total_sessions,
            engagement_score: response.user_profile.engagement_score
          }
        });
      }
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error('Analytics error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="section">
      <div className="container">
        <div className="hero">
          <h1>User Analytics & Insights</h1>
          <p>
            Track your cultural journey and discover insights about your preferences, 
            behavior patterns, and cultural evolution over time.
          </p>
          {!isAuthenticated && (
            <div style={{ 
              padding: '1rem', 
              marginTop: '1rem',
              backgroundColor: '#FEF3C7', 
              border: '1px solid #F59E0B', 
              borderRadius: '0.5rem',
              color: '#92400E'
            }}>
              <strong>Demo Mode:</strong> You're viewing demo analytics. Sign in to see your personalized analytics and track your cultural journey.
            </div>
          )}
        </div>

        <div className="features-grid" style={{ gap: '2rem', marginBottom: '2rem' }}>
          <div className="card" style={{ padding: '2rem' }}>
            <h3 className="text-accent" style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Analytics Dashboard</h3>
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
            <p style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
              {isAuthenticated 
                ? `Welcome back, ${user?.username || 'User'}! View your cultural intelligence profile and usage patterns.`
                : 'View demo analytics to understand how the cultural intelligence system works.'
              }
            </p>
            <button
              className="btn btn-primary"
              onClick={handleLoadAnalytics}
              disabled={isLoading}
              style={{ 
                width: '100%', 
                padding: '0.875rem 1.5rem', 
                fontSize: '1rem',
                fontWeight: '500',
                borderRadius: '0.5rem',
                border: 'none',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.6 : 1
              }}
            >
              {isLoading ? (
                <>
                  <div className="spinner"></div>
                  Loading Analytics...
                </>
              ) : (
                <>
                  <BarChart3 size={18} style={{ marginRight: '0.5rem' }} />
                  {isAuthenticated ? 'Load My Analytics' : 'Load Demo Analytics'}
                </>
              )}
            </button>
          </div>

          <div className="card" style={{ padding: '2rem' }}>
            <h3 className="text-accent" style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Analytics Features</h3>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.25rem' }}>
              <Users size={20} style={{ marginRight: '0.75rem', color: 'var(--accent-color)' }} />
              <span style={{ fontSize: '1rem' }}>User Behavior Tracking</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.25rem' }}>
              <TrendingUp size={20} style={{ marginRight: '0.75rem', color: 'var(--accent-color)' }} />
              <span style={{ fontSize: '1rem' }}>Cultural Profile Analysis</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.25rem' }}>
              <Activity size={20} style={{ marginRight: '0.75rem', color: 'var(--accent-color)' }} />
              <span style={{ fontSize: '1rem' }}>Feature Usage Insights</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.25rem' }}>
              <BarChart3 size={20} style={{ marginRight: '0.75rem', color: 'var(--accent-color)' }} />
              <span style={{ fontSize: '1rem' }}>Recommendation Performance</span>
            </div>
          </div>
        </div>

        {analytics && (
          <div className="section">
            <h2 style={{ marginBottom: '2rem' }}>
              {isAuthenticated ? 'Your Analytics' : 'Demo Analytics'}
            </h2>
            
            {!isAuthenticated ? (
              <div style={{ 
                padding: '1rem', 
                marginBottom: '2rem',
                backgroundColor: '#FEF3C7', 
                border: '1px solid #F59E0B', 
                borderRadius: '0.5rem',
                color: '#92400E'
              }}>
                <strong>Demo Data:</strong> This shows sample analytics data. Sign in to see your personalized analytics and track your cultural journey over time.
              </div>
            ) : (
              <div style={{ 
                padding: '1rem', 
                marginBottom: '2rem',
                backgroundColor: '#D1FAE5', 
                border: '1px solid #10B981', 
                borderRadius: '0.5rem',
                color: '#065F46'
              }}>
                <strong>Your Data:</strong> This shows your personalized analytics based on your cultural preferences and usage patterns.
              </div>
            )}
            
            <div className="features-grid" style={{ gap: '2rem', marginBottom: '2rem' }}>
              <div className="card" style={{ padding: '2rem' }}>
                <h3 className="text-accent" style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>User Profile</h3>
                <div style={{ display: 'grid', gap: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>Total Sessions:</span>
                    <span style={{ color: 'var(--accent-color)', fontWeight: '600' }}>{analytics.user_profile.total_sessions}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>Total Requests:</span>
                    <span style={{ color: 'var(--accent-color)', fontWeight: '600' }}>{analytics.user_profile.total_requests}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>Engagement Score:</span>
                    <span style={{ color: 'var(--accent-color)', fontWeight: '600' }}>{(analytics.user_profile.engagement_score * 100).toFixed(1)}%</span>
                  </div>
                  <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '0.5rem' }}>
                    <span style={{ fontWeight: '500', display: 'block', marginBottom: '0.5rem' }}>Cultural Profile:</span>
                    <span style={{ color: 'var(--text-secondary)' }}>{analytics.user_profile.cultural_profile}</span>
                  </div>
                </div>
              </div>

              <div className="card" style={{ padding: '2rem' }}>
                <h3 className="text-accent" style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Feature Usage</h3>
                <div style={{ display: 'grid', gap: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>Story Development:</span>
                    <span style={{ color: 'var(--accent-color)', fontWeight: '600' }}>{analytics.feature_usage.stories} requests</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>Food Analysis:</span>
                    <span style={{ color: 'var(--accent-color)', fontWeight: '600' }}>{analytics.feature_usage.food} requests</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>Travel Planning:</span>
                    <span style={{ color: 'var(--accent-color)', fontWeight: '600' }}>{analytics.feature_usage.travel} requests</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>Recommendations:</span>
                    <span style={{ color: 'var(--accent-color)', fontWeight: '600' }}>{analytics.feature_usage.recommendations} requests</span>
                  </div>
                </div>
              </div>

              <div className="card" style={{ padding: '2rem' }}>
                <h3 className="text-accent" style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Cultural Insights</h3>
                <div style={{ marginBottom: '1.5rem' }}>
                  <span style={{ fontWeight: '500', display: 'block', marginBottom: '0.5rem' }}>Top Interests:</span>
                  <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.5rem', margin: 0 }}>
                    {analytics.cultural_insights.top_interests.map((interest, index) => (
                      <li key={index} style={{ marginBottom: '0.25rem' }}>{interest}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <span style={{ fontWeight: '500', display: 'block', marginBottom: '0.5rem' }}>Taste Evolution:</span>
                  <span style={{ color: 'var(--text-secondary)' }}>{analytics.cultural_insights.taste_evolution}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics; 