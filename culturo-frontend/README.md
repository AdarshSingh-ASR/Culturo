# Culturo Frontend

A modern, responsive React application for cultural discovery and AI-powered analysis.

## 🚀 Features

### Core Functionality
- **Story Development**: AI-powered story generation and analysis
- **Food Analysis**: Text-based food analysis with nutritional and cultural insights
- **Travel Planning**: Intelligent travel itinerary generation
- **Recommendations**: Personalized cultural recommendations
- **Analytics**: User behavior tracking and insights

### Technical Features
- **TypeScript**: Full type safety and IntelliSense
- **React 18**: Latest React features and hooks
- **Vite**: Fast development and build tooling
- **Responsive Design**: Mobile-first approach
- **Error Handling**: Comprehensive error management
- **Loading States**: Smooth user experience

## 🛠️ Technology Stack

- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: CSS with CSS Variables
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Development**: ESLint, TypeScript

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API server running

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd culturo-frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

### Environment Configuration
Create a `.env` file in the project root:

```env
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=90000

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_AUTH=true

# Environment
VITE_ENV=development
```

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
├── pages/              # Page components
│   ├── Home.tsx        # Landing page
│   ├── Stories.tsx     # Story development
│   ├── Food.tsx        # Food analysis
│   ├── Travel.tsx      # Travel planning
│   ├── Recommendations.tsx # Recommendations
│   ├── Analytics.tsx   # User analytics
│   ├── SignIn.tsx      # Authentication
│   └── SignUp.tsx      # User registration
├── services/           # API and utility services
│   └── api.ts         # API service with TypeScript types
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication context
├── config.ts          # Application configuration
├── App.tsx            # Main application component
├── main.tsx           # Application entry point
└── index.css          # Global styles
```

## 🎯 API Integration

### Food Analysis
The food analysis feature now uses text input instead of image upload:

```typescript
// Analyze food by name
const analysis = await apiService.analyzeFood({
  food_name: "pizza",
  cuisine_type: "italian",
  include_nutrition: true,
  include_cultural_context: true,
  include_recommendations: true
});
```

**Features:**
- Text-based food name input
- Optional cuisine type selection
- Comprehensive nutritional analysis
- Cultural context and significance
- Personalized recommendations
- Dietary restrictions and allergens
- Recipe suggestions

### Story Development
```typescript
const story = await apiService.generateStory({
  story_prompt: "A tale about cultural discovery",
  genre: "adventure",
  target_audience: "young adults"
});
```

### Travel Planning
```typescript
const plan = await apiService.planTravel({
  destination: "Tokyo",
  travel_style: "cultural",
  duration: "7 days",
  group_size: 2,
  budget_level: "moderate",
  cultural_interests: ["food", "history", "art"]
});
```

## 🎨 UI/UX Design

### Design System
- **Color Scheme**: Modern, accessible color palette
- **Typography**: Clean, readable fonts
- **Spacing**: Consistent spacing system
- **Components**: Reusable, accessible components

### User Experience
- **Loading States**: Smooth loading animations
- **Error Handling**: User-friendly error messages
- **Responsive Design**: Works on all device sizes
- **Accessibility**: WCAG compliant design
- **Keyboard Navigation**: Full keyboard support

## 🔧 Configuration

### API Configuration
```typescript
// src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 90000;
```

### Feature Flags
```typescript
// src/config.ts
export const config = {
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  enableAuth: import.meta.env.VITE_ENABLE_AUTH === 'true',
  apiUrl: import.meta.env.VITE_API_URL,
  apiTimeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '90000')
};
```

## 🚀 Development Workflow

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript checks
```

### Development Tips
1. **Hot Reload**: Changes are reflected immediately
2. **TypeScript**: Full type safety and IntelliSense
3. **Error Boundaries**: Graceful error handling
4. **Console Logging**: Debug information in browser console

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile-First Approach
- Single column layouts on mobile
- Optimized touch interactions
- Responsive navigation
- Adaptive content sizing

## 🎯 Customization

### Theme Customization
1. Modify CSS variables in `src/index.css`
2. Update color scheme in `:root` selector
3. Customize component styles as needed

### Feature Configuration
1. Update environment variables
2. Modify feature flags in `src/config.ts`
3. Adjust API endpoints in `src/services/api.ts`

### Adding New Pages
1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Update navigation in header
4. Add API integration if needed

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend CORS is configured
   - Check API URL in environment variables

2. **API Connection Issues**
   - Verify backend server is running
   - Check network connectivity
   - Validate API URL configuration

3. **Authentication Issues**
   - Check JWT token validity
   - Verify authentication endpoints
   - Clear localStorage if needed

### Debug Steps
1. Check browser console for errors
2. Verify environment variables
3. Test API endpoints directly
4. Check network tab for failed requests

## 📈 Performance

### Optimizations
- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Components loaded on demand
- **Caching**: Browser and service worker caching
- **Bundle Analysis**: Vite bundle analyzer

### Monitoring
- **Performance Metrics**: Core Web Vitals
- **Error Tracking**: Automatic error reporting
- **User Analytics**: Behavior tracking

## 🔒 Security

### Best Practices
- **HTTPS Only**: All API calls use HTTPS
- **Input Validation**: Client-side validation
- **Token Management**: Secure JWT token handling
- **CORS Configuration**: Proper cross-origin setup

## 📚 Documentation

- [API Integration Guide](./API_INTEGRATION.md)
- [Backend Documentation](../culturo-backend/README.md)
- [Component Library](./src/components/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ for cultural discovery and AI-powered insights.
