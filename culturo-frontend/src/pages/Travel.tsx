import { useState } from 'react';
import { MapPin, Calendar, Users, Globe } from 'lucide-react';
import { apiService, handleApiError } from '../services/api';
import type { TravelPlanningRequest, TravelPlanningResponse } from '../services/api';

const Travel = () => {
  const [destination, setDestination] = useState('');
  const [travelStyle, setTravelStyle] = useState('');
  const [duration, setDuration] = useState('');
  const [groupSize, setGroupSize] = useState(1);
  const [budgetLevel, setBudgetLevel] = useState('moderate');
  const [culturalInterests, setCulturalInterests] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [itinerary, setItinerary] = useState<TravelPlanningResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePlan = async () => {
    if (!destination.trim()) {
      setError('Please enter a destination');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const requestData: TravelPlanningRequest = {
        destination: destination.trim(),
        travel_style: travelStyle || undefined,
        duration: duration || undefined,
        group_size: groupSize,
        budget_level: budgetLevel,
        cultural_interests: culturalInterests
      };

      console.log('Sending travel planning request:', requestData);
      const response = await apiService.planTravel(requestData);
      console.log('Travel planning response received:', response);
      setItinerary(response);
      
      // Track the event
      try {
        await apiService.trackEvent({
          event_type: 'feature_use',
          event_name: 'travel_planning',
          event_data: { destination, travelStyle, duration }
        });
      } catch (analyticsError) {
        console.warn('Analytics tracking failed:', analyticsError);
        // Don't fail the main request if analytics fails
      }
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error('Travel planning error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="section">
      <div className="container">
        <div className="hero">
          <h1>Culturally-Aware Travel Planning</h1>
          <p>
            Create personalized travel itineraries based on your cultural preferences 
            and interests. Discover authentic experiences and cultural insights.
          </p>
        </div>

        <div className="features-grid">
          <div className="card">
            <h3 className="text-accent">Travel Planning</h3>
            {error && (
              <div style={{ 
                padding: '0.75rem', 
                marginBottom: '1rem', 
                backgroundColor: '#FEE2E2', 
                border: '1px solid #FCA5A5', 
                borderRadius: '0.5rem',
                color: '#DC2626'
              }}>
                {error}
              </div>
            )}
            <div className="form-group">
              <label className="form-label">Destination</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Tokyo, Japan"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Travel Style</label>
              <select
                className="form-input"
                value={travelStyle}
                onChange={(e) => setTravelStyle(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Select Style</option>
                <option value="cultural">Cultural</option>
                <option value="adventure">Adventure</option>
                <option value="relaxing">Relaxing</option>
                <option value="luxury">Luxury</option>
                <option value="budget">Budget</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Duration</label>
              <select
                className="form-input"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Select Duration</option>
                <option value="3 days">3 days</option>
                <option value="5 days">5 days</option>
                <option value="7 days">7 days</option>
                <option value="10 days">10 days</option>
                <option value="14 days">14 days</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Group Size</label>
              <select
                className="form-input"
                value={groupSize}
                onChange={(e) => setGroupSize(Number(e.target.value))}
                disabled={isLoading}
              >
                <option value={1}>1 person</option>
                <option value={2}>2 people</option>
                <option value={3}>3 people</option>
                <option value={4}>4 people</option>
                <option value={5}>5 people</option>
                <option value={6}>6+ people</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Budget Level</label>
              <select
                className="form-input"
                value={budgetLevel}
                onChange={(e) => setBudgetLevel(e.target.value)}
                disabled={isLoading}
              >
                <option value="budget">Budget</option>
                <option value="moderate">Moderate</option>
                <option value="luxury">Luxury</option>
                <option value="ultra_luxury">Ultra Luxury</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Cultural Interests (Optional)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., art, food, history, music"
                value={culturalInterests.join(', ')}
                onChange={(e) => setCulturalInterests(e.target.value.split(',').map(s => s.trim()).filter(s => s))}
                disabled={isLoading}
              />
              <small style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                Separate multiple interests with commas
              </small>
            </div>
            <button
              className="btn btn-primary"
              onClick={handlePlan}
              disabled={isLoading || !destination.trim()}
            >
              {isLoading ? (
                <>
                  <div className="spinner"></div>
                  Planning Trip...
                </>
              ) : (
                <>
                  <MapPin size={16} style={{ marginRight: '0.5rem' }} />
                  Plan Trip
                </>
              )}
            </button>
          </div>

          <div className="card">
            <h3 className="text-accent">Travel Features</h3>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <Globe size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Cultural Insights</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <Calendar size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Personalized Itineraries</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <Users size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Local Experiences</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <MapPin size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Cultural Activities</span>
            </div>
          </div>
        </div>

        {itinerary && (
          <div className="section">
            <h2>Your Travel Itinerary</h2>
            
            {/* Trip Overview Card */}
            <div className="features-grid">
              <div className="card">
                <h3 className="text-accent">{itinerary.destination}</h3>
                <p><strong>Duration:</strong> {itinerary.duration}</p>
                <p><strong>Travel Style:</strong> {itinerary.travel_style}</p>
                <p><strong>Budget Estimate:</strong> {itinerary.budget_estimate}</p>
                <p><strong>Cultural Insights:</strong></p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{itinerary.cultural_insights}</p>
              </div>
            </div>

            {/* Rich Natural Language Response (like qloo-llm-hackathon-2025) */}
            {itinerary.llm_summary && (
              <div className="section">
                <h3>Your Personalized Itinerary</h3>
                <div className="card" style={{ padding: '2rem', lineHeight: '1.6', fontSize: '1rem' }}>
                  <div style={{ 
                    fontFamily: 'inherit',
                    color: 'var(--text-primary)'
                  }}>
                    {itinerary.llm_summary.split('\n').map((line, index) => {
                      // Handle markdown formatting
                      if (line.startsWith('# ')) {
                        return <h2 key={index} style={{ color: 'var(--accent-color)', marginBottom: '1rem' }}>{line.substring(2)}</h2>;
                      } else if (line.startsWith('## ')) {
                        return <h3 key={index} style={{ color: 'var(--accent-color)', marginBottom: '0.75rem' }}>{line.substring(3)}</h3>;
                      } else if (line.startsWith('### ')) {
                        return <h4 key={index} style={{ color: 'var(--accent-color)', marginBottom: '0.5rem' }}>{line.substring(4)}</h4>;
                      } else if (line.startsWith('* ') || line.startsWith('- ')) {
                        return <div key={index} style={{ marginLeft: '1rem', marginBottom: '0.25rem' }}>• {line.substring(2)}</div>;
                      } else if (line.startsWith('**') && line.endsWith('**')) {
                        return <strong key={index}>{line.substring(2, line.length - 2)}</strong>;
                      } else if (line.trim() === '') {
                        return <br key={index} />;
                      } else {
                        return <div key={index} style={{ marginBottom: '0.5rem' }}>{line}</div>;
                      }
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Daily Activities with Details */}
            <div className="section">
              <h3>Daily Activities</h3>
              <div className="features-grid">
                {itinerary.itinerary && itinerary.itinerary.map((day, index) => (
                  <div key={index} className="card" style={{ padding: '1.5rem', marginBottom: '1rem' }}>
                    <h4 style={{ color: 'var(--accent-color)', marginBottom: '0.5rem' }}>Day {day.day}</h4>
                    <p style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>{day.activity}</p>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>{day.cultural_context}</p>
                    
                    {/* Show detailed activities if available */}
                    {day.morning_activity && (
                      <div style={{ marginBottom: '0.5rem' }}>
                        <span style={{ fontWeight: 'bold', color: 'var(--accent-color)' }}>🌅 Morning:</span> {day.morning_activity}
                      </div>
                    )}
                    {day.afternoon_activity && (
                      <div style={{ marginBottom: '0.5rem' }}>
                        <span style={{ fontWeight: 'bold', color: 'var(--accent-color)' }}>☀️ Afternoon:</span> {day.afternoon_activity}
                      </div>
                    )}
                    {day.evening_activity && (
                      <div style={{ marginBottom: '0.5rem' }}>
                        <span style={{ fontWeight: 'bold', color: 'var(--accent-color)' }}>🌙 Evening:</span> {day.evening_activity}
                      </div>
                    )}
                    
                    {/* Show places if available */}
                    {day.places && day.places.length > 0 && (
                      <div style={{ marginTop: '1rem', padding: '0.5rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '0.25rem' }}>
                        <p style={{ fontWeight: 'bold', marginBottom: '0.5rem', color: 'var(--accent-color)' }}>📍 Places to Visit:</p>
                        {day.places.map((place, placeIndex) => (
                          <div key={placeIndex} style={{ marginBottom: '0.25rem', fontSize: '0.9rem' }}>
                            <strong>{place.name}</strong>
                            {place.properties && place.properties.address && (
                              <span style={{ color: 'var(--text-secondary)' }}> - {place.properties.address}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Cultural Activities */}
            {(itinerary.cultural_activities && itinerary.cultural_activities.length > 0) && (
              <div className="section">
                <h3>Cultural Activities</h3>
                <div className="features-grid">
                  {itinerary.cultural_activities.map((activity, index) => (
                    <div key={index} className="card" style={{ padding: '1rem' }}>
                      <h4 style={{ color: 'var(--accent-color)', marginBottom: '0.5rem' }}>{activity.name}</h4>
                      <p style={{ marginBottom: '0.5rem' }}>{activity.description}</p>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>{activity.cultural_significance}</p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        <span>⏱️ {activity.duration}</span>
                        <span>💰 {activity.cost_range}</span>
                        <span>📍 {activity.location}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Local Experiences */}
            {(itinerary.local_experiences && itinerary.local_experiences.length > 0) && (
              <div className="section">
                <h3>Local Experiences</h3>
                <div className="features-grid">
                  {itinerary.local_experiences.map((experience, index) => (
                    <div key={index} className="card" style={{ padding: '1rem' }}>
                      <h4 style={{ color: 'var(--accent-color)', marginBottom: '0.5rem' }}>{experience.name}</h4>
                      <p style={{ marginBottom: '0.5rem' }}>{experience.description}</p>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>{experience.cultural_context}</p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        <span>⏱️ {experience.duration}</span>
                        <span>💰 {experience.cost}</span>
                        <span>📍 {experience.location}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Travel; 