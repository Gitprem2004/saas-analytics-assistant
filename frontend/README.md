# SaaS Analytics Assistant

AI-powered natural language interface for SaaS business intelligence. Ask questions about your business data in plain English and get instant SQL queries, visualizations, and insights.

![Demo](screenshots/demo.gif)

## Features

- Natural language to SQL conversion using Google Gemini AI
- Real-time data visualization (charts and tables)
- AI-generated business insights
- Query history tracking
- CSV data export
- Sample dataset with 1000+ users, subscriptions, and revenue records

## Tech Stack

**Frontend**
- React with TypeScript
- Chart.js for visualizations
- Responsive design with CSS

**Backend**
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite database
- Google Gemini Pro AI (free tier)

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
uvicorn app.main:app --reload --port 8000