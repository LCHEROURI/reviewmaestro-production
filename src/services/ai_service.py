import os
import json
from typing import Dict, List, Optional
import openai
from datetime import datetime

class AIService:
    """Service for AI-powered review analysis and response generation"""
    
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY'),
            base_url=os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
    
    def analyze_sentiment(self, review_text: str) -> Dict:
        """
        Analyze the sentiment of a review text
        
        Args:
            review_text: The review text to analyze
            
        Returns:
            Dict containing sentiment, score, and key topics
        """
        try:
            prompt = f"""
            Analyze the following restaurant review and provide:
            1. Sentiment (positive, negative, or neutral)
            2. Sentiment score (-1 to 1, where -1 is very negative and 1 is very positive)
            3. Key topics mentioned (as a list)
            4. Urgency level (low, medium, high) based on how critical the issues are
            
            Review: "{review_text}"
            
            Respond in JSON format:
            {{
                "sentiment": "positive|negative|neutral",
                "sentiment_score": 0.0,
                "key_topics": ["topic1", "topic2"],
                "urgency_level": "low|medium|high"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing restaurant reviews. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            # Return fallback analysis
            return {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "key_topics": ["general feedback"],
                "urgency_level": "low"
            }
    
    def generate_response(self, review_text: str, restaurant_name: str, 
                         sentiment: str = None, tone: str = "professional",
                         custom_instructions: str = None) -> Dict:
        """
        Generate a response to a restaurant review
        
        Args:
            review_text: The original review text
            restaurant_name: Name of the restaurant
            sentiment: Sentiment of the review (positive, negative, neutral)
            tone: Desired tone for the response
            custom_instructions: Additional instructions for response generation
            
        Returns:
            Dict containing the generated response and metadata
        """
        try:
            # Build the prompt based on sentiment and tone
            tone_instructions = {
                "professional": "Use a professional, courteous tone",
                "friendly": "Use a warm, friendly, and personable tone",
                "apologetic": "Use an apologetic and empathetic tone, focusing on making things right",
                "grateful": "Use a grateful and appreciative tone"
            }
            
            sentiment_context = ""
            if sentiment == "positive":
                sentiment_context = "This is a positive review. Express gratitude and encourage future visits."
            elif sentiment == "negative":
                sentiment_context = "This is a negative review. Acknowledge concerns, apologize if appropriate, and offer to make things right."
            else:
                sentiment_context = "This is a neutral review. Thank them for their feedback."
            
            prompt = f"""
            You are writing a response to a restaurant review on behalf of {restaurant_name}.
            
            Review: "{review_text}"
            
            Instructions:
            - {tone_instructions.get(tone, 'Use a professional tone')}
            - {sentiment_context}
            - Keep the response concise (2-3 sentences maximum)
            - Be authentic and avoid overly generic responses
            - Include the restaurant name naturally
            - If it's a negative review, offer a way to contact the restaurant directly
            {f"- Additional instructions: {custom_instructions}" if custom_instructions else ""}
            
            Generate only the response text, no additional formatting or quotes.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at writing professional restaurant responses to customer reviews. Always write in a natural, human-like manner."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            return {
                "response_text": generated_text,
                "model_used": "gpt-3.5-turbo",
                "tone": tone,
                "confidence_score": 0.85,  # Could be calculated based on model confidence
                "generation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error in response generation: {e}")
            # Return fallback response
            fallback_responses = {
                "positive": f"Thank you so much for your wonderful review! We're thrilled you enjoyed your experience at {restaurant_name} and look forward to welcoming you back soon.",
                "negative": f"Thank you for your feedback about your experience at {restaurant_name}. We take all concerns seriously and would love the opportunity to make things right. Please contact us directly.",
                "neutral": f"Thank you for taking the time to review {restaurant_name}. We appreciate your feedback and hope to see you again soon."
            }
            
            return {
                "response_text": fallback_responses.get(sentiment, fallback_responses["neutral"]),
                "model_used": "fallback",
                "tone": tone,
                "confidence_score": 0.5,
                "generation_timestamp": datetime.utcnow().isoformat()
            }
    
    def generate_multiple_responses(self, review_text: str, restaurant_name: str,
                                  sentiment: str = None, tones: List[str] = None) -> List[Dict]:
        """
        Generate multiple response options with different tones
        
        Args:
            review_text: The original review text
            restaurant_name: Name of the restaurant
            sentiment: Sentiment of the review
            tones: List of tones to generate responses for
            
        Returns:
            List of response dictionaries
        """
        if not tones:
            tones = ["professional", "friendly", "apologetic"] if sentiment == "negative" else ["professional", "friendly", "grateful"]
        
        responses = []
        for tone in tones:
            response = self.generate_response(review_text, restaurant_name, sentiment, tone)
            response["tone"] = tone
            responses.append(response)
        
        return responses
    
    def extract_key_issues(self, review_text: str) -> List[str]:
        """
        Extract specific issues or compliments from a review
        
        Args:
            review_text: The review text to analyze
            
        Returns:
            List of key issues or points mentioned
        """
        try:
            prompt = f"""
            Extract the key specific issues, compliments, or points mentioned in this restaurant review.
            Focus on concrete, actionable items.
            
            Review: "{review_text}"
            
            Return as a JSON array of strings:
            ["issue1", "issue2", "compliment1"]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting key points from restaurant reviews. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            issues = json.loads(response.choices[0].message.content)
            return issues if isinstance(issues, list) else []
            
        except Exception as e:
            print(f"Error extracting key issues: {e}")
            return []

# Global instance
ai_service = AIService()

