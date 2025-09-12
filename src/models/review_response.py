from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class ReviewResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    response_type = db.Column(db.String(50), nullable=True)  # ai_generated, manual, template
    tone = db.Column(db.String(50), nullable=True)  # professional, friendly, apologetic, grateful
    status = db.Column(db.String(20), default='draft')  # draft, approved, posted, rejected
    
    # AI generation metadata
    ai_model_used = db.Column(db.String(50), nullable=True)
    generation_prompt = db.Column(db.Text, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    
    # Approval workflow
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Platform posting
    posted_at = db.Column(db.DateTime, nullable=True)
    platform_response_id = db.Column(db.String(100), nullable=True)
    posting_error = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ReviewResponse {self.id} for Review {self.review_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'review_id': self.review_id,
            'response_text': self.response_text,
            'response_type': self.response_type,
            'tone': self.tone,
            'status': self.status,
            'ai_model_used': self.ai_model_used,
            'generation_prompt': self.generation_prompt,
            'confidence_score': self.confidence_score,
            'created_by': self.created_by,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'platform_response_id': self.platform_response_id,
            'posting_error': self.posting_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

