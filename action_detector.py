"""
Action detection and scheduling module for identifying actionable items in emails.
"""

import re
import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

class ActionDetector:
    """
    Handles detection of actionable items and calendar events in emails.
    """
    
    def __init__(self):
        """
        Initialize the action detector.
        """
        # Common action verbs that indicate a request or task
        self.action_verbs = [
            'please', 'kindly', 'request', 'need', 'should', 'must', 'review',
            'provide', 'send', 'submit', 'complete', 'finish', 'prepare',
            'update', 'check', 'confirm', 'approve', 'verify', 'ensure'
        ]
        
        # Patterns for date detection
        self.date_patterns = [
            # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            # Month DD, YYYY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{2,4}\b',
            # DD Month YYYY
            r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec),?\s+\d{2,4}\b',
            # Next/This Monday, Tuesday, etc.
            r'\b(?:next|this)\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b',
            # Tomorrow, day after tomorrow
            r'\b(?:tomorrow|day after tomorrow)\b',
            # In X days/weeks/months
            r'\bin\s+\d+\s+(?:day|days|week|weeks|month|months)\b'
        ]
        
        # Patterns for time detection
        self.time_patterns = [
            # HH:MM AM/PM
            r'\b(?:0?[1-9]|1[0-2]):[0-5][0-9]\s*(?:am|pm|AM|PM)\b',
            # Military time
            r'\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9]\b',
            # X AM/PM
            r'\b(?:0?[1-9]|1[0-2])\s*(?:am|pm|AM|PM)\b'
        ]
    
    def detect_actions(self, email):
        """
        Detect actionable items in an email.
        
        Args:
            email (dict): Email data
            
        Returns:
            dict: Email with added action data
        """
        # Make a copy of the email to avoid modifying the original
        email_with_actions = email.copy()
        
        # Get email content
        subject = email.get('subject', '')
        body = email.get('body', '')
        
        # If body is not a string, use snippet
        if not isinstance(body, str):
            body = email.get('snippet', '')
        
        # Combine subject and body for analysis
        text = f"{subject}\n{body}"
        
        # Detect action items
        action_items = self._extract_action_items(text)
        email_with_actions['action_items'] = action_items
        
        # Detect calendar events
        calendar_events = self._extract_calendar_events(text)
        email_with_actions['calendar_events'] = calendar_events
        
        # Determine if email requires a response
        requires_response = self._requires_response(text)
        email_with_actions['requires_response'] = requires_response
        
        return email_with_actions
    
    def _extract_action_items(self, text):
        """
        Extract action items from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            list: List of action items
        """
        action_items = []
        
        # Split text into sentences
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            # Check if sentence contains action verbs
            if any(verb in sentence.lower() for verb in self.action_verbs):
                # Check if sentence is imperative or contains a request
                if self._is_actionable_sentence(sentence):
                    action_items.append(sentence.strip())
        
        return action_items
    
    def _is_actionable_sentence(self, sentence):
        """
        Determine if a sentence is actionable.
        
        Args:
            sentence (str): Sentence to analyze
            
        Returns:
            bool: True if sentence is actionable, False otherwise
        """
        # Check for common action indicators
        action_indicators = [
            r'\bplease\b', r'\bkindly\b', r'\bcan you\b', r'\bcould you\b',
            r'\bwould you\b', r'\bneed to\b', r'\bshould\b', r'\bmust\b',
            r'\brequire\b', r'\brequired\b', r'\baction\b', r'\btask\b'
        ]
        
        for indicator in action_indicators:
            if re.search(indicator, sentence.lower()):
                return True
        
        # Check if sentence starts with a verb (imperative)
        words = sentence.strip().split()
        if words and words[0].lower() in [
            'review', 'send', 'check', 'update', 'provide', 'complete',
            'submit', 'prepare', 'ensure', 'confirm', 'verify', 'approve'
        ]:
            return True
        
        return False
    
    def _extract_calendar_events(self, text):
        """
        Extract calendar events from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            list: List of calendar events
        """
        calendar_events = []
        
        # Look for meeting/event indicators
        meeting_indicators = [
            'meeting', 'call', 'conference', 'webinar', 'discussion',
            'appointment', 'session', 'sync', 'catch-up', 'review',
            'interview', 'presentation', 'demo', 'workshop'
        ]
        
        # Split text into sentences
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            # Check if sentence contains meeting indicators
            if any(indicator in sentence.lower() for indicator in meeting_indicators):
                # Extract date and time information
                date_info = self._extract_date_info(sentence)
                time_info = self._extract_time_info(sentence)
                
                if date_info or time_info:
                    # Create calendar event
                    event = {
                        'title': self._generate_event_title(sentence),
                        'description': sentence.strip(),
                        'date': date_info,
                        'time': time_info
                    }
                    calendar_events.append(event)
        
        return calendar_events
    
    def _extract_date_info(self, text):
        """
        Extract date information from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Extracted date information or None
        """
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Try to parse dates using dateutil
        try:
            # Look for common date formats
            for word in text.split():
                try:
                    date = parser.parse(word, fuzzy=True)
                    # Only return if it's a future date
                    if date.date() >= datetime.datetime.now().date():
                        return date.strftime('%Y-%m-%d')
                except:
                    continue
        except:
            pass
        
        return None
    
    def _extract_time_info(self, text):
        """
        Extract time information from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Extracted time information or None
        """
        for pattern in self.time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _generate_event_title(self, text):
        """
        Generate a title for a calendar event based on text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Generated event title
        """
        # Look for meeting type indicators
        meeting_types = [
            'team meeting', 'status update', 'weekly sync', 'daily standup',
            'project review', 'planning session', 'interview', 'presentation',
            'demo', 'workshop', 'conference call', 'webinar', 'discussion'
        ]
        
        for meeting_type in meeting_types:
            if meeting_type in text.lower():
                return meeting_type.title()
        
        # If no specific type found, use generic title
        return "Meeting"
    
    def _requires_response(self, text):
        """
        Determine if an email requires a response.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            bool: True if email requires response, False otherwise
        """
        # Check for question marks
        if '?' in text:
            return True
        
        # Check for response request indicators
        response_indicators = [
            r'\blet me know\b', r'\bplease respond\b', r'\brespond\b',
            r'\breply\b', r'\byour thoughts\b', r'\byour opinion\b',
            r'\bwhat do you think\b', r'\bget back to me\b', r'\bconfirm\b'
        ]
        
        for indicator in response_indicators:
            if re.search(indicator, text.lower()):
                return True
        
        return False
    
    def propose_calendar_event(self, email):
        """
        Propose a calendar event based on email content.
        
        Args:
            email (dict): Email data
            
        Returns:
            dict: Calendar event data or None
        """
        # Check if email has calendar events
        if not email.get('calendar_events'):
            return None
        
        # Get the first calendar event
        event = email['calendar_events'][0]
        
        # Try to parse date
        event_date = None
        if event.get('date'):
            try:
                # Handle relative dates
                if 'tomorrow' in event['date'].lower():
                    event_date = datetime.datetime.now() + datetime.timedelta(days=1)
                elif 'day after tomorrow' in event['date'].lower():
                    event_date = datetime.datetime.now() + datetime.timedelta(days=2)
                elif 'next' in event['date'].lower():
                    # Handle "next Monday", "next Tuesday", etc.
                    day_match = re.search(r'next\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)', 
                                         event['date'], re.IGNORECASE)
                    if day_match:
                        day_name = day_match.group(1)[:3].lower()
                        day_map = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
                        target_day = day_map.get(day_name, 0)
                        
                        # Calculate days until next occurrence of the day
                        current_day = datetime.datetime.now().weekday()
                        days_ahead = target_day - current_day
                        if days_ahead <= 0:  # Target day already happened this week
                            days_ahead += 7
                            
                        event_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
                else:
                    # Try to parse with dateutil
                    event_date = parser.parse(event['date'], fuzzy=True)
            except:
                # If parsing fails, use tomorrow as default
                event_date = datetime.datetime.now() + datetime.timedelta(days=1)
        else:
            # If no date specified, use tomorrow
            event_date = datetime.datetime.now() + datetime.timedelta(days=1)
        
        # Try to parse time
        event_time = None
        if event.get('time'):
            try:
                # Parse time string
                time_str = event['time']
                
                # Handle "X AM/PM" format
                if re.match(r'\b(?:0?[1-9]|1[0-2])\s*(?:am|pm|AM|PM)\b', time_str):
                    time_str = time_str.replace(' ', '')
                    
                # Create a datetime object with the time
                time_obj = parser.parse(time_str)
                
                # Extract hour and minute
                hour = time_obj.hour
                minute = time_obj.minute
                
                # Set the time on the event date
                if event_date:
                    event_date = event_date.replace(hour=hour, minute=minute)
            except:
                # If parsing fails, use default time (10:00 AM)
                if event_date:
                    event_date = event_date.replace(hour=10, minute=0)
        else:
            # If no time specified, use default (10:00 AM)
            if event_date:
                event_date = event_date.replace(hour=10, minute=0)
        
        # Create calendar event proposal
        calendar_proposal = {
            'title': event['title'],
            'description': event['description'],
            'start_time': event_date.strftime('%Y-%m-%d %H:%M') if event_date else None,
            'duration': 60,  # Default duration in minutes
            'attendees': [email.get('sender'), email.get('recipient')],
            'location': 'Virtual Meeting'  # Default location
        }
        
        return calendar_proposal
