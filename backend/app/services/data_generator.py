from faker import Faker
import random
from datetime import datetime, timedelta
from decimal import Decimal as PyDecimal
from sqlalchemy.orm import Session
from ..models.saas_models import User, Subscription, Event, Revenue

fake = Faker()

def generate_sample_data(db: Session):
    # Clear existing data
    db.query(Revenue).delete()
    db.query(Event).delete()
    db.query(Subscription).delete()
    db.query(User).delete()
    
    # Generate Users
    # Generate Users
    users = []
    used_emails = set()
    for i in range(1000):
        # Ensure unique emails
        email = fake.email()
        while email in used_emails:
            email = fake.email()
        used_emails.add(email)
    
        user = User(
            email=email,
            created_at=fake.date_time_between(start_date='-2y', end_date='now'),
            plan_type=random.choice(['free', 'basic', 'pro', 'enterprise']),
            status=random.choice(['active', 'inactive', 'churned'])
        )
        users.append(user)
    
    db.add_all(users)
    db.commit()
    
    # Refresh users to get their IDs
    db.refresh(users[0])
    users = db.query(User).all()
    
    # Generate Subscriptions
    subscriptions = []
    for user in users:
        if user.plan_type != 'free':
            mrr_amounts = {'basic': 29, 'pro': 99, 'enterprise': 299}
            subscription = Subscription(
                user_id=user.id,
                plan_name=user.plan_type,
                mrr=PyDecimal(mrr_amounts.get(user.plan_type, 29)),
                start_date=user.created_at,
                end_date=None if user.status == 'active' else fake.date_time_between(start_date=user.created_at, end_date='now'),
                status=user.status
            )
            subscriptions.append(subscription)
    
    db.add_all(subscriptions)
    db.commit()
    
    # Generate Events
    events = []
    event_types = ['login', 'feature_used', 'export_data', 'create_report', 'invite_user']
    
    for user in users:
        num_events = random.randint(10, 100)
        for _ in range(num_events):
            event = Event(
                user_id=user.id,
                event_name=random.choice(event_types),
                event_date=fake.date_time_between(start_date=user.created_at, end_date='now'),
                properties={'feature': fake.word(), 'duration': random.randint(1, 3600)}
            )
            events.append(event)
    
    db.add_all(events)
    db.commit()
    
    # Generate Revenue
    revenues = []
    start_date = datetime.now() - timedelta(days=365)
    for i in range(365):
        current_date = start_date + timedelta(days=i)
        daily_revenue = PyDecimal(random.uniform(1000, 5000))
        
        revenue = Revenue(
            date=current_date.date(),
            amount=daily_revenue,
            source='subscriptions',
            user_id=random.choice(users).id if users else None
        )
        revenues.append(revenue)
    
    db.add_all(revenues)
    db.commit()
    
    return {
        'users': len(users),
        'subscriptions': len(subscriptions), 
        'events': len(events),
        'revenue_records': len(revenues)
    } 
