import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Globe, BookOpen, Utensils, MapPin, Sparkles, BarChart3, LogOut, User } from 'lucide-react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';

import Stories from './pages/Stories';
import Food from './pages/Food';
import Travel from './pages/Travel';
import Recommendations from './pages/Recommendations';
import Analytics from './pages/Analytics';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';

function Header() {
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
  
  const navItems = [
    { path: '/', label: 'Home', icon: Globe },
  
    { path: '/stories', label: 'Stories', icon: BookOpen },
    { path: '/food', label: 'Food', icon: Utensils },
    { path: '/travel', label: 'Travel', icon: MapPin },
    { path: '/recommendations', label: 'Recommendations', icon: Sparkles },
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo">
            Culturo
          </Link>
          <nav>
            <ul className="nav">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <li key={item.path}>
                    <Link
                      to={item.path}
                      className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                    >
                      <Icon size={16} style={{ marginRight: '0.5rem' }} />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
          <div className="auth-nav">
            {isAuthenticated ? (
              <div className="user-menu">
                <span className="user-name">
                  <User size={16} style={{ marginRight: '0.5rem' }} />
                  {user?.username || user?.email}
                </span>
                <button onClick={logout} className="btn btn-secondary logout-btn">
                  <LogOut size={16} style={{ marginRight: '0.5rem' }} />
                  Logout
                </button>
              </div>
            ) : (
              <div className="auth-buttons">
                <Link to="/signin" className="btn btn-secondary">
                  Sign In
                </Link>
                <Link to="/signup" className="btn btn-primary">
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/signin" element={<SignIn />} />
              <Route path="/signup" element={<SignUp />} />
      
              <Route path="/stories" element={<ProtectedRoute><Stories /></ProtectedRoute>} />
              <Route path="/food" element={<ProtectedRoute><Food /></ProtectedRoute>} />
              <Route path="/travel" element={<ProtectedRoute><Travel /></ProtectedRoute>} />
              <Route path="/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
              <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
