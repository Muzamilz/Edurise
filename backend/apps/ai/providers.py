import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
from decimal import Decimal

import google.generativeai as genai
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def generate_response(self, messages: List[Dict], context: Optional[Dict] = None) -> Tuple[str, int, int]:
        """Generate AI response for chat. Returns (response, tokens_used, response_time_ms)"""
        pass
    
    @abstractmethod
    def generate_summary(self, content: str, content_type: str = 'text') -> Tuple[str, List[str], int, int]:
        """Generate content summary. Returns (summary, key_points, tokens_used, generation_time_ms)"""
        pass
    
    @abstractmethod
    def generate_quiz(self, content: str, num_questions: int = 5, difficulty: str = 'medium') -> Tuple[List[Dict], int, int]:
        """Generate quiz questions. Returns (questions, tokens_used, generation_time_ms)"""
        pass


class GeminiProvider(AIProvider):
    """Enhanced Gemini AI provider implementation with rate limiting and cost tracking"""
    
    # Token cost estimates (approximate, based on Gemini pricing)
    INPUT_TOKEN_COST = 0.00025 / 1000  # $0.00025 per 1K tokens
    OUTPUT_TOKEN_COST = 0.0005 / 1000  # $0.0005 per 1K tokens
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.8,
            top_k=40,
            max_output_tokens=2048,
        )
    
    def generate_response(self, messages: List[Dict], context: Optional[Dict] = None) -> Tuple[str, int, int]:
        """Generate AI response for chat with enhanced context awareness"""
        start_time = time.time()
        
        try:
            # Build enhanced prompt with context
            prompt = self._build_tutor_prompt(messages, context)
            
            # Generate response with retry logic
            response = self._generate_with_retry(prompt)
            
            # Calculate metrics
            response_time_ms = int((time.time() - start_time) * 1000)
            tokens_used = self._estimate_tokens(prompt + response.text)
            
            return response.text, tokens_used, response_time_ms
            
        except Exception as e:
            logger.error(f"Gemini chat generation error: {str(e)}")
            raise Exception(f"AI service temporarily unavailable: {str(e)}")
    
    def generate_summary(self, content: str, content_type: str = 'text') -> Tuple[str, List[str], int, int]:
        """Generate enhanced content summary with key points extraction"""
        start_time = time.time()
        
        try:
            prompt = self._build_summary_prompt(content, content_type)
            
            response = self._generate_with_retry(prompt)
            
            # Parse response to extract summary and key points
            summary_data = self._parse_summary_response(response.text)
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            tokens_used = self._estimate_tokens(prompt + response.text)
            
            return summary_data['summary'], summary_data['key_points'], tokens_used, generation_time_ms
            
        except Exception as e:
            logger.error(f"Gemini summary generation error: {str(e)}")
            raise Exception(f"Summary generation failed: {str(e)}")
    
    def generate_quiz(self, content: str, num_questions: int = 5, difficulty: str = 'medium') -> Tuple[List[Dict], int, int]:
        """Generate quiz questions with enhanced formatting and validation"""
        start_time = time.time()
        
        try:
            prompt = self._build_quiz_prompt(content, num_questions, difficulty)
            
            response = self._generate_with_retry(prompt)
            
            # Parse and validate quiz questions
            questions = self._parse_quiz_response(response.text)
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            tokens_used = self._estimate_tokens(prompt + response.text)
            
            return questions, tokens_used, generation_time_ms
            
        except Exception as e:
            logger.error(f"Gemini quiz generation error: {str(e)}")
            raise Exception(f"Quiz generation failed: {str(e)}")
    
    def _generate_with_retry(self, prompt: str, max_retries: int = 3):
        """Generate content with retry logic for reliability"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
                
                if response.text:
                    return response
                else:
                    raise Exception("Empty response from Gemini")
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # Exponential backoff
                time.sleep(2 ** attempt)
                logger.warning(f"Gemini API retry {attempt + 1}/{max_retries}: {str(e)}")
        
        raise Exception("Max retries exceeded")
    
    def _build_tutor_prompt(self, messages: List[Dict], context: Optional[Dict] = None) -> str:
        """Build enhanced tutor prompt with context"""
        system_prompt = """You are an AI tutor for the Edurise learning platform. Your role is to:
        - Provide helpful, accurate, and educational responses
        - Adapt your teaching style to the student's level
        - Encourage learning and critical thinking
        - Stay focused on educational topics
        - Be patient and supportive
        
        Guidelines:
        - Keep responses concise but comprehensive
        - Use examples when helpful
        - Ask follow-up questions to encourage deeper learning
        - If unsure about something, acknowledge it honestly
        """
        
        # Add context if available
        if context:
            context_info = []
            if context.get('course_title'):
                context_info.append(f"Course: {context['course_title']}")
            if context.get('course_description'):
                context_info.append(f"Course Description: {context['course_description']}")
            if context.get('learning_objectives'):
                context_info.append(f"Learning Objectives: {', '.join(context['learning_objectives'])}")
            
            if context_info:
                system_prompt += f"\n\nCurrent Context:\n{chr(10).join(context_info)}"
        
        # Format conversation history
        conversation = [system_prompt]
        for msg in messages[-10:]:  # Keep last 10 messages for context
            role = "Student" if msg['role'] == 'user' else "Tutor"
            conversation.append(f"{role}: {msg['content']}")
        
        return "\n\n".join(conversation)
    
    def _build_summary_prompt(self, content: str, content_type: str) -> str:
        """Build enhanced summary prompt based on content type"""
        content_type_instructions = {
            'live_class': 'This is a transcript from a live class session.',
            'course_module': 'This is content from a course module.',
            'video': 'This is a transcript from a video lesson.',
            'text': 'This is educational text content.'
        }
        
        prompt = f"""
        {content_type_instructions.get(content_type, 'This is educational content.')}
        
        Please analyze the following content and provide:
        1. A comprehensive summary (2-3 paragraphs)
        2. Key learning points (5-7 bullet points)
        
        Content to summarize:
        {content}
        
        Please format your response as JSON:
        {{
            "summary": "Your comprehensive summary here...",
            "key_points": [
                "Key point 1",
                "Key point 2",
                "Key point 3",
                "Key point 4",
                "Key point 5"
            ]
        }}
        """
        
        return prompt
    
    def _build_quiz_prompt(self, content: str, num_questions: int, difficulty: str) -> str:
        """Build enhanced quiz generation prompt"""
        difficulty_instructions = {
            'easy': 'Focus on basic concepts and definitions. Questions should test recall and understanding.',
            'medium': 'Include application and analysis questions. Test understanding and ability to apply concepts.',
            'hard': 'Include synthesis and evaluation questions. Test critical thinking and complex problem-solving.'
        }
        
        prompt = f"""
        Create {num_questions} multiple choice questions based on the following educational content.
        
        Difficulty Level: {difficulty.title()}
        {difficulty_instructions.get(difficulty, '')}
        
        Content:
        {content}
        
        Requirements for each question:
        - Clear, unambiguous question text
        - 4 plausible answer options (A, B, C, D)
        - Only one correct answer
        - Brief explanation of why the correct answer is right
        - Questions should test different aspects of the content
        
        Format your response as valid JSON:
        {{
            "questions": [
                {{
                    "question": "Question text here?",
                    "options": [
                        "Option A text",
                        "Option B text", 
                        "Option C text",
                        "Option D text"
                    ],
                    "correct_answer": 0,
                    "explanation": "Explanation of why option A is correct..."
                }}
            ]
        }}
        """
        
        return prompt
    
    def _parse_summary_response(self, response_text: str) -> Dict:
        """Parse and validate summary response"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                summary_data = json.loads(json_str)
                
                # Validate required fields
                if 'summary' in summary_data and 'key_points' in summary_data:
                    return summary_data
            
            # Fallback: parse manually if JSON parsing fails
            lines = response_text.strip().split('\n')
            summary = ""
            key_points = []
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if 'summary' in line.lower() and ':' in line:
                    current_section = 'summary'
                    summary = line.split(':', 1)[1].strip()
                elif 'key' in line.lower() and 'point' in line.lower():
                    current_section = 'key_points'
                elif current_section == 'summary' and not line.startswith('-') and not line.startswith('•'):
                    summary += " " + line
                elif current_section == 'key_points' and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    key_points.append(line.lstrip('-•* '))
            
            return {
                'summary': summary.strip() or "Summary could not be generated.",
                'key_points': key_points or ["Key points could not be extracted."]
            }
            
        except Exception as e:
            logger.error(f"Error parsing summary response: {str(e)}")
            return {
                'summary': "Error generating summary.",
                'key_points': ["Unable to extract key points."]
            }
    
    def _parse_quiz_response(self, response_text: str) -> List[Dict]:
        """Parse and validate quiz response"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                quiz_data = json.loads(json_str)
                
                if 'questions' in quiz_data:
                    questions = quiz_data['questions']
                    
                    # Validate each question
                    validated_questions = []
                    for q in questions:
                        if self._validate_quiz_question(q):
                            validated_questions.append(q)
                    
                    return validated_questions
            
            # Fallback: return empty list if parsing fails
            logger.warning("Could not parse quiz response, returning empty list")
            return []
            
        except Exception as e:
            logger.error(f"Error parsing quiz response: {str(e)}")
            return []
    
    def _validate_quiz_question(self, question: Dict) -> bool:
        """Validate a single quiz question structure"""
        required_fields = ['question', 'options', 'correct_answer', 'explanation']
        
        # Check all required fields exist
        for field in required_fields:
            if field not in question:
                return False
        
        # Validate options (should be a list with 4 items)
        if not isinstance(question['options'], list) or len(question['options']) != 4:
            return False
        
        # Validate correct_answer (should be 0-3)
        if not isinstance(question['correct_answer'], int) or question['correct_answer'] not in range(4):
            return False
        
        return True
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for cost calculation"""
        # Rough estimation: ~4 characters per token for English text
        return len(text) // 4
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate cost based on token usage"""
        input_cost = Decimal(str(input_tokens * self.INPUT_TOKEN_COST))
        output_cost = Decimal(str(output_tokens * self.OUTPUT_TOKEN_COST))
        return input_cost + output_cost
