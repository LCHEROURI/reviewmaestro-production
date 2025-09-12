# ReviewMaestro

AI-Powered Restaurant Review Management SaaS Platform

## Overview

ReviewMaestro is a comprehensive SaaS platform designed specifically for restaurant owners and managers to monitor, analyze, and respond to customer reviews across multiple platforms. Using advanced AI technology, ReviewMaestro helps you understand customer sentiment, prioritize responses, and generate professional replies that enhance your restaurant's reputation.

## 🚀 Live Demo

**Production URL**: [https://kkh7ikc7z7pz.manus.space](https://kkh7ikc7z7pz.manus.space)

## ✨ Key Features

- **Centralized Review Management**: Aggregate reviews from Google, Yelp, TripAdvisor, and other platforms in one dashboard
- **AI-Powered Sentiment Analysis**: Automatically analyze review sentiment and identify key topics
- **Smart Response Generation**: Create professional, personalized responses with AI assistance
- **Priority Management**: Identify high-priority reviews that need immediate attention
- **Performance Analytics**: Track your review metrics and response effectiveness over time
- **Multi-Restaurant Support**: Manage multiple restaurant locations from a single account

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python)
- **AI Integration**: OpenAI GPT for sentiment analysis and response generation
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **API**: RESTful API with comprehensive endpoints

### Frontend
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome

### Deployment
- **Backend**: Flask with Gunicorn
- **Frontend**: Built and served as static files
- **Platform**: Manus Cloud Platform

## 📁 Project Structure

```
reviewmaestro/
├── src/                          # Backend source code
│   ├── main.py                   # Flask application entry point
│   ├── models/                   # Database models
│   │   ├── user.py
│   │   ├── restaurant.py
│   │   ├── review.py
│   │   └── review_response.py
│   ├── routes/                   # API routes
│   │   ├── user.py
│   │   ├── restaurant.py
│   │   ├── review.py
│   │   └── response.py
│   └── services/                 # Business logic
│       └── ai_service.py
├── static/                       # Frontend build files
├── templates/                    # HTML templates
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies (for frontend build)
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/LCHEROURI/reviewmaestro.git
   cd reviewmaestro
   ```

2. **Set up the backend**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "OPENAI_API_BASE=https://api.openai.com/v1" >> .env
   ```

4. **Run the application**
   ```bash
   # Start the Flask server
   python src/main.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - The application includes sample data for testing

### Frontend Development (Optional)

If you want to modify the frontend:

1. **Install frontend dependencies**
   ```bash
   cd reviewmaestro-frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   # Copy build files to Flask static directory
   cp -r dist/* ../reviewmaestro/static/
   ```

## 📖 API Documentation

The API provides comprehensive endpoints for:

- **User Management**: Create, read, update, delete users
- **Restaurant Management**: Manage restaurant profiles and settings
- **Review Operations**: Import, analyze, and manage reviews
- **Response Management**: Generate, edit, and post responses
- **Analytics**: Retrieve performance metrics and trends

### Example API Endpoints

```bash
# Get all reviews for a restaurant
GET /api/reviews?restaurant_id=1

# Analyze a review with AI
POST /api/reviews/1/analyze

# Generate response for a review
POST /api/reviews/1/generate-response
{
  "tone": "professional",
  "user_id": 1
}

# Get restaurant statistics
GET /api/restaurants/1/stats
```

For complete API documentation, see the [API Documentation](docs/api.md).

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_reviewmaestro.py
```

The test suite covers:
- User operations
- Restaurant management
- Review processing
- AI analysis functionality
- Response generation
- Error handling

## 🚀 Deployment

### Production Deployment

The application is production-ready and can be deployed to various platforms:

1. **Manus Cloud** (Current deployment)
   - Automatic scaling and SSL
   - Integrated CI/CD
   - Production URL: https://kkh7ikc7z7pz.manus.space

2. **Other Platforms**
   - Heroku
   - AWS
   - Google Cloud Platform
   - DigitalOcean

### Environment Configuration

For production deployment, ensure these environment variables are set:

```bash
OPENAI_API_KEY=your_production_openai_key
OPENAI_API_BASE=https://api.openai.com/v1
FLASK_ENV=production
DATABASE_URL=your_production_database_url  # Optional
```

## 🔧 Configuration

### AI Service Configuration

The AI service can be configured in `src/services/ai_service.py`:

- **Model Selection**: Choose between different OpenAI models
- **Response Templates**: Customize response generation templates
- **Sentiment Thresholds**: Adjust sentiment analysis sensitivity

### Database Configuration

- **Development**: Uses SQLite by default
- **Production**: Easily configurable for PostgreSQL or MySQL
- **Models**: Comprehensive database schema for all entities

## 📊 Features in Detail

### AI-Powered Analysis
- Sentiment scoring (-1.0 to 1.0)
- Key topic extraction
- Urgency level assessment
- Bulk analysis capabilities

### Response Generation
- Multiple tone options (professional, friendly, apologetic)
- Context-aware responses
- Customizable templates
- Multi-language support ready

### Analytics Dashboard
- Review trend analysis
- Sentiment distribution
- Platform performance comparison
- Response rate tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Comprehensive user guide included
- **Issues**: Report bugs and request features via GitHub Issues
- **Email**: support@reviewmaestro.com (for production support)

## 🎯 Roadmap

- [ ] Mobile application (iOS/Android)
- [ ] Advanced analytics with machine learning insights
- [ ] Integration with more review platforms
- [ ] Multi-language response generation
- [ ] Automated review monitoring alerts
- [ ] Competitive benchmarking features

## 🏆 Acknowledgments

- OpenAI for providing the AI capabilities
- The Flask and React communities for excellent frameworks
- All contributors and testers who helped improve the platform

---

**Built with ❤️ for restaurant owners who care about their customers**

