import { useState } from 'react';
import { BookOpen, PenTool, Users, Eye, Sparkles } from 'lucide-react';
import { apiService, handleApiError } from '../services/api';
import type { StoryGenerationRequest, StoryGenerationResponse } from '../services/api';

const Stories = () => {
  const [storyPrompt, setStoryPrompt] = useState('');
  const [genre, setGenre] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [story, setStory] = useState<StoryGenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!storyPrompt.trim()) {
      setError('Please enter a story idea or prompt');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const requestData: StoryGenerationRequest = {
        story_prompt: storyPrompt.trim(),
        genre: genre || undefined,
        target_audience: targetAudience || undefined
      };

      const response = await apiService.generateStory(requestData);
      setStory(response);
      
      // Track the event
      await apiService.trackEvent({
        event_type: 'feature_use',
        event_name: 'story_generation',
        event_data: { genre, targetAudience }
      });
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error('Story generation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="section">
      <div className="container">
        <div className="hero">
          <h1>AI-Powered Story Development</h1>
          <p>
            Create compelling stories with cultural context and audience analysis. 
            Our AI helps you develop narratives that resonate with specific audiences.
          </p>
        </div>

        <div className="features-grid">
          <div className="card">
            <h3 className="text-accent">Story Analysis</h3>
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
              <label className="form-label">Story Idea or Prompt</label>
              <textarea
                className="form-input"
                placeholder="Describe your story idea, characters, or theme..."
                value={storyPrompt}
                onChange={(e) => setStoryPrompt(e.target.value)}
                rows={4}
                disabled={isLoading}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Genre</label>
              <select
                className="form-input"
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Select Genre</option>
                <option value="drama">Drama</option>
                <option value="comedy">Comedy</option>
                <option value="romance">Romance</option>
                <option value="thriller">Thriller</option>
                <option value="fantasy">Fantasy</option>
                <option value="sci-fi">Science Fiction</option>
                <option value="historical">Historical</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Target Audience</label>
              <select
                className="form-input"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Select Audience</option>
                <option value="young_adults">Young Adults (18-25)</option>
                <option value="adults">Adults (25-45)</option>
                <option value="teens">Teenagers (13-17)</option>
                <option value="children">Children (5-12)</option>
                <option value="seniors">Seniors (65+)</option>
              </select>
            </div>
            <button
              className="btn btn-primary"
              onClick={handleGenerate}
              disabled={isLoading || !storyPrompt.trim()}
            >
              {isLoading ? (
                <>
                  <div className="spinner"></div>
                  Generating Story...
                </>
              ) : (
                <>
                  <PenTool size={16} style={{ marginRight: '0.5rem' }} />
                  Generate Story
                </>
              )}
            </button>
          </div>

          <div className="card">
            <h3 className="text-accent">Story Features</h3>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <BookOpen size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Plot Development</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <Users size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Character Analysis</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <Eye size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Visual Scene Generation</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <Sparkles size={20} style={{ marginRight: '0.5rem', color: 'var(--accent-color)' }} />
              <span>Cultural Context</span>
            </div>
          </div>
        </div>

        {story && (
          <div className="section">
            <h2>Generated Story</h2>
            <div className="features-grid">
              <div className="card">
                                 <h3 className="text-accent">{story.title}</h3>
                 <p><strong>Summary:</strong></p>
                 <div style={{ 
                   padding: '0.75rem', 
                   marginBottom: '1rem', 
                   backgroundColor: 'var(--bg-secondary)', 
                   borderRadius: '0.5rem',
                   whiteSpace: 'pre-wrap',
                   lineHeight: '1.5'
                 }}>
                   {story.summary}
                 </div>
                 <p><strong>Plot Outline:</strong></p>
                 <div style={{ 
                   padding: '0.75rem', 
                   marginBottom: '1rem', 
                   backgroundColor: 'var(--bg-secondary)', 
                   borderRadius: '0.5rem',
                   whiteSpace: 'pre-wrap',
                   lineHeight: '1.5'
                 }}>
                   {story.plot_outline}
                 </div>
                
                <p><strong>Characters:</strong></p>
                <div style={{ marginBottom: '1rem' }}>
                  {story.characters.map((character, index) => (
                    <div key={index} style={{ 
                      padding: '0.75rem', 
                      marginBottom: '0.5rem', 
                      backgroundColor: 'var(--bg-secondary)', 
                      borderRadius: '0.5rem',
                      border: '1px solid var(--border-color)'
                    }}>
                      <strong>{character.name}</strong> ({character.role})
                      <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        {character.description}
                      </p>
                      <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        <strong>Traits:</strong> {character.personality_traits.join(', ')}
                      </p>
                    </div>
                  ))}
                </div>

                <p><strong>Cultural Context:</strong></p>
                <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>{story.cultural_context}</p>
                
                <p><strong>Writing Style:</strong></p>
                <p style={{ color: 'var(--text-secondary)' }}>{story.writing_style}</p>
                
                <p><strong>Estimated Word Count:</strong></p>
                <p style={{ color: 'var(--text-secondary)' }}>{story.estimated_word_count.toLocaleString()} words</p>
              </div>

              <div className="card">
                <h3 className="text-accent">Story Elements</h3>
                
                                 <p><strong>Scenes:</strong></p>
                 <div style={{ marginBottom: '1rem' }}>
                   {story.scenes.map((scene, index) => (
                     <div key={index} style={{ 
                       padding: '0.75rem', 
                       marginBottom: '1rem', 
                       backgroundColor: 'var(--bg-secondary)', 
                       borderRadius: '0.5rem',
                       fontSize: '0.9rem',
                       border: '1px solid var(--border-color)'
                     }}>
                       <strong>Scene {scene.scene_number}: {scene.title}</strong>
                       <div style={{ 
                         margin: '0.5rem 0 0 0', 
                         color: 'var(--text-secondary)',
                         whiteSpace: 'pre-wrap',
                         lineHeight: '1.5',
                         maxHeight: '300px',
                         overflowY: 'auto'
                       }}>
                         {scene.description}
                       </div>
                     </div>
                   ))}
                 </div>

                <p><strong>Themes:</strong></p>
                <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.5rem', marginBottom: '1rem' }}>
                  {story.themes.map((theme, index) => (
                    <li key={index}>
                      {typeof theme === 'string' ? theme : (theme as any)?.name || (theme as any)?.description || JSON.stringify(theme)}
                    </li>
                  ))}
                </ul>
                
                <p><strong>Tone Suggestions:</strong></p>
                <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.5rem', marginBottom: '1rem' }}>
                  {story.tone_suggestions.map((tone, index) => (
                    <li key={index}>
                      {typeof tone === 'string' ? tone : (tone as any)?.name || (tone as any)?.description || JSON.stringify(tone)}
                    </li>
                  ))}
                </ul>
                
                <p><strong>Target Demographics:</strong></p>
                <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.5rem', marginBottom: '1rem' }}>
                  {story.audience_analysis.target_demographics.map((demo, index) => (
                    <li key={index}>
                      {typeof demo === 'string' ? demo : (demo as any)?.name || (demo as any)?.description || JSON.stringify(demo)}
                    </li>
                  ))}
                </ul>

                <p><strong>Cultural Interests:</strong></p>
                <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.5rem', marginBottom: '1rem' }}>
                  {story.audience_analysis.cultural_interests.map((interest, index) => (
                    <li key={index}>
                      {typeof interest === 'string' ? interest : (interest as any)?.name || (interest as any)?.description || JSON.stringify(interest)}
                    </li>
                  ))}
                </ul>

                <p><strong>Reading Preferences:</strong></p>
                <ul style={{ color: 'var(--text-secondary)', paddingLeft: '1.5rem' }}>
                  {story.audience_analysis.reading_preferences.map((pref, index) => (
                    <li key={index}>
                      {typeof pref === 'string' ? pref : (pref as any)?.name || (pref as any)?.description || JSON.stringify(pref)}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Stories; 