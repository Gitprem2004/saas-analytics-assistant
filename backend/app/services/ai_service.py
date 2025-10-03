import google.generativeai as genai
import os
from typing import Dict, Any
import json
import re
from sqlalchemy.orm import Session
from sqlalchemy import text

class SaaSAnalyticsAI:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Fallback patterns if API fails
        self.query_patterns = {
            'total_users': ['total users', 'how many users', 'user count', 'number of users'],
            'active_users': ['active users', 'active customers'],
            'mrr': ['mrr', 'monthly recurring revenue', 'recurring revenue'],
            'revenue': ['revenue', 'income', 'earnings'],
            'churn': ['churn', 'churned', 'cancelled', 'lost users'],
            'signups': ['signups', 'new users', 'registrations', 'signed up'],
            'subscriptions': ['subscriptions', 'paid users', 'paying customers'],
            'plans': ['plans', 'plan types', 'subscription plans'],
            'events': ['events', 'activities', 'user activity'],
            'features': ['features', 'popular features', 'most used', 'feature usage']
        }
    
    def generate_sql_query(self, question: str) -> str:
        """Convert natural language question to SQL query using Gemini AI"""
        
        system_prompt = """You are an expert SQL generator for SaaS analytics. Your ONLY job is to output valid SQLite queries.

        DATABASE SCHEMA:
        - users: id, email, created_at, plan_type, status
        - subscriptions: id, user_id, plan_name, mrr (monthly recurring revenue), start_date, end_date, status
        - events: id, user_id, event_name, event_date, properties
        - revenue: id, date, amount, source, user_id

        STRICT RULES:
        1. Output ONLY the SQL query - no explanations, no markdown, no extra text
        2. Use SQLite syntax (not MySQL or PostgreSQL)
        3. Always add LIMIT 100 for safety
        4. Use ROUND() for decimal calculations
        5. For averages across users, JOIN tables appropriately
        6. Active subscriptions: WHERE status = 'active'
        7. Recent data: WHERE created_at >= date('now', '-12 months')

        EXAMPLES:
        Question: "How many users?" 
        Answer: SELECT COUNT(*) as total_users FROM users

        Question: "What's our MRR?"
        Answer: SELECT ROUND(SUM(mrr), 2) as total_mrr FROM subscriptions WHERE status = 'active'

        Question: "Average revenue per user?"
        Answer: SELECT ROUND(AVG(total_revenue), 2) as avg_revenue_per_user FROM (SELECT user_id, SUM(amount) as total_revenue FROM revenue GROUP BY user_id)

        Question: "Show revenue by month for the last 6 months"
        Answer: SELECT strftime('%Y-%m', date) as month, ROUND(SUM(amount), 2) as revenue FROM revenue WHERE date >= date('now', '-6 months') GROUP BY month ORDER BY month DESC

        Question: "Compare active vs churned users"
        Answer: SELECT status, COUNT(*) as count FROM users GROUP BY status

        Now generate SQL for this question:
        {question}

        SQL:"""
        
        try:
            # Try Gemini AI first
            response = self.model.generate_content(
                system_prompt.format(question=question)
            )
            
            sql_query = response.text.strip()
            
            # Clean up the SQL query
            sql_query = re.sub(r'^```sql\s*', '', sql_query, flags=re.IGNORECASE)
            sql_query = re.sub(r'^```\s*', '', sql_query)
            sql_query = re.sub(r'\s*```$', '', sql_query)
            sql_query = sql_query.strip()
            
            print(f"Gemini generated SQL: {sql_query}")
            return sql_query
            
        except Exception as e:
            # Fallback to pattern matching
            print(f"Gemini unavailable, using fallback: {str(e)}")
            return self.get_fallback_query(question)
    
    def get_fallback_query(self, question: str) -> str:
        """Fallback pattern matching if Gemini fails"""
        question_lower = question.lower()
        
        if any(pattern in question_lower for pattern in self.query_patterns['total_users']):
            return "SELECT COUNT(*) as total_users FROM users"
        
        elif any(pattern in question_lower for pattern in self.query_patterns['active_users']):
            return "SELECT COUNT(*) as active_users FROM users WHERE status = 'active'"
        
        elif any(pattern in question_lower for pattern in self.query_patterns['mrr']):
            return "SELECT ROUND(SUM(mrr), 2) as monthly_recurring_revenue FROM subscriptions WHERE status = 'active'"
        
        elif any(pattern in question_lower for pattern in self.query_patterns['revenue']):
            return "SELECT ROUND(SUM(amount), 2) as total_revenue FROM revenue WHERE date >= date('now', '-1 year')"
        
        elif any(pattern in question_lower for pattern in self.query_patterns['churn']):
            return "SELECT COUNT(*) as churned_users FROM users WHERE status = 'churned'"
        
        elif any(pattern in question_lower for pattern in self.query_patterns['signups']):
            return "SELECT COUNT(*) as new_signups FROM users WHERE created_at >= date('now', '-30 days')"
        
        elif any(pattern in question_lower for pattern in self.query_patterns['subscriptions']):
            return "SELECT COUNT(*) as total_subscriptions FROM subscriptions WHERE status = 'active'"
        
        elif any(pattern in question_lower for pattern in self.query_patterns['plans']):
            return "SELECT plan_type, COUNT(*) as user_count FROM users GROUP BY plan_type ORDER BY user_count DESC"
        
        elif 'features' in question_lower and 'popular' in question_lower:
            return "SELECT event_name as feature_name, COUNT(*) as usage_count FROM events GROUP BY event_name ORDER BY usage_count DESC LIMIT 10"
        
        else:
            return "SELECT COUNT(*) as total_users FROM users"
    
    def execute_query(self, db: Session, sql_query: str) -> Dict[str, Any]:
        """Execute SQL query safely and return formatted results"""
        
        try:
            # Basic SQL injection prevention
            forbidden_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER']
            sql_upper = sql_query.upper()
            
            for keyword in forbidden_keywords:
                if keyword in sql_upper:
                    raise Exception(f"Query contains forbidden operation: {keyword}")
            
            # Execute query
            result = db.execute(text(sql_query))
            
            # Format results
            if result.returns_rows:
                rows = result.fetchall()
                columns = list(result.keys()) if rows else []
                
                # Convert to list of dictionaries
                data = []
                for row in rows:
                    row_dict = {}
                    for i, column in enumerate(columns):
                        row_dict[column] = str(row[i])
                    data.append(row_dict)
                
                return {
                    "type": "table" if len(data) > 1 else "metric",
                    "data": data,
                    "columns": columns,
                    "row_count": len(data)
                }
            else:
                return {
                    "type": "success",
                    "message": "Query executed successfully"
                }
                
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    def generate_insights(self, question: str, query_result: Dict[str, Any]) -> str:
        """Generate business insights using Gemini AI"""
        
        try:
            data = query_result.get("data", [])
            
            if not data:
                return "No data available for analysis."
            
            # Try Gemini for insights
            insight_prompt = f"""Based on this SaaS analytics data, provide ONE brief business insight (max 40 words).
Focus on actionable recommendations for SaaS growth.

Question: {question}
Data: {json.dumps(data[:5], default=str)}

Insight:"""
            
            response = self.model.generate_content(insight_prompt)
            return response.text.strip()
            
        except Exception as e:
            # Fallback insights
            print(f"Gemini insights unavailable: {str(e)}")
            return self.get_fallback_insight(question, query_result)
    
    def get_fallback_insight(self, question: str, query_result: Dict[str, Any]) -> str:
        """Fallback insights if Gemini fails"""
        question_lower = question.lower()
        data = query_result.get("data", [])
        
        if not data:
            return "No data available for analysis."
        
        first_result = data[0]
        
        if 'users' in question_lower:
            user_count = int(list(first_result.values())[0])
            return f"Strong user base of {user_count:,} users. Focus on retention and upselling opportunities."
        
        elif 'revenue' in question_lower or 'mrr' in question_lower:
            revenue = float(list(first_result.values())[0])
            return f"Revenue of ${revenue:,.2f} indicates healthy business performance."
        
        elif 'churn' in question_lower:
            churn_count = int(list(first_result.values())[0])
            return f"{churn_count} churned users. Monitor retention strategies and customer satisfaction."
        
        elif len(data) > 1:
            return f"Analysis shows {len(data)} data points. Look for trends to guide business decisions."
        
        else:
            return "Data retrieved successfully. Use these metrics to guide your SaaS growth strategy."