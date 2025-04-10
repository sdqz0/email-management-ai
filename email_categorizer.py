"""
Email categorization module for analyzing and prioritizing emails.
"""

import re
from config import PRIORITY_LEVELS, PRIORITY_KEYWORDS

class EmailCategorizer:
    """
    Handles categorization and prioritization of emails.
    """
    
    def __init__(self):
        """
        Initialize the email categorizer with configuration settings.
        """
        self.priority_levels = PRIORITY_LEVELS
        self.priority_keywords = PRIORITY_KEYWORDS
    
    def categorize_email(self, email):
        """
        Analyze and categorize an email based on content, sender, and other factors.
        
        Args:
            email (dict): Email data to categorize
            
        Returns:
            dict: Email with added categorization data
        """
        # Make a copy of the email to avoid modifying the original
        categorized_email = email.copy()
        
        # Determine priority
        priority = self._determine_priority(email)
        categorized_email['priority'] = priority
        
        # Determine category
        category = self._determine_category(email)
        categorized_email['category'] = category
        
        # Check for calendar events or appointments
        has_calendar_event = self._detect_calendar_event(email)
        categorized_email['has_calendar_event'] = has_calendar_event
        
        # Check for deadlines
        deadline = self._detect_deadline(email)
        categorized_email['deadline'] = deadline
        
        return categorized_email
    
    def _determine_priority(self, email):
        """
        Determine the priority level of an email.
        
        Args:
            email (dict): Email data
            
        Returns:
            str: Priority level ('high', 'medium', or 'low')
        """
        # Check if email is from an important sender
        if self._is_important_sender(email['sender']):
            return 'high'
        
        # Check for priority keywords in subject and body
        subject = email['subject'].lower()
        body = email['body'].lower() if isinstance(email['body'], str) else ''
        snippet = email['snippet'].lower()
        
        # Combine text for keyword search
        text = f"{subject} {snippet} {body[:1000]}"  # Limit body to first 1000 chars for efficiency
        
        # Check for high priority keywords
        for keyword in self.priority_keywords['high']:
            if keyword.lower() in text:
                return 'high'
        
        # Check for medium priority keywords
        for keyword in self.priority_keywords['medium']:
            if keyword.lower() in text:
                return 'medium'
        
        # Check for low priority keywords
        for keyword in self.priority_keywords['low']:
            if keyword.lower() in text:
                return 'low'
        
        # Default priority is medium
        return 'medium'
    
    def _determine_category(self, email):
        """
        Determine the category of an email.
        
        Args:
            email (dict): Email data
            
        Returns:
            str: Category name
        """
        # Check Gmail labels first
        labels = email.get('labels', [])
        
        if 'CATEGORY_PERSONAL' in labels:
            return 'personal'
        elif 'CATEGORY_SOCIAL' in labels:
            return 'social'
        elif 'CATEGORY_PROMOTIONS' in labels:
            return 'promotions'
        elif 'CATEGORY_UPDATES' in labels:
            return 'updates'
        elif 'CATEGORY_FORUMS' in labels:
            return 'forums'
        
        # If no Gmail category, try to determine from content
        subject = email['subject'].lower()
        sender = email['sender'].lower()
        
        # Check for newsletter or promotional content
        if any(term in subject for term in ['newsletter', 'weekly update', 'digest', 'subscription']):
            return 'newsletter'
        
        # Check for automated notifications
        if any(term in sender for term in ['noreply', 'no-reply', 'donotreply', 'notification']):
            return 'notification'
        
        # Default category
        return 'primary'
    
    def _is_important_sender(self, sender):
        """
        Check if the sender is considered important.
        This would typically be customized based on user preferences.
        
        Args:
            sender (str): Email sender
            
        Returns:
            bool: True if sender is important, False otherwise
        """
        # This is a placeholder for a more sophisticated implementation
        # In a real application, this would check against a user-defined list
        important_domains = ['boss.com', 'ceo.com', 'important.com']
        
        for domain in important_domains:
            if domain in sender.lower():
                return True
        
        return False
    
    def _detect_calendar_event(self, email):
        """
        Detect if an email contains calendar event information.
        
        Args:
            email (dict): Email data
            
        Returns:
            bool: True if calendar event detected, False otherwise
        """
        # Check for calendar-related keywords in subject and body
        subject = email['subject'].lower()
        body = email['body'].lower() if isinstance(email['body'], str) else ''
        
        calendar_keywords = [
            'meeting', 'appointment', 'schedule', 'calendar', 'invite',
            'join me', 'conference', 'call', 'webinar', 'event'
        ]
        
        # Check subject for calendar keywords
        if any(keyword in subject for keyword in calendar_keywords):
            return True
        
        # Check body for calendar keywords and time patterns
        if any(keyword in body for keyword in calendar_keywords):
            # Look for time patterns (e.g., 3:00 PM, 15:00)
            time_pattern = r'\b([0-1]?[0-9]|2[0-3]):[0-5][0-9]\s*(am|pm|AM|PM)?\b'
            if re.search(time_pattern, body):
                return True
            
            # Look for date patterns (e.g., Monday, Jan 15, 2023-04-07)
            date_pattern = r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}'
            if re.search(date_pattern, body, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_deadline(self, email):
        """
        Detect if an email contains deadline information.
        
        Args:
            email (dict): Email data
            
        Returns:
            str: Deadline text if detected, None otherwise
        """
        # Check for deadline-related keywords in subject and body
        subject = email['subject'].lower()
        body = email['body'].lower() if isinstance(email['body'], str) else ''
        
        deadline_keywords = [
            'deadline', 'due date', 'due by', 'submit by', 'complete by',
            'no later than', 'by the end of', 'eod', 'cob'
        ]
        
        # Combine text for search
        text = f"{subject} {body}"
        
        # Search for deadline keywords
        for keyword in deadline_keywords:
            if keyword in text:
                # Find the sentence containing the keyword
                sentences = re.split(r'[.!?]', text)
                for sentence in sentences:
                    if keyword in sentence:
                        # Extract a window around the keyword for context
                        start = max(0, text.find(sentence) - 50)
                        end = min(len(text), text.find(sentence) + len(sentence) + 50)
                        context = text[start:end].strip()
                        return context
        
        return None
