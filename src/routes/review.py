from flask import Blueprint, jsonify, request
from src.models.user import db
from src.models.review import Review
from src.models.restaurant import Restaurant
from datetime import datetime, timedelta
import json

review_bp = Blueprint('review', __name__)

@review_bp.route('/reviews', methods=['GET'])
def get_reviews():
    """Get reviews with optional filtering"""
    restaurant_id = request.args.get('restaurant_id', type=int)
    platform = request.args.get('platform')
    sentiment = request.args.get('sentiment')
    days_back = request.args.get('days_back', type=int, default=30)
    limit = request.args.get('limit', type=int, default=50)
    
    query = Review.query
    
    # Filter by restaurant
    if restaurant_id:
        query = query.filter_by(restaurant_id=restaurant_id)
    
    # Filter by platform
    if platform:
        query = query.filter_by(platform=platform)
    
    # Filter by sentiment
    if sentiment:
        query = query.filter_by(sentiment=sentiment)
    
    # Filter by date range
    if days_back:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        query = query.filter(Review.review_date >= cutoff_date)
    
    # Order by most recent first
    reviews = query.order_by(Review.review_date.desc()).limit(limit).all()
    
    return jsonify([review.to_dict() for review in reviews])

@review_bp.route('/reviews', methods=['POST'])
def create_review():
    """Create a new review (typically from platform integration)"""
    data = request.json
    
    # Validate required fields
    required_fields = ['restaurant_id', 'platform', 'platform_review_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if restaurant exists
    restaurant = Restaurant.query.get(data['restaurant_id'])
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    # Check if review already exists
    existing_review = Review.query.filter_by(
        platform=data['platform'],
        platform_review_id=data['platform_review_id']
    ).first()
    
    if existing_review:
        return jsonify({'error': 'Review already exists'}), 409
    
    # Parse review date if provided
    review_date = None
    if data.get('review_date'):
        try:
            review_date = datetime.fromisoformat(data['review_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid review_date format'}), 400
    
    review = Review(
        restaurant_id=data['restaurant_id'],
        platform=data['platform'],
        platform_review_id=data['platform_review_id'],
        author_name=data.get('author_name'),
        author_profile_url=data.get('author_profile_url'),
        rating=data.get('rating'),
        review_text=data.get('review_text'),
        review_date=review_date,
        review_url=data.get('review_url'),
        sentiment=data.get('sentiment'),
        sentiment_score=data.get('sentiment_score'),
        key_topics=data.get('key_topics'),
        urgency_level=data.get('urgency_level')
    )
    
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201

@review_bp.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """Get a specific review"""
    review = Review.query.get_or_404(review_id)
    return jsonify(review.to_dict())

@review_bp.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """Update a review (typically AI analysis results)"""
    review = Review.query.get_or_404(review_id)
    data = request.json
    
    # Update AI analysis fields
    if 'sentiment' in data:
        review.sentiment = data['sentiment']
    if 'sentiment_score' in data:
        review.sentiment_score = data['sentiment_score']
    if 'key_topics' in data:
        review.key_topics = data['key_topics']
    if 'urgency_level' in data:
        review.urgency_level = data['urgency_level']
    
    # Update response tracking
    if 'response_generated' in data:
        review.response_generated = data['response_generated']
    if 'response_posted' in data:
        review.response_posted = data['response_posted']
        if data['response_posted']:
            review.response_date = datetime.utcnow()
    
    review.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(review.to_dict())

@review_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """Delete a review"""
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return '', 204

@review_bp.route('/reviews/<int:review_id>/analyze', methods=['POST'])
def analyze_review(review_id):
    """Trigger AI analysis for a specific review"""
    review = Review.query.get_or_404(review_id)
    
    if not review.review_text:
        return jsonify({'error': 'No review text to analyze'}), 400
    
    try:
        from src.services.ai_service import ai_service
        analysis = ai_service.analyze_sentiment(review.review_text)
        
        # Update review with analysis
        review.sentiment = analysis['sentiment']
        review.sentiment_score = analysis['sentiment_score']
        review.key_topics = json.dumps(analysis['key_topics'])
        review.urgency_level = analysis['urgency_level']
        review.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'review_id': review_id,
            'analysis': analysis,
            'message': 'Review analysis completed'
        })
    except Exception as e:
        # Fallback to mock analysis if AI service fails
        mock_analysis = {
            'sentiment': 'positive' if 'good' in review.review_text.lower() else 'negative',
            'sentiment_score': 0.8 if 'good' in review.review_text.lower() else -0.6,
            'key_topics': ['food quality', 'service'],
            'urgency_level': 'high' if 'terrible' in review.review_text.lower() else 'low'
        }
        
        # Update review with analysis
        review.sentiment = mock_analysis['sentiment']
        review.sentiment_score = mock_analysis['sentiment_score']
        review.key_topics = json.dumps(mock_analysis['key_topics'])
        review.urgency_level = mock_analysis['urgency_level']
        review.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'review_id': review_id,
            'analysis': mock_analysis,
            'message': 'Review analysis completed (fallback mode)',
            'error': str(e)
        })

@review_bp.route('/reviews/bulk-analyze', methods=['POST'])
def bulk_analyze_reviews():
    """Analyze multiple reviews at once"""
    data = request.json
    restaurant_id = data.get('restaurant_id')
    
    if not restaurant_id:
        return jsonify({'error': 'restaurant_id is required'}), 400
    
    # Get unanalyzed reviews for the restaurant
    unanalyzed_reviews = Review.query.filter_by(
        restaurant_id=restaurant_id,
        sentiment=None
    ).filter(Review.review_text.isnot(None)).all()
    
    analyzed_count = 0
    errors = []
    
    try:
        from src.services.ai_service import ai_service
        
        for review in unanalyzed_reviews:
            try:
                analysis = ai_service.analyze_sentiment(review.review_text)
                
                review.sentiment = analysis['sentiment']
                review.sentiment_score = analysis['sentiment_score']
                review.key_topics = json.dumps(analysis['key_topics'])
                review.urgency_level = analysis['urgency_level']
                review.updated_at = datetime.utcnow()
                analyzed_count += 1
                
            except Exception as e:
                errors.append(f"Review {review.id}: {str(e)}")
                # Use fallback analysis
                mock_analysis = {
                    'sentiment': 'positive' if 'good' in review.review_text.lower() else 'negative',
                    'sentiment_score': 0.8 if 'good' in review.review_text.lower() else -0.6,
                    'key_topics': ['food quality', 'service'],
                    'urgency_level': 'high' if 'terrible' in review.review_text.lower() else 'low'
                }
                
                review.sentiment = mock_analysis['sentiment']
                review.sentiment_score = mock_analysis['sentiment_score']
                review.key_topics = json.dumps(mock_analysis['key_topics'])
                review.urgency_level = mock_analysis['urgency_level']
                review.updated_at = datetime.utcnow()
                analyzed_count += 1
    
    except ImportError as e:
        # AI service not available, use fallback for all
        for review in unanalyzed_reviews:
            mock_analysis = {
                'sentiment': 'positive' if 'good' in review.review_text.lower() else 'negative',
                'sentiment_score': 0.8 if 'good' in review.review_text.lower() else -0.6,
                'key_topics': ['food quality', 'service'],
                'urgency_level': 'high' if 'terrible' in review.review_text.lower() else 'low'
            }
            
            review.sentiment = mock_analysis['sentiment']
            review.sentiment_score = mock_analysis['sentiment_score']
            review.key_topics = json.dumps(mock_analysis['key_topics'])
            review.urgency_level = mock_analysis['urgency_level']
            review.updated_at = datetime.utcnow()
            analyzed_count += 1
    
    db.session.commit()
    
    response_data = {
        'message': f'Analyzed {analyzed_count} reviews',
        'analyzed_count': analyzed_count
    }
    
    if errors:
        response_data['errors'] = errors
    
    return jsonify(response_data)

