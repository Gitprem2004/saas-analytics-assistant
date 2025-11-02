# SaaS Analytics Assistant

AI-powered natural language interface for business intelligence. Ask questions about your SaaS metrics in plain English and get instant SQL queries, visualizations, and insights powered by Google Gemini AI.

## Features

- **Natural Language Queries**: Convert plain English questions to SQL automatically
- **Real-time Visualizations**: Interactive charts (pie/bar) and data tables
- **AI-Generated Insights**: Business recommendations based on query results
- **Query History**: Track and reuse previous queries
- **Data Export**: Download results as CSV
- **Sample Dataset**: Pre-populated with 1000+ users, subscriptions, events, and revenue records

## Tech Stack

### Frontend
- React with TypeScript
- Chart.js for data visualization
- Responsive CSS design

### Backend
- FastAPI (Python web framework)
- SQLAlchemy ORM
- SQLite database
- Google Gemini Pro AI (free tier)

## Architecture
Frontend (React) → Backend API (FastAPI) → Gemini AI → SQL Generation → Database → Results

## Sample Queries

- "How many total users do we have?"
- "What's our monthly recurring revenue?"
- "Show me user signups by month"
- "What's our customer churn rate?"
- "Which features are most popular?"
- "What's the conversion rate from free to paid plans?"

## Local Development Setup

### Prerequisites 
- Python 3.11 or higher
- Node.js 18 or higher
- Git

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000

### Frontend Setup
cd frontend
npm install
cp .env.example .env
npm start

###Initialize Database

Visit http://localhost:8000/api/generate-data or use the API docs at http://localhost:8000/docs

##Environment Variables
###Backend (.env)
GEMINI_API_KEY=your_key_here  # Get from https://aistudio.google.com/app/apikey
DATABASE_URL=sqlite:///./saas_analytics.db
ENVIRONMENT=development

###Frontend (.env)
REACT_APP_API_URL=http://localhost:8000

##API Endpoints

GET / - Health check
POST /api/query - Analyze natural language query
POST /api/generate-data - Generate sample SaaS data
POST /api/initialize-database - Initialize database for deployment
GET /docs - Interactive API documentation

#Project Structure

saas-analytics-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── database.py       # Database configuration
│   │   ├── config.py         # Settings management
│   │   ├── models/
│   │   │   └── saas_models.py    # SQLAlchemy models
│   │   └── services/
│   │       ├── ai_service.py     # Gemini AI integration
│   │       └── data_generator.py # Sample data creation
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   └── App.css
│   ├── package.json
│   └── .env
└── README.md

#Deployment
##Backend (Railway)

Push code to GitHub
Create new project on Railway.app
Connect GitHub repository
Add environment variables
Deploy automatically

##Frontend (Vercel)

Push code to GitHub
Import project on Vercel.com
Set root directory to frontend
Add environment variables

#Deploy

#Live Demo
[Add your deployment URL here]

#Screenshots

[Add screenshots of your application showing different queries and visualizations]

#Key Learnings

This project demonstrates:

Full-stack development (React + FastAPI)
AI integration with Google Gemini
Natural language processing for SQL generation
Data visualization with Chart.js
RESTful API design
Database modeling for SaaS metrics
Deployment to cloud platforms

##Future Enhancements

User authentication and multi-tenancy
Real-time database connections (PostgreSQL, MySQL)
Advanced chart types (line graphs, heatmaps)
Scheduled report generation
Export to PDF with formatted reports
Query optimization and caching
More complex analytical queries

#License
MIT License
Author
PREMKUMAR S

GitHub: https://github.com/Gitprem2004
LinkedIn: https://www.linkedin.com/in/prem19
Email: premkarthik30@gmail.com

#Acknowledgments

Google Gemini AI for natural language processing
FastAPI framework
React and Chart.js communities

---

## **NOW YOU'RE DEPLOYMENT READY**

All pre-deployment fixes are complete:
- Security (gitignore, env files)
- Database initialization
- Error handling
- Configuration management
- Professional documentation

**Next step: Push to GitHub and deploy to Railway + Vercel**

Ready to proceed with deployment?