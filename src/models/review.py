from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # google, yelp, tripadvisor
    platform_review_id = db.Column(db.String(100), nullable=False)
    author_name = db.Column(db.String(100), nullable=True)
    author_profile_url = db.Column(db.String(200), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    review_text = db.Column(db.Text, nullable=True)
    review_date = db.Column(db.DateTime, nullable=True)
    review_url = db.Column(db.String(300), nullable=True)
    
    # AI Analysis fields
    sentiment = db.Column(db.String(20), nullable=True)  # positive, negative, neutral
    sentiment_score = db.Column(db.Float, nullable=True)  # -1 to 1
    key_topics = db.Column(db.Text, nullable=True)  # JSON string of topics
    urgency_level = db.Column(db.String(20), nullable=True)  # low, medium, high
    
    # Response tracking
    response_generated = db.Column(db.Boolean, default=False)
    response_posted = db.Column(db.Boolean, default=False)
    response_date = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with responses
    responses = db.relationship('ReviewResponse', backref='review', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Review {self.platform}:{self.platform_review_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'platform': self.platform,
            'platform_review_id': self.platform_review_id,
            'author_name': self.author_name,
            'author_profile_url': self.author_profile_url,
            'rating': self.rating,
            'review_text': self.review_text,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            'review_url': self.review_url,
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score,
            'key_topics': self.key_topics,
            'urgency_level': self.urgency_level,
            'response_generated': self.response_generated,
            'response_posted': self.response_posted,
            'response_date': self.response_date.isoformat() if self.response_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

