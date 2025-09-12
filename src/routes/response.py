from flask import Blueprint, jsonify, request
from src.models.user import db
from src.models.review import Review
from src.models.review_response import ReviewResponse
from datetime import datetime
import os

response_bp = Blueprint('response', __name__)

@response_bp.route('/responses', methods=['GET'])
def get_responses():
    """Get responses with optional filtering"""
    review_id = request.args.get('review_id', type=int)
    status = request.args.get('status')
    limit = request.args.get('limit', type=int, default=50)
    
    query = ReviewResponse.query
    
    # Filter by review
    if review_id:
        query = query.filter_by(review_id=review_id)
    
    # Filter by status
    if status:
        query = query.filter_by(status=status)
    
    # Order by most recent first
    responses = query.order_by(ReviewResponse.created_at.desc()).limit(limit).all()
    
    return jsonify([response.to_dict() for response in responses])

@response_bp.route('/responses', methods=['POST'])
def create_response():
    """Create a new response"""
    data = request.json
    
    # Validate required fields
    if not data.get('review_id'):
        return jsonify({'error': 'review_id is required'}), 400
    if not data.get('response_text'):
        return jsonify({'error': 'response_text is required'}), 400
    
    # Check if review exists
    review = Review.query.get(data['review_id'])
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    response = ReviewResponse(
        review_id=data['review_id'],
        response_text=data['response_text'],
        response_type=data.get('response_type', 'manual'),
        tone=data.get('tone'),
        status=data.get('status', 'draft'),
        ai_model_used=data.get('ai_model_used'),
        generation_prompt=data.get('generation_prompt'),
        confidence_score=data.get('confidence_score'),
        created_by=data.get('created_by')
    )
    
    db.session.add(response)
    db.session.commit()
    return jsonify(response.to_dict()), 201

@response_bp.route('/responses/<int:response_id>', methods=['GET'])
def get_response(response_id):
    """Get a specific response"""
    response = ReviewResponse.query.get_or_404(response_id)
    return jsonify(response.to_dict())

@response_bp.route('/responses/<int:response_id>', methods=['PUT'])
def update_response(response_id):
    """Update a response"""
    response = ReviewResponse.query.get_or_404(response_id)
    data = request.json
    
    # Update fields if provided
    if 'response_text' in data:
        response.response_text = data['response_text']
    if 'tone' in data:
        response.tone = data['tone']
    if 'status' in data:
        response.status = data['status']
        if data['status'] == 'approved':
            response.approved_by = data.get('approved_by')
            response.approved_at = datetime.utcnow()
    
    response.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(response.to_dict())

@response_bp.route('/responses/<int:response_id>', methods=['DELETE'])
def delete_response(response_id):
    """Delete a response"""
    response = ReviewResponse.query.get_or_404(response_id)
    db.session.delete(response)
    db.session.commit()
    return '', 204

@response_bp.route('/responses/<int:response_id>/approve', methods=['POST'])
def approve_response(response_id):
    """Approve a response"""
    response = ReviewResponse.query.get_or_404(response_id)
    data = request.json
    
    response.status = 'approved'
    response.approved_by = data.get('approved_by')
    response.approved_at = datetime.utcnow()
    response.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(response.to_dict())

@response_bp.route('/responses/<int:response_id>/reject', methods=['POST'])
def reject_response(response_id):
    """Reject a response"""
    response = ReviewResponse.query.get_or_404(response_id)
    
    response.status = 'rejected'
    response.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(response.to_dict())

@response_bp.route('/reviews/<int:review_id>/generate-response', methods=['POST'])
def generate_response(review_id):
    """Generate an AI response for a review"""
    review = Review.query.get_or_404(review_id)
    data = request.json
    
    if not review.review_text:
        return jsonify({'error': 'No review text available for response generation'}), 400
    
    # Get restaurant info for context
    restaurant = review.restaurant
    tone = data.get('tone', 'professional')
    custom_instructions = data.get('custom_instructions')
    
    try:
        from src.services.ai_service import ai_service
        ai_response = ai_service.generate_response(
            review.review_text,
            restaurant.name,
            review.sentiment,
            tone,
            custom_instructions
        )
        
        # Create the response record
        response = ReviewResponse(
            review_id=review_id,
            response_text=ai_response['response_text'],
            response_type='ai_generated',
            tone=tone,
            status='draft',
            ai_model_used=ai_response['model_used'],
            generation_prompt=f"Generate a {tone} response to this {review.sentiment} review",
            confidence_score=ai_response['confidence_score'],
            created_by=data.get('user_id')
        )
        
        db.session.add(response)
        
        # Update review to mark response as generated
        review.response_generated = True
        review.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Response generated successfully',
            'response': response.to_dict()
        })
        
    except Exception as e:
        # Fallback to mock response generation
        if review.sentiment == 'positive':
            mock_response = f"Thank you so much for your wonderful review! We're thrilled to hear that you enjoyed your experience at {restaurant.name}. We look forward to welcoming you back soon!"
        elif review.sentiment == 'negative':
            mock_response = f"Thank you for your feedback. We sincerely apologize for not meeting your expectations during your visit to {restaurant.name}. We take all feedback seriously and would love the opportunity to make things right. Please contact us directly so we can address your concerns."
        else:
            mock_response = f"Thank you for taking the time to review {restaurant.name}. We appreciate your feedback and hope to see you again soon!"
        
        # Create the response record
        response = ReviewResponse(
            review_id=review_id,
            response_text=mock_response,
            response_type='ai_generated',
            tone=tone,
            status='draft',
            ai_model_used='fallback_v1',
            generation_prompt=f"Generate a {tone} response to this {review.sentiment} review",
            confidence_score=0.5,
            created_by=data.get('user_id')
        )
        
        db.session.add(response)
        
        # Update review to mark response as generated
        review.response_generated = True
        review.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Response generated successfully (fallback mode)',
            'response': response.to_dict(),
            'error': str(e)
        })

@response_bp.route('/reviews/<int:review_id>/generate-multiple-responses', methods=['POST'])
def generate_multiple_responses(review_id):
    """Generate multiple AI response options for a review"""
    review = Review.query.get_or_404(review_id)
    data = request.json
    
    if not review.review_text:
        return jsonify({'error': 'No review text available for response generation'}), 400
    
    tones = data.get('tones', ['professional', 'friendly', 'apologetic'] if review.sentiment == 'negative' else ['professional', 'friendly', 'grateful'])
    restaurant = review.restaurant
    responses = []
    
    try:
        from src.services.ai_service import ai_service
        ai_responses = ai_service.generate_multiple_responses(
            review.review_text,
            restaurant.name,
            review.sentiment,
            tones
        )
        
        for ai_response in ai_responses:
            response = ReviewResponse(
                review_id=review_id,
                response_text=ai_response['response_text'],
                response_type='ai_generated',
                tone=ai_response['tone'],
                status='draft',
                ai_model_used=ai_response['model_used'],
                generation_prompt=f"Generate a {ai_response['tone']} response to this {review.sentiment} review",
                confidence_score=ai_response['confidence_score'],
                created_by=data.get('user_id')
            )
            
            db.session.add(response)
            responses.append(response)
        
    except Exception as e:
        # Fallback to mock response generation
        for tone in tones:
            if review.sentiment == 'positive':
                if tone == 'professional':
                    mock_response = f"Thank you for your positive review of {restaurant.name}. We appreciate your feedback and look forward to serving you again."
                elif tone == 'friendly':
                    mock_response = f"Wow, thank you so much! We're absolutely delighted that you had such a great time at {restaurant.name}. Can't wait to see you again! 😊"
                else:
                    mock_response = f"Thank you for your kind words about {restaurant.name}. We're grateful for customers like you!"
            elif review.sentiment == 'negative':
                if tone == 'professional':
                    mock_response = f"Thank you for your feedback regarding your experience at {restaurant.name}. We take all concerns seriously and would appreciate the opportunity to discuss this matter further."
                elif tone == 'apologetic':
                    mock_response = f"We are deeply sorry that your experience at {restaurant.name} did not meet your expectations. This is not the standard we strive for, and we would very much like to make this right."
                else:
                    mock_response = f"We sincerely apologize for the issues you experienced at {restaurant.name}. Your feedback helps us improve, and we hope you'll give us another chance."
            else:
                mock_response = f"Thank you for taking the time to review {restaurant.name}. We value all feedback from our guests."
            
            response = ReviewResponse(
                review_id=review_id,
                response_text=mock_response,
                response_type='ai_generated',
                tone=tone,
                status='draft',
                ai_model_used='fallback_v1',
                generation_prompt=f"Generate a {tone} response to this {review.sentiment} review",
                confidence_score=0.5,
                created_by=data.get('user_id')
            )
            
            db.session.add(response)
            responses.append(response)
    
    # Update review to mark response as generated
    review.response_generated = True
    review.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'Generated {len(responses)} response options',
        'responses': [response.to_dict() for response in responses]
    })

