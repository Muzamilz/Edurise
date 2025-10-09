import google.generativeai as genai
from django.conf import settings
from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def generate_response(self, messages, context=None):
        pass
    
    @abstractmethod
    def generate_summary(self, content):
        pass
    
    @abstractmethod
    def generate_quiz(self, content, num_questions=5):
        pass


class GeminiProvider(AIProvider):
    """Gemini AI provider implementation"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_response(self, messages, context=None):
        """Generate AI response for chat"""
        try:
            # Format messages for Gemini
            conversation_text = self._format_messages(messages)
            
            if context:
                conversation_text = f"Context: {context}\n\n{conversation_text}"
            
            response = self.model.generate_content(conversation_text)
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_summary(self, content):
        """Generate content summary"""
        try:
            prompt = f"""
            Please provide a concise summary of the following educational content:
            
            {content}
            
            Summary should be:
            - Clear and concise
            - Highlight key learning points
            - Be suitable for students
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_quiz(self, content, num_questions=5):
        """Generate quiz questions from content"""
        try:
            prompt = f"""
            Create {num_questions} multiple choice questions based on this content:
            
            {content}
            
            Format as JSON with this structure:
            {{
                "questions": [
                    {{
                        "question": "Question text",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": 0,
                        "explanation": "Why this is correct"
                    }}
                ]
            }}
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _format_messages(self, messages):
        """Format messages for Gemini API"""
        formatted = []
        for msg in messages:
            role = "User" if msg['role'] == 'user' else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)