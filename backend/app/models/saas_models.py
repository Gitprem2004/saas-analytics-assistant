from sqlalchemy import Column, Integer, String, DateTime, JSON, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=func.now())
    plan_type = Column(String(50))
    status = Column(String(50))
    
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    plan_name = Column(String(100))
    mrr = Column(Numeric(10, 2))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50))

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    event_name = Column(String(100))
    event_date = Column(DateTime, default=func.now())
    properties = Column(JSON)

class Revenue(Base):
    __tablename__ = "revenue"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    amount = Column(Numeric(10, 2))
    source = Column(String(100))
    user_id = Column(Integer)
