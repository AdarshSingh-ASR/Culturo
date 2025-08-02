import { BookOpen, Utensils, MapPin, Sparkles, Brain, Users, ArrowRight, Star, Globe, Target, Shield, Clock } from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: Brain,
      title: 'Cultural Taste Analysis',
      description: 'Deep insights into your preferences across music, food, fashion, and more using AI-powered analysis.',
      color: '#6B4E3B'
    },
    {
      icon: Sparkles,
      title: 'AI-Powered Recommendations',
      description: 'Personalized suggestions using advanced LLMs for culturally relevant content tailored just for you.',
      color: '#8B6B4B'
    },
    {
      icon: BookOpen,
      title: 'Story Development',
      description: 'AI-assisted story creation with audience analysis and cultural context integration.',
      color: '#A67C52'
    },
    {
      icon: Utensils,
      title: 'Food Intelligence',
      description: 'AI-powered food analysis and cultural cuisine recommendations based on your taste preferences.',
      color: '#C49A6C'
    },
    {
      icon: MapPin,
      title: 'Travel Planning',
      description: 'Culturally-aware trip itineraries based on your personal tastes and preferences.',
      color: '#D4B483'
    },
    {
      icon: Users,
      title: 'Content Generation',
      description: 'Create personalized narratives and creative content tailored to your cultural preferences.',
      color: '#E4C49A'
    }
  ];

  const stats = [
    { number: '10K+', label: 'Cultural Insights Generated' },
    { number: '50K+', label: 'Recommendations Delivered' },
    { number: '95%', label: 'User Satisfaction Rate' },
    { number: '24/7', label: 'AI-Powered Analysis' }
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Cultural Enthusiast',
      content: 'Culturo helped me discover amazing international cuisine and music I never knew existed. The recommendations are spot-on!',
      rating: 5
    },
    {
      name: 'Marcus Rodriguez',
      role: 'Travel Blogger',
      content: 'The travel planning feature is incredible. It created a perfect itinerary based on my cultural interests.',
      rating: 5
    },
    {
      name: 'Emma Thompson',
      role: 'Content Creator',
      content: 'The story development tool is a game-changer. It helps me create culturally relevant content that resonates with my audience.',
      rating: 5
    }
  ];

  const benefits = [
    {
      icon: Target,
      title: 'Personalized Experience',
      description: 'Every recommendation is tailored to your unique cultural preferences and tastes.'
    },
    {
      icon: Globe,
      title: 'Global Cultural Access',
      description: 'Discover content from cultures around the world, expanding your horizons.'
    },
    {
      icon: Shield,
      title: 'Privacy-First',
      description: 'Your cultural data is protected with enterprise-grade security measures.'
    },
    {
      icon: Clock,
      title: 'Real-Time Insights',
      description: 'Get instant cultural analysis and recommendations powered by advanced AI.'
    }
  ];

  return (
    <div>
      {/* Hero Section */}
      <section className="hero" style={{ 
        background: 'linear-gradient(135deg, var(--background-primary) 0%, #F8F6F2 100%)',
        padding: '4rem 0 6rem 0',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div className="container">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: '1fr 1fr', 
            gap: '3rem', 
            alignItems: 'center',
            maxWidth: '1200px',
            margin: '0 auto'
          }}>
            <div>
              <div style={{ 
                display: 'inline-flex', 
                alignItems: 'center', 
                gap: '0.5rem',
                padding: '0.5rem 1rem',
                backgroundColor: 'rgba(107, 78, 59, 0.1)',
                borderRadius: '2rem',
                marginBottom: '1.5rem',
                fontSize: '0.9rem',
                color: 'var(--accent-color)',
                fontWeight: '500'
              }}>
                <Sparkles size={16} />
                AI-Powered Cultural Intelligence
              </div>
              
              <h1 style={{ 
                fontSize: '3.5rem', 
                lineHeight: '1.1', 
                marginBottom: '1.5rem',
                background: 'linear-gradient(135deg, var(--text-primary) 0%, var(--accent-color) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                Discover Your Cultural DNA
              </h1>
              
              <p style={{ 
                fontSize: '1.25rem', 
                lineHeight: '1.6', 
                marginBottom: '2rem',
                color: 'var(--text-secondary)'
              }}>
                Unlock personalized cultural insights, recommendations, and creative content generation 
                powered by advanced AI and taste analysis. Your cultural journey starts here.
              </p>
              
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <a href="/recommendations" className="btn btn-primary" style={{ 
                  padding: '1rem 2rem',
                  fontSize: '1.1rem',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  Start Your Journey
                  <ArrowRight size={20} />
                </a>
                <a href="/stories" className="btn btn-secondary" style={{ 
                  padding: '1rem 2rem',
                  fontSize: '1.1rem'
                }}>
                  Explore Stories
                </a>
              </div>
            </div>
            
            <div style={{ 
              position: 'relative',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center'
            }}>
              <div style={{
                width: '400px',
                height: '400px',
                background: 'linear-gradient(135deg, var(--accent-color) 0%, #8B6B4B 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                boxShadow: '0 20px 40px rgba(107, 78, 59, 0.3)'
              }}>
                <div style={{
                  width: '300px',
                  height: '300px',
                  background: 'var(--background-secondary)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: 'inset 0 4px 8px rgba(0, 0, 0, 0.1)'
                }}>
                  <Globe size={80} color="var(--accent-color)" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section style={{ 
        padding: '3rem 0',
        backgroundColor: 'var(--background-secondary)',
        borderTop: '1px solid var(--border-color)',
        borderBottom: '1px solid var(--border-color)'
      }}>
        <div className="container">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '2rem',
            textAlign: 'center'
          }}>
            {stats.map((stat, index) => (
              <div key={index}>
                <div style={{ 
                  fontSize: '2.5rem', 
                  fontWeight: '700', 
                  color: 'var(--accent-color)',
                  marginBottom: '0.5rem'
                }}>
                  {stat.number}
                </div>
                <div style={{ 
                  color: 'var(--text-secondary)',
                  fontSize: '1rem'
                }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="section">
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
              Why Choose Culturo?
            </h2>
            <p style={{ 
              fontSize: '1.2rem', 
              color: 'var(--text-secondary)',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              Experience the future of cultural discovery with our advanced AI-powered platform
            </p>
          </div>

          <div className="features-grid">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              return (
                <div key={index} className="card" style={{ 
                  textAlign: 'center',
                  padding: '2rem',
                  border: '1px solid var(--border-color)',
                  borderRadius: '1rem',
                  transition: 'all 0.3s ease'
                }}>
                  <div style={{
                    width: '60px',
                    height: '60px',
                    backgroundColor: 'rgba(107, 78, 59, 0.1)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 1.5rem',
                    color: 'var(--accent-color)'
                  }}>
                    <Icon size={28} />
                  </div>
                  <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>
                    {benefit.title}
                  </h3>
                  <p style={{ color: 'var(--text-secondary)' }}>
                    {benefit.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section" style={{ backgroundColor: 'var(--background-secondary)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
              Powerful Features
            </h2>
            <p style={{ 
              fontSize: '1.2rem', 
              color: 'var(--text-secondary)',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              Everything you need to explore and understand your cultural preferences
            </p>
          </div>

          <div className="features-grid">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="feature-card" style={{
                  padding: '2rem',
                  backgroundColor: 'var(--background-primary)',
                  borderRadius: '1rem',
                  border: '1px solid var(--border-color)',
                  transition: 'all 0.3s ease',
                  position: 'relative',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '4px',
                    background: `linear-gradient(90deg, ${feature.color} 0%, ${feature.color}80 100%)`
                  }} />
                  <div className="feature-icon" style={{
                    width: '60px',
                    height: '60px',
                    backgroundColor: `${feature.color}15`,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '1.5rem',
                    color: feature.color
                  }}>
                    <Icon size={28} />
                  </div>
                  <h3 className="feature-title" style={{ 
                    marginBottom: '1rem',
                    color: 'var(--text-primary)'
                  }}>
                    {feature.title}
                  </h3>
                  <p style={{ color: 'var(--text-secondary)' }}>
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="section">
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
              What Our Users Say
            </h2>
            <p style={{ 
              fontSize: '1.2rem', 
              color: 'var(--text-secondary)',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              Join thousands of users who have discovered their cultural DNA
            </p>
          </div>

          <div className="features-grid">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="card" style={{ 
                padding: '2rem',
                border: '1px solid var(--border-color)',
                borderRadius: '1rem',
                position: 'relative'
              }}>
                <div style={{ 
                  display: 'flex', 
                  gap: '0.25rem', 
                  marginBottom: '1rem' 
                }}>
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} size={16} fill="#FFD700" color="#FFD700" />
                  ))}
                </div>
                <p style={{ 
                  fontSize: '1.1rem', 
                  lineHeight: '1.6',
                  marginBottom: '1.5rem',
                  fontStyle: 'italic',
                  color: 'var(--text-secondary)'
                }}>
                  "{testimonial.content}"
                </p>
                <div>
                  <div style={{ 
                    fontWeight: '600', 
                    color: 'var(--text-primary)',
                    marginBottom: '0.25rem'
                  }}>
                    {testimonial.name}
                  </div>
                  <div style={{ 
                    color: 'var(--accent-color)',
                    fontSize: '0.9rem'
                  }}>
                    {testimonial.role}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Stack Section */}
      <section className="section" style={{ backgroundColor: 'var(--background-secondary)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
              Powered by Advanced Technology
            </h2>
            <p style={{ 
              fontSize: '1.2rem', 
              color: 'var(--text-secondary)',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              Cutting-edge AI and machine learning for unparalleled cultural insights
            </p>
          </div>

          <div className="features-grid">
            <div className="card text-center" style={{ 
              padding: '2rem',
              border: '1px solid var(--border-color)',
              borderRadius: '1rem',
              backgroundColor: 'var(--background-primary)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
            }}>
              <h3 className="text-accent" style={{ marginBottom: '1rem' }}>Qloo Taste AI™</h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                Cultural affinity data and taste analysis across multiple domains
              </p>
            </div>
            <div className="card text-center" style={{ 
              padding: '2rem',
              border: '1px solid var(--border-color)',
              borderRadius: '1rem',
              backgroundColor: 'var(--background-primary)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
            }}>
              <h3 className="text-accent" style={{ marginBottom: '1rem' }}>Google Gemini</h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                Advanced AI for content generation and cultural insights
              </p>
            </div>
            <div className="card text-center" style={{ 
              padding: '2rem',
              border: '1px solid var(--border-color)',
              borderRadius: '1rem',
              backgroundColor: 'var(--background-primary)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
            }}>
              <h3 className="text-accent" style={{ marginBottom: '1rem' }}>OpenAI GPT</h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                Alternative LLM for specialized tasks and recommendations
              </p>
            </div>
            <div className="card text-center" style={{ 
              padding: '2rem',
              border: '1px solid var(--border-color)',
              borderRadius: '1rem',
              backgroundColor: 'var(--background-primary)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
            }}>
              <h3 className="text-accent" style={{ marginBottom: '1rem' }}>FastAPI Backend</h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                High-performance API with real-time cultural analysis
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section" style={{ 
        background: 'linear-gradient(135deg, var(--accent-color) 0%, #8B6B4B 100%)',
        color: 'white',
        textAlign: 'center',
        padding: '2.5rem 0',
        position: 'relative'
      }}>
        <div className="container">
          <h2 style={{ 
            fontSize: '2.2rem', 
            marginBottom: '1rem',
            color: 'white',
            fontWeight: '600'
          }}>
            Ready to Discover Your Cultural DNA?
          </h2>
          
          <p style={{ 
            fontSize: '1.1rem', 
            marginBottom: '2rem',
            color: 'rgba(255, 255, 255, 0.9)',
            maxWidth: '600px',
            margin: '0 auto 2rem',
            lineHeight: '1.5'
          }}>
            Join thousands of users exploring their cultural preferences with AI-powered insights.
          </p>
          
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            justifyContent: 'center', 
            flexWrap: 'wrap',
            marginBottom: '1.5rem'
          }}>
            <a href="/recommendations" className="btn" style={{ 
              backgroundColor: 'white',
              color: 'var(--accent-color)',
              padding: '0.875rem 1.75rem',
              fontSize: '1rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: '500',
              borderRadius: '0.5rem',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              transition: 'all 0.3s ease',
              textDecoration: 'none'
            }}>
              Get Started Now
              <ArrowRight size={18} />
            </a>
            <a href="/stories" className="btn" style={{ 
              backgroundColor: 'transparent',
              color: 'white',
              border: '2px solid white',
              padding: '0.875rem 1.75rem',
              fontSize: '1rem',
              fontWeight: '500',
              borderRadius: '0.5rem',
              transition: 'all 0.3s ease',
              textDecoration: 'none'
            }}>
              Explore Stories
            </a>
          </div>
          
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '2rem',
            marginTop: '1.5rem',
            paddingTop: '1.5rem',
            borderTop: '1px solid rgba(255,255,255,0.2)'
          }}>
            <div style={{ 
              textAlign: 'center',
              color: 'rgba(255, 255, 255, 0.8)',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}>
              Personalized
            </div>
            <div style={{ 
              textAlign: 'center',
              color: 'rgba(255, 255, 255, 0.8)',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}>
              Instant
            </div>
            <div style={{ 
              textAlign: 'center',
              color: 'rgba(255, 255, 255, 0.8)',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}>
              Secure
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home; 