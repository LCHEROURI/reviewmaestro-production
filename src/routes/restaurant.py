from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.models.restaurant import Restaurant
from datetime import datetime

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/restaurants', methods=['GET'])
def get_restaurants():
    """Get all restaurants for the authenticated user"""
    # In a real implementation, you'd get user_id from JWT token
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    restaurants = Restaurant.query.filter_by(owner_id=user_id).all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

@restaurant_bp.route('/restaurants', methods=['POST'])
def create_restaurant():
    """Create a new restaurant"""
    data = request.json
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Restaurant name is required'}), 400
    if not data.get('owner_id'):
        return jsonify({'error': 'Owner ID is required'}), 400
    
    # Check if user exists
    user = User.query.get(data['owner_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    restaurant = Restaurant(
        name=data['name'],
        address=data.get('address'),
        phone=data.get('phone'),
        email=data.get('email'),
        website=data.get('website'),
        cuisine_type=data.get('cuisine_type'),
        description=data.get('description'),
        owner_id=data['owner_id'],
        google_place_id=data.get('google_place_id'),
        yelp_business_id=data.get('yelp_business_id'),
        tripadvisor_location_id=data.get('tripadvisor_location_id')
    )
    
    db.session.add(restaurant)
    db.session.commit()
    return jsonify(restaurant.to_dict()), 201

@restaurant_bp.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    """Get a specific restaurant"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    return jsonify(restaurant.to_dict())

@restaurant_bp.route('/restaurants/<int:restaurant_id>', methods=['PUT'])
def update_restaurant(restaurant_id):
    """Update a restaurant"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    data = request.json
    
    # Update fields if provided
    restaurant.name = data.get('name', restaurant.name)
    restaurant.address = data.get('address', restaurant.address)
    restaurant.phone = data.get('phone', restaurant.phone)
    restaurant.email = data.get('email', restaurant.email)
    restaurant.website = data.get('website', restaurant.website)
    restaurant.cuisine_type = data.get('cuisine_type', restaurant.cuisine_type)
    restaurant.description = data.get('description', restaurant.description)
    restaurant.google_place_id = data.get('google_place_id', restaurant.google_place_id)
    restaurant.yelp_business_id = data.get('yelp_business_id', restaurant.yelp_business_id)
    restaurant.tripadvisor_location_id = data.get('tripadvisor_location_id', restaurant.tripadvisor_location_id)
    restaurant.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(restaurant.to_dict())

@restaurant_bp.route('/restaurants/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    """Delete a restaurant"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

@restaurant_bp.route('/restaurants/<int:restaurant_id>/stats', methods=['GET'])
def get_restaurant_stats(restaurant_id):
    """Get statistics for a restaurant"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Import here to avoid circular imports
    from src.models.review import Review
    
    total_reviews = Review.query.filter_by(restaurant_id=restaurant_id).count()
    positive_reviews = Review.query.filter_by(restaurant_id=restaurant_id, sentiment='positive').count()
    negative_reviews = Review.query.filter_by(restaurant_id=restaurant_id, sentiment='negative').count()
    neutral_reviews = Review.query.filter_by(restaurant_id=restaurant_id, sentiment='neutral').count()
    
    # Calculate average rating
    reviews_with_rating = Review.query.filter(
        Review.restaurant_id == restaurant_id,
        Review.rating.isnot(None)
    ).all()
    
    avg_rating = None
    if reviews_with_rating:
        avg_rating = sum(review.rating for review in reviews_with_rating) / len(reviews_with_rating)
    
    stats = {
        'restaurant_id': restaurant_id,
        'restaurant_name': restaurant.name,
        'total_reviews': total_reviews,
        'positive_reviews': positive_reviews,
        'negative_reviews': negative_reviews,
        'neutral_reviews': neutral_reviews,
        'average_rating': round(avg_rating, 2) if avg_rating else None,
        'response_rate': 0  # TODO: Calculate response rate
    }
    
    return jsonify(stats)

