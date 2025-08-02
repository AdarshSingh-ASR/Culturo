import { useState } from 'react';
import { Utensils, Search, Brain, Apple } from 'lucide-react';
import { apiService, handleApiError } from '../services/api';
import type { FoodAnalysisRequest, FoodAnalysisResponse } from '../services/api';

const Food = () => {
  const [foodName, setFoodName] = useState('');
  const [cuisineType, setCuisineType] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analysis, setAnalysis] = useState<FoodAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const cuisineOptions = [
    { value: '', label: 'Any Cuisine' },
    { value: 'italian', label: 'Italian' },
    { value: 'chinese', label: 'Chinese' },
    { value: 'japanese', label: 'Japanese' },
    { value: 'indian', label: 'Indian' },
    { value: 'mexican', label: 'Mexican' },
    { value: 'french', label: 'French' },
    { value: 'thai', label: 'Thai' },
    { value: 'mediterranean', label: 'Mediterranean' },
    { value: 'american', label: 'American' },
    { value: 'korean', label: 'Korean' },
    { value: 'vietnamese', label: 'Vietnamese' },
    { value: 'greek', label: 'Greek' },
    { value: 'turkish', label: 'Turkish' },
    { value: 'moroccan', label: 'Moroccan' },
    { value: 'lebanese', label: 'Lebanese' }
  ];

  const handleAnalyze = async () => {
    if (!foodName.trim()) {
      setError('Please enter a food name to analyze');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const requestData: FoodAnalysisRequest = {
        food_name: foodName.trim(),
        cuisine_type: cuisineType || undefined,
        include_nutrition: true,
        include_cultural_context: true,
        include_recommendations: true
      };

      const response = await apiService.analyzeFood(requestData);
      setAnalysis(response);
      
      // Track the event
      await apiService.trackEvent({
        event_type: 'feature_use',
        event_name: 'food_analysis',
        event_data: { food_name: response.food_name }
      });
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error('Food analysis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isLoading) {
      handleAnalyze();
    }
  };

  return (
    <div className="section">
      <div className="container">
        <div className="hero">
          <h1>Food Intelligence & Analysis</h1>
          <p>
            Enter a food name to get comprehensive nutritional insights, 
            cultural context, and personalized recommendations powered by AI.
          </p>
        </div>

        <div className="features-grid">
          <div className="card">
            <h3 className="text-accent">Food Analysis</h3>
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
              <label className="form-label">Food Name</label>
              <input
                type="text"
                value={foodName}
                onChange={(e) => setFoodName(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., pizza, sushi, curry, burger..."
                className="form-input"
                disabled={isLoading}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Cuisine Type (Optional)</label>
              <select
                value={cuisineType}
                onChange={(e) => setCuisineType(e.target.value)}
                className="form-input"
                disabled={isLoading}
              >
                {cuisineOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <button
              className="btn btn-primary"
              onClick={handleAnalyze}
              disabled={isLoading || !foodName.trim()}
            >
              {isLoading ? (
                <>
                  <div className="spinner"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <Search size={16} style={{ marginRight: '0.5rem' }} />
                  Analyze Food
                </>
              )}
            </button>
          </div>

          <div className="card">
            <h3 className="text-accent">Analysis Features</h3>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <Search size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>AI-Powered Food Recognition</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <Apple size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Nutritional Analysis</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <Brain size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Cultural Context</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <Utensils size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Personalized Recommendations</span>
            </div>
          </div>
        </div>

        {analysis && (
          <div className="section">
            <h2>Analysis Results</h2>
            <div className="features-grid">
              <div className="card">
                <h3 className="text-accent">{analysis.food_name}</h3>
                <p><strong>Confidence:</strong> {(analysis.confidence_score * 100).toFixed(1)}%</p>
                <p><strong>Category:</strong> {analysis.category}</p>
                <p><strong>Cuisine Type:</strong> {analysis.cuisine_type}</p>
                
                <h4 style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>Cultural Context</h4>
                <p><strong>Origin:</strong> {analysis.cultural_context.origin_country}</p>
                {analysis.cultural_context.origin_region && (
                  <p><strong>Region:</strong> {analysis.cultural_context.origin_region}</p>
                )}
                {analysis.cultural_context.historical_significance && (
                  <p><strong>Historical Significance:</strong> {analysis.cultural_context.historical_significance}</p>
                )}
                <p><strong>Traditional Occasions:</strong></p>
                <ul style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                  {analysis.cultural_context.traditional_occasions.map((occasion, index) => (
                    <li key={index}>{occasion}</li>
                  ))}
                </ul>
                <p><strong>Preparation Methods:</strong></p>
                <ul style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                  {analysis.cultural_context.preparation_methods.map((method, index) => (
                    <li key={index}>{method}</li>
                  ))}
                </ul>
              </div>

              <div className="card">
                <h3 className="text-accent">Nutritional Information</h3>
                <p><strong>Calories:</strong> {analysis.nutrition.calories}</p>
                <p><strong>Protein:</strong> {analysis.nutrition.protein}g</p>
                <p><strong>Carbohydrates:</strong> {analysis.nutrition.carbohydrates}g</p>
                <p><strong>Fat:</strong> {analysis.nutrition.fat}g</p>
                {analysis.nutrition.fiber && (
                  <p><strong>Fiber:</strong> {analysis.nutrition.fiber}g</p>
                )}
                {analysis.nutrition.sugar && (
                  <p><strong>Sugar:</strong> {analysis.nutrition.sugar}g</p>
                )}
                {analysis.nutrition.sodium && (
                  <p><strong>Sodium:</strong> {analysis.nutrition.sodium}mg</p>
                )}
                
                <h4 style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>Health Benefits</h4>
                <ul style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                  {analysis.health_benefits.map((benefit, index) => (
                    <li key={index}>{benefit}</li>
                  ))}
                </ul>
              </div>

              <div className="card">
                <h3 className="text-accent">Recommendations</h3>
                <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.5rem' }}>
                  {analysis.recommendations.map((rec, index) => (
                    <li key={index}>
                      <strong>{rec.food_name}:</strong> {rec.reason}
                      {rec.cultural_connection && (
                        <div style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>
                          <em>Cultural: {rec.cultural_connection}</em>
                        </div>
                      )}
                      {rec.nutritional_benefit && (
                        <div style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>
                          <em>Nutrition: {rec.nutritional_benefit}</em>
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="card">
                <h3 className="text-accent">Ingredients</h3>
                <ul style={{ marginLeft: '1rem' }}>
                  {analysis.ingredients.map((ingredient, index) => (
                    <li key={index}>
                      <strong>{ingredient.name}</strong>
                      {ingredient.quantity && ` - ${ingredient.quantity}`}
                      {ingredient.category && ` (${ingredient.category})`}
                    </li>
                  ))}
                </ul>

                {analysis.dietary_restrictions.length > 0 && (
                  <>
                    <h4 style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>Dietary Restrictions</h4>
                    <ul style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                      {analysis.dietary_restrictions.map((restriction, index) => (
                        <li key={index}>{restriction}</li>
                      ))}
                    </ul>
                  </>
                )}

                {analysis.allergens.length > 0 && (
                  <>
                    <h4 style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>Allergens</h4>
                    <ul style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                      {analysis.allergens.map((allergen, index) => (
                        <li key={index}>{allergen}</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>

              {analysis.recipe && (
                <div className="card">
                  <h3 className="text-accent">Recipe: {analysis.recipe.title}</h3>
                  <p>{analysis.recipe.description}</p>
                  <p><strong>Cooking Time:</strong> {analysis.recipe.cooking_time}</p>
                  <p><strong>Difficulty:</strong> {analysis.recipe.difficulty_level}</p>
                  <p><strong>Servings:</strong> {analysis.recipe.servings}</p>
                  
                  <h4 style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>Instructions</h4>
                  <ol style={{ marginLeft: '1rem' }}>
                    {analysis.recipe.instructions.map((instruction, index) => (
                      <li key={index}>{instruction}</li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Food; 