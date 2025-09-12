from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    cuisine_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Platform integration settings
    google_place_id = db.Column(db.String(100), nullable=True)
    yelp_business_id = db.Column(db.String(100), nullable=True)
    tripadvisor_location_id = db.Column(db.String(100), nullable=True)
    
    # Relationship with reviews
    reviews = db.relationship('Review', backref='restaurant', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'cuisine_type': self.cuisine_type,
            'description': self.description,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'google_place_id': self.google_place_id,
            'yelp_business_id': self.yelp_business_id,
            'tripadvisor_location_id': self.tripadvisor_location_id
        }

