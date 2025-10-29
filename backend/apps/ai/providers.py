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
    """Enhanced Gemini AI provider implementation with advanced features"""
    
    # Token cost estimates (approximate, based on Gemini pricing)
    INPUT_TOKEN_COST = 0.00025 / 1000  # $0.00025 per 1K tokens
    OUTPUT_TOKEN_COST = 0.0005 / 1000  # $0.0005 per 1K tokens
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise Exception("Gemini API key not configured")
            
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use the most efficient model available
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.8,
            top_k=40,
            max_output_tokens=2048,
        )
        
        # Enhanced configuration
        self.max_retries = getattr(settings, 'AI_MAX_RETRIES', 3)
        self.cache_timeout = getattr(settings, 'AI_CACHE_TIMEOUT', 3600)
        self.quality_threshold = getattr(settings, 'AI_RESPONSE_QUALITY_THRESHOLD', 0.8)
    
    def generate_response(self, messages: List[Dict], context: Optional[Dict] = None) -> Tuple[str, int, int]:
        """Generate AI response for chat with enhanced context awareness and caching"""
        start_time = time.time()
        
        try:
            # Build enhanced prompt with context
            prompt = self._build_tutor_prompt(messages, context)
            
            # Check cache for similar conversations
            cache_key = self._generate_cache_key('chat', prompt[-500:])  # Use last 500 chars for cache key
            cached_response = cache.get(cache_key)
            
            if cached_response:
                logger.info("Using cached AI response")
                return cached_response['response'], cached_response['tokens'], cached_response['time_ms']
            
            # Generate response with retry logic
            response = self._generate_with_retry(prompt)
            
            # Calculate metrics
            response_time_ms = int((time.time() - start_time) * 1000)
            tokens_used = self._estimate_tokens(prompt + response.text)
            
            # Quality monitoring
            quality_score = self._assess_response_quality(response.text, messages)
            if quality_score < self.quality_threshold:
                logger.warning(f"Low quality AI response detected: {quality_score}")
            
            # Cache the response
            cache_data = {
                'response': response.text,
                'tokens': tokens_used,
                'time_ms': response_time_ms,
                'quality_score': quality_score
            }
            cache.set(cache_key, cache_data, self.cache_timeout)
            
            return response.text, tokens_used, response_time_ms
            
        except Exception as e:
            logger.error(f"Gemini chat generation error: {str(e)}")
            raise Exception(f"AI service temporarily unavailable: {str(e)}")
    
    def generate_summary(self, content: str, content_type: str = 'text') -> Tuple[str, List[str], int, int]:
        """Generate enhanced content summary with key points extraction and caching"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key('summary', content[:1000])  # Use first 1000 chars for cache key
            cached_summary = cache.get(cache_key)
            
            if cached_summary:
                logger.info("Using cached AI summary")
                return (
                    cached_summary['summary'], 
                    cached_summary['key_points'], 
                    cached_summary['tokens'], 
                    cached_summary['time_ms']
                )
            
            prompt = self._build_summary_prompt(content, content_type)
            
            response = self._generate_with_retry(prompt)
            
            # Parse response to extract summary and key points
            summary_data = self._parse_summary_response(response.text)
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            tokens_used = self._estimate_tokens(prompt + response.text)
            
            # Quality monitoring for summary
            quality_score = self._assess_summary_quality(summary_data['summary'], summary_data['key_points'])
            if quality_score < self.quality_threshold:
                logger.warning(f"Low quality AI summary detected: {quality_score}")
            
            # Cache the summary
            cache_data = {
                'summary': summary_data['summary'],
                'key_points': summary_data['key_points'],
                'tokens': tokens_used,
                'time_ms': generation_time_ms,
                'quality_score': quality_score
            }
            cache.set(cache_key, cache_data, self.cache_timeout)
            
            return summary_data['summary'], summary_data['key_points'], tokens_used, generation_time_ms
            
        except Exception as e:
            logger.error(f"Gemini summary generation error: {str(e)}")
            raise Exception(f"Summary generation failed: {str(e)}")
    
    def generate_quiz(self, content: str, num_questions: int = 5, difficulty: str = 'medium') -> Tuple[List[Dict], int, int]:
        """Generate quiz questions with enhanced formatting, validation and caching"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key('quiz', f"{content[:500]}_{num_questions}_{difficulty}")
            cached_quiz = cache.get(cache_key)
            
            if cached_quiz:
                logger.info("Using cached AI quiz")
                return cached_quiz['questions'], cached_quiz['tokens'], cached_quiz['time_ms']
            
            prompt = self._build_quiz_prompt(content, num_questions, difficulty)
            
            response = self._generate_with_retry(prompt)
            
            # Parse and validate quiz questions
            questions = self._parse_quiz_response(response.text)
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            tokens_used = self._estimate_tokens(prompt + response.text)
            
            # Quality monitoring for quiz
            quality_score = self._assess_quiz_quality(questions, num_questions)
            if quality_score < self.quality_threshold:
                logger.warning(f"Low quality AI quiz detected: {quality_score}")
            
            # Cache the quiz
            cache_data = {
                'questions': questions,
                'tokens': tokens_used,
                'time_ms': generation_time_ms,
                'quality_score': quality_score
            }
            cache.set(cache_key, cache_data, self.cache_timeout)
            
            return questions, tokens_used, generation_time_ms
            
        except Exception as e:
            logger.error(f"Gemini quiz generation error: {str(e)}")
            raise Exception(f"Quiz generation failed: {str(e)}")
    
    def _generate_with_retry(self, prompt: str):
        """Generate content with enhanced retry logic and error handling"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
                
                if response.text and response.text.strip():
                    # Log successful generation
                    logger.info(f"Gemini API success on attempt {attempt + 1}")
                    return response
                else:
                    raise Exception("Empty or whitespace-only response from Gemini")
                    
            except Exception as e:
                last_error = e
                
                # Log the specific error
                error_msg = str(e)
                if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                    logger.error(f"Gemini API quota/limit error: {error_msg}")
                    raise Exception("AI service quota exceeded. Please try again later.")
                elif "safety" in error_msg.lower():
                    logger.warning(f"Gemini safety filter triggered: {error_msg}")
                    raise Exception("Content filtered by AI safety systems. Please rephrase your request.")
                elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                    logger.warning(f"Gemini network error on attempt {attempt + 1}: {error_msg}")
                else:
                    logger.warning(f"Gemini API error on attempt {attempt + 1}: {error_msg}")
                
                # Don't retry on certain errors
                if "quota" in error_msg.lower() or "safety" in error_msg.lower():
                    raise e
                
                if attempt == self.max_retries - 1:
                    break
                
                # Exponential backoff with jitter
                backoff_time = (2 ** attempt) + (time.time() % 1)  # Add jitter
                logger.info(f"Retrying Gemini API in {backoff_time:.2f} seconds...")
                time.sleep(backoff_time)
        
        # If we get here, all retries failed
        logger.error(f"Gemini API failed after {self.max_retries} attempts. Last error: {last_error}")
        raise Exception(f"AI service temporarily unavailable after {self.max_retries} attempts: {str(last_error)}")
    
    def _build_tutor_prompt(self, messages: List[Dict], context: Optional[Dict] = None) -> str:
        """Build enhanced tutor prompt with context"""
        system_prompt = """You are the EduRise AI Assistant, exclusively designed to help users with the EduRise Learning Management System platform.

        STRICT GUIDELINES - ONLY respond to questions about:
        - EduRise platform features and functionality
        - How to use EduRise (courses, live classes, assignments, etc.)
        - EduRise pricing, plans, and subscriptions
        - Technical support for EduRise platform
        - Account management and settings in EduRise
        - Course enrollment and progress in EduRise
        - EduRise's AI tutoring, content summarization, and quiz generation features
        - Live classes, video conferencing, and virtual classroom features
        - Certificates, progress tracking, and analytics in EduRise
        - Payment methods and billing for EduRise services

        IMPORTANT RESTRICTIONS:
        - DO NOT answer general educational questions unrelated to EduRise
        - DO NOT provide tutoring on academic subjects (math, science, etc.)
        - DO NOT help with homework or assignments from other platforms
        - DO NOT discuss competitors or other learning platforms
        - If asked about non-EduRise topics, politely redirect to EduRise-specific help

        Response Style:
        - Be helpful and friendly about EduRise features
        - Keep responses focused on the platform
        - Provide specific guidance on using EduRise
        - Suggest relevant EduRise features that might help the user
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
            'live_class': 'This is a transcript from an EduRise live class session.',
            'course_module': 'This is content from an EduRise course module.',
            'video': 'This is a transcript from an EduRise video lesson.',
            'text': 'This is educational content from the EduRise platform.'
        }
        
        prompt = f"""
        You are the EduRise AI Assistant. {content_type_instructions.get(content_type, 'This is educational content from the EduRise platform.')}
        
        IMPORTANT: Only summarize content that appears to be legitimate educational material from EduRise courses or classes. 
        If the content seems unrelated to EduRise educational material, respond with an error message.
        
        Please analyze the following EduRise educational content and provide:
        1. A comprehensive summary (2-3 paragraphs) focused on the learning objectives
        2. Key learning points (5-7 bullet points) that students should remember
        
        Content to summarize:
        {content}
        
        Please format your response as JSON:
        {{
            "summary": "Your comprehensive summary of the EduRise educational content...",
            "key_points": [
                "Key learning point 1",
                "Key learning point 2",
                "Key learning point 3",
                "Key learning point 4",
                "Key learning point 5"
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
        You are the EduRise AI Assistant. Create {num_questions} multiple choice questions based on the following EduRise course content.
        
        IMPORTANT: Only generate questions from legitimate EduRise educational content. 
        If the content seems unrelated to educational material, respond with an error message.
        
        Difficulty Level: {difficulty.title()}
        {difficulty_instructions.get(difficulty, '')}
        
        EduRise Course Content:
        {content}
        
        Requirements for each question:
        - Clear, unambiguous question text based on the EduRise content
        - 4 plausible answer options (A, B, C, D)
        - Only one correct answer
        - Brief explanation of why the correct answer is right
        - Questions should test different aspects of the EduRise course material
        - Focus on learning objectives relevant to EduRise students
        
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
    
    def _generate_cache_key(self, operation_type: str, content_hash: str) -> str:
        """Generate cache key for AI operations"""
        import hashlib
        content_hash = hashlib.md5(content_hash.encode()).hexdigest()[:16]
        return f"ai_gemini_{operation_type}_{content_hash}"
    
    def _assess_response_quality(self, response: str, messages: List[Dict]) -> float:
        """Assess the quality of AI chat response"""
        try:
            # Basic quality checks
            if not response or len(response.strip()) < 10:
                return 0.0
            
            # Check for educational content indicators
            educational_indicators = [
                'learn', 'understand', 'concept', 'example', 'explain', 
                'because', 'therefore', 'however', 'consider', 'remember'
            ]
            
            response_lower = response.lower()
            indicator_count = sum(1 for indicator in educational_indicators if indicator in response_lower)
            
            # Base score from indicators
            quality_score = min(indicator_count / 3.0, 1.0)  # Max 1.0 from indicators
            
            # Bonus for appropriate length (not too short, not too long)
            length_score = 1.0
            if len(response) < 50:
                length_score = len(response) / 50.0
            elif len(response) > 1000:
                length_score = max(0.5, 1000.0 / len(response))
            
            # Bonus for question engagement
            if '?' in response:
                quality_score += 0.1
            
            # Penalty for generic responses
            generic_phrases = ['i can help', 'let me know', 'feel free to ask']
            if any(phrase in response_lower for phrase in generic_phrases):
                quality_score -= 0.1
            
            return max(0.0, min(1.0, quality_score * length_score))
            
        except Exception as e:
            logger.warning(f"Error assessing response quality: {str(e)}")
            return 0.5  # Default neutral score
    
    def _assess_summary_quality(self, summary: str, key_points: List[str]) -> float:
        """Assess the quality of AI summary"""
        try:
            if not summary or len(summary.strip()) < 50:
                return 0.0
            
            if not key_points or len(key_points) < 3:
                return 0.3
            
            # Check summary length (should be substantial but not too long)
            length_score = 1.0
            if len(summary) < 100:
                length_score = len(summary) / 100.0
            elif len(summary) > 2000:
                length_score = max(0.5, 2000.0 / len(summary))
            
            # Check key points quality
            points_score = min(len(key_points) / 5.0, 1.0)  # Ideal 5 points
            
            # Check for summary indicators
            summary_indicators = ['summary', 'overview', 'main', 'key', 'important', 'primary']
            indicator_score = min(
                sum(1 for indicator in summary_indicators if indicator in summary.lower()) / 3.0, 
                1.0
            )
            
            return (length_score + points_score + indicator_score) / 3.0
            
        except Exception as e:
            logger.warning(f"Error assessing summary quality: {str(e)}")
            return 0.5
    
    def _assess_quiz_quality(self, questions: List[Dict], expected_count: int) -> float:
        """Assess the quality of AI-generated quiz"""
        try:
            if not questions:
                return 0.0
            
            # Check if we got the expected number of questions
            count_score = min(len(questions) / expected_count, 1.0)
            
            # Check question structure quality
            valid_questions = 0
            for q in questions:
                if self._validate_quiz_question(q):
                    valid_questions += 1
            
            structure_score = valid_questions / len(questions) if questions else 0.0
            
            # Check question content quality
            content_scores = []
            for q in questions:
                question_text = q.get('question', '')
                if len(question_text) > 20 and '?' in question_text:
                    content_scores.append(1.0)
                elif len(question_text) > 10:
                    content_scores.append(0.7)
                else:
                    content_scores.append(0.3)
            
            content_score = sum(content_scores) / len(content_scores) if content_scores else 0.0
            
            return (count_score + structure_score + content_score) / 3.0
            
        except Exception as e:
            logger.warning(f"Error assessing quiz quality: {str(e)}")
            return 0.5
