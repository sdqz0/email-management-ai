"""
Smart Response Generation module for Email Management AI Agent.
Provides AI-generated response suggestions for emails.
"""

import re
import random
from datetime import datetime
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class SmartResponseGenerator:
    """
    Handles generation of AI-powered email response suggestions.
    """
    
    def __init__(self):
        """
        Initialize the smart response generator.
        """
        # Initialize NLP components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Response templates by category
        self.templates = {
            'meeting_request': [
                "I'm available for the meeting on {date} at {time}. Looking forward to discussing {topic}.",
                "Thank you for the invitation. I can attend the meeting on {date} at {time}.",
                "I'll be happy to join the discussion about {topic} on {date} at {time}.",
                "I've added the meeting to my calendar for {date} at {time}. Looking forward to it."
            ],
            'task_assignment': [
                "I'll take care of {task} by {deadline}. I'll update you on the progress.",
                "Thank you for assigning {task} to me. I'll complete it by {deadline}.",
                "I'll start working on {task} right away and will have it done by {deadline}.",
                "I've noted the {task} assignment and will ensure it's completed by {deadline}."
            ],
            'information_request': [
                "Here's the information you requested about {topic}: {info}",
                "Regarding your question about {topic}, {info}",
                "I've gathered the details you asked for about {topic}: {info}",
                "In response to your inquiry about {topic}: {info}"
            ],
            'follow_up': [
                "I wanted to follow up on {topic}. Have you had a chance to review it?",
                "Just checking in on {topic}. Let me know if you need anything else from me.",
                "Following up on our discussion about {topic}. Any updates on your end?",
                "Touching base regarding {topic}. How would you like to proceed?"
            ],
            'thank_you': [
                "Thank you for {action}. I really appreciate it.",
                "I wanted to express my thanks for {action}.",
                "Thank you so much for {action}. It's greatly appreciated.",
                "I appreciate your help with {action}. Thank you."
            ],
            'apology': [
                "I apologize for {issue}. I'll make sure it doesn't happen again.",
                "I'm sorry about {issue}. Let me know how I can make it right.",
                "Please accept my apology for {issue}. I understand the inconvenience this caused.",
                "I sincerely apologize for {issue} and will take steps to address it immediately."
            ],
            'acknowledgment': [
                "I've received your email about {topic} and will review it shortly.",
                "Thank you for sending the information about {topic}. I'll take a look at it.",
                "I acknowledge receipt of your message regarding {topic}.",
                "Got your email about {topic}. I'll get back to you soon with my thoughts."
            ],
            'general': [
                "Thank you for your email. I'll respond in detail soon.",
                "I've received your message and will get back to you shortly.",
                "Thanks for reaching out. I'll review this and respond as soon as possible.",
                "I appreciate your email. I'll prepare a thorough response soon."
            ]
        }
        
        # Quick replies for common situations
        self.quick_replies = {
            'confirmation': [
                "Confirmed, thank you.",
                "Yes, that works for me.",
                "Sounds good, I confirm.",
                "I confirm receipt, thanks."
            ],
            'acknowledgment': [
                "Got it, thanks.",
                "Received, thank you.",
                "Thanks for letting me know.",
                "Noted, appreciate the update."
            ],
            'agreement': [
                "I agree with your suggestion.",
                "That sounds like a good plan.",
                "I'm on board with this approach.",
                "I support this decision."
            ],
            'clarification': [
                "Could you please provide more details about this?",
                "I need some clarification on this point.",
                "Could you elaborate on what you mean by this?",
                "I'm not sure I understand - could you explain further?"
            ],
            'scheduling': [
                "How about meeting next Tuesday at 2 PM?",
                "Would Wednesday afternoon work for a quick call?",
                "I'm available this Thursday between 10 AM and 2 PM.",
                "Let's schedule a 30-minute discussion tomorrow."
            ]
        }
        
        # Email type detection patterns
        self.email_type_patterns = {
            'meeting_request': [
                r'meet', r'meeting', r'discuss', r'discussion', r'call',
                r'schedule', r'calendar', r'availability', r'available',
                r'zoom', r'teams', r'conference', r'invite'
            ],
            'task_assignment': [
                r'task', r'assignment', r'project', r'deadline', r'complete',
                r'finish', r'deliver', r'responsibility', r'assigned',
                r'due date', r'due by', r'action item'
            ],
            'information_request': [
                r'information', r'details', r'data', r'report', r'update',
                r'status', r'question', r'inquiry', r'clarification',
                r'explain', r'elaborate', r'provide'
            ],
            'follow_up': [
                r'follow up', r'following up', r'checking in', r'touch base',
                r'status update', r'progress', r'any updates', r'reminder'
            ],
            'thank_you': [
                r'thank you', r'thanks', r'appreciate', r'grateful',
                r'recognition', r'acknowledgment'
            ],
            'apology': [
                r'sorry', r'apology', r'apologize', r'regret', r'mistake',
                r'error', r'inconvenience', r'issue'
            ]
        }
    
    def generate_response(self, email, user_data=None):
        """
        Generate response suggestions for an email.
        
        Args:
            email (dict): Email data
            user_data (dict, optional): User preferences and history data
            
        Returns:
            dict: Response suggestions including templates and quick replies
        """
        # Extract email content
        subject = email.get('subject', '')
        body = email.get('body', '')
        sender = email.get('sender', '')
        
        # Determine email type
        email_type = self._determine_email_type(subject, body)
        
        # Extract key information
        key_info = self._extract_key_info(subject, body, email_type)
        
        # Generate template-based responses
        template_responses = self._generate_template_responses(email_type, key_info, user_data)
        
        # Generate quick replies if appropriate
        quick_reply_suggestions = self._generate_quick_replies(email_type, key_info)
        
        # Personalize responses based on user data if available
        if user_data:
            template_responses = self._personalize_responses(template_responses, user_data, sender)
        
        return {
            'email_type': email_type,
            'template_responses': template_responses,
            'quick_replies': quick_reply_suggestions,
            'key_info': key_info
        }
    
    def _determine_email_type(self, subject, body):
        """
        Determine the type of email based on content analysis.
        
        Args:
            subject (str): Email subject
            body (str): Email body
            
        Returns:
            str: Email type
        """
        # Combine subject and body for analysis
        text = f"{subject} {body}".lower()
        
        # Check for each email type pattern
        type_scores = {}
        for email_type, patterns in self.email_type_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(r'\b' + pattern + r'\b', text)
                score += len(matches)
            type_scores[email_type] = score
        
        # Get the email type with the highest score
        if max(type_scores.values()) > 0:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        
        # Default to general if no specific type is detected
        return 'general'
    
    def _extract_key_info(self, subject, body, email_type):
        """
        Extract key information from the email based on its type.
        
        Args:
            subject (str): Email subject
            body (str): Email body
            email_type (str): Type of email
            
        Returns:
            dict: Extracted key information
        """
        # Combine subject and body for analysis
        text = f"{subject}\n{body}"
        
        # Initialize key info dictionary
        key_info = {
            'topic': self._extract_topic(subject, body),
            'date': self._extract_date(text),
            'time': self._extract_time(text),
            'deadline': self._extract_deadline(text),
            'task': self._extract_task(text) if email_type == 'task_assignment' else '',
            'action': self._extract_action(text) if email_type == 'thank_you' else '',
            'issue': self._extract_issue(text) if email_type == 'apology' else '',
            'info': ''  # Placeholder for information requests
        }
        
        return key_info
    
    def _extract_topic(self, subject, body):
        """
        Extract the main topic from the email.
        
        Args:
            subject (str): Email subject
            body (str): Email body
            
        Returns:
            str: Main topic
        """
        # Use subject as the primary source for topic
        if subject:
            # Remove common prefixes like "Re:", "Fwd:", etc.
            clean_subject = re.sub(r'^(Re|Fwd|FW|RE|FWD):\s*', '', subject)
            return clean_subject
        
        # If subject is empty, try to extract from the first sentence of the body
        if body:
            sentences = sent_tokenize(body)
            if sentences:
                return sentences[0][:50] + ('...' if len(sentences[0]) > 50 else '')
        
        return "this matter"  # Default fallback
    
    def _extract_date(self, text):
        """
        Extract date information from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Extracted date or placeholder
        """
        # Common date patterns
        date_patterns = [
            # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            # Month DD, YYYY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{2,4}\b',
            # DD Month YYYY
            r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec),?\s+\d{2,4}\b',
            # Next/This Monday, Tuesday, etc.
            r'\b(?:next|this)\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b',
            # Tomorrow, day after tomorrow
            r'\b(?:tomorrow|day after tomorrow)\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Default to tomorrow if no date found
        tomorrow = (datetime.now().date() + timedelta(days=1)).strftime("%A, %B %d")
        return tomorrow
    
    def _extract_time(self, text):
        """
        Extract time information from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Extracted time or placeholder
        """
        # Common time patterns
        time_patterns = [
            # HH:MM AM/PM
            r'\b(?:0?[1-9]|1[0-2]):[0-5][0-9]\s*(?:am|pm|AM|PM)\b',
            # Military time
            r'\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9]\b',
            # X AM/PM
            r'\b(?:0?[1-9]|1[0-2])\s*(?:am|pm|AM|PM)\b'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Default to a business hour if no time found
        return "10:00 AM"
    
    def _extract_deadline(self, text):
        """
        Extract deadline information from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Extracted deadline or placeholder
        """
        # Look for deadline indicators
        deadline_indicators = [
            r'due\s+by\s+(.*?)[\.;,]',
            r'deadline\s+(?:is|of)\s+(.*?)[\.;,]',
            r'complete\s+by\s+(.*?)[\.;,]',
            r'finish\s+by\s+(.*?)[\.;,]',
            r'submit\s+by\s+(.*?)[\.;,]'
        ]
        
        for pattern in deadline_indicators:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no specific deadline found, extract any date as potential deadline
        date = self._extract_date(text)
        if date:
            return date
        
        # Default to end of week if no deadline found
        return "the end of this week"
    
    def _extract_task(self, text):
        """
        Extract task information from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Extracted task or placeholder
        """
        # Look for task assignment patterns
        task_patterns = [
            r'(?:please|kindly|could you|can you)\s+(.*?)[\.;,]',
            r'(?:assigned|assigning|assign)\s+(?:you|to you)\s+(.*?)[\.;,]',
            r'(?:task|responsibility)\s+(?:is|of)\s+(.*?)[\.;,]',
            r'need\s+you\s+to\s+(.*?)[\.;,]',
            r'would\s+like\s+you\s+to\s+(.*?)[\.;,]'
        ]
        
        for pattern in task_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no specific task found, use topic as fallback
        return "the requested task"
    
    def _extract_action(self, text):
        """
        Extract action information for thank you emails.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Extracted action or placeholder
        """
        # Look for thank you context
        thank_patterns = [
            r'thank\s+(?:you|you\s+for|for)\s+(.*?)[\.;,]',
            r'thanks\s+for\s+(.*?)[\.;,]',
            r'appreciate\s+(?:your|the)\s
(Content truncated due to size limit. Use line ranges to read in chunks)