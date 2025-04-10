"""
Workload Management System for Email Management AI Agent.
Helps users prioritize tasks and manage their workload effectively.
"""

import re
import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
import heapq
from collections import defaultdict

class WorkloadManager:
    """
    Handles task extraction, prioritization, and workload management.
    """
    
    def __init__(self):
        """
        Initialize the workload manager.
        """
        # Task priority levels
        self.priority_levels = {
            'critical': 5,  # Highest priority
            'high': 4,
            'medium': 3,
            'low': 2,
            'optional': 1   # Lowest priority
        }
        
        # Sender importance levels (to be populated from user data)
        self.sender_importance = {}
        
        # Task extraction patterns
        self.task_patterns = [
            # Direct requests
            r'(?:please|kindly|could you|can you)\s+(.*?)[\.;,]',
            r'(?:need|want|require)\s+you\s+to\s+(.*?)[\.;,]',
            r'(?:would|should)\s+(?:like|appreciate)\s+(?:it\s+)?if\s+you\s+(?:could|would)\s+(.*?)[\.;,]',
            
            # Assignments
            r'(?:assign|assigning|assigned)\s+(?:to\s+)?you\s+(.*?)[\.;,]',
            r'your\s+(?:task|assignment|responsibility)\s+is\s+to\s+(.*?)[\.;,]',
            
            # Action items
            r'action\s+item(?:s)?(?:\s+for\s+you)?:\s+(.*?)[\.;,]',
            r'follow(?:\s+|\-)up(?:\s+item)?(?:s)?:\s+(.*?)[\.;,]',
            
            # Deadlines with tasks
            r'(?:due|complete|finish|submit|deliver)\s+by\s+.*?:\s+(.*?)[\.;,]',
            
            # Implicit tasks
            r'(?:waiting|depend)(?:ing)?\s+on\s+you\s+(?:to|for)\s+(.*?)[\.;,]',
            r'(?:expecting|expect)\s+you\s+to\s+(.*?)[\.;,]'
        ]
        
        # Deadline extraction patterns
        self.deadline_patterns = [
            # Explicit deadlines
            r'(?:due|deadline|complete|finish|submit|deliver)\s+by\s+(.*?)[\.;,]',
            r'(?:due|deadline|completion)\s+date(?:\s+is)?:\s+(.*?)[\.;,]',
            r'(?:needed|required)\s+by\s+(.*?)[\.;,]',
            
            # Timeframe deadlines
            r'within\s+(\d+)\s+(?:day|days|week|weeks|month|months)',
            r'in\s+the\s+next\s+(\d+)\s+(?:day|days|week|weeks|month|months)',
            r'by\s+(?:the\s+)?end\s+of\s+(today|tomorrow|this\s+week|next\s+week|this\s+month)',
            
            # Specific dates
            r'by\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?',
            r'by\s+(\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)(?:,?\s+\d{4})?)',
            
            # Relative dates
            r'by\s+(tomorrow|next\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday))',
            r'by\s+(this|next)\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)'
        ]
        
        # Urgency indicators
        self.urgency_indicators = {
            'critical': [
                'urgent', 'critical', 'emergency', 'asap', 'immediately', 'right away',
                'highest priority', 'top priority', 'crisis', 'crucial', 'vital'
            ],
            'high': [
                'important', 'priority', 'as soon as possible', 'timely', 'pressing',
                'significant', 'key', 'major', 'essential', 'necessary'
            ],
            'medium': [
                'needed', 'required', 'should', 'would be good', 'appreciate',
                'helpful', 'beneficial', 'valuable', 'useful'
            ],
            'low': [
                'when you can', 'at your convenience', 'if you have time', 'optional',
                'nice to have', 'would be nice', 'not urgent', 'low priority'
            ]
        }
        
        # Project keywords (to be populated from user data)
        self.project_keywords = {}
        
        # Task status tracking
        self.tasks = {}
        
        # Workload metrics
        self.daily_capacity = 8  # Default: 8 hours per day
        self.task_time_estimates = {
            'critical': 2.0,  # Default: 2 hours for critical tasks
            'high': 1.5,      # Default: 1.5 hours for high priority tasks
            'medium': 1.0,    # Default: 1 hour for medium priority tasks
            'low': 0.5,       # Default: 30 minutes for low priority tasks
            'optional': 0.25  # Default: 15 minutes for optional tasks
        }
    
    def extract_tasks_from_email(self, email):
        """
        Extract tasks from an email.
        
        Args:
            email (dict): Email data
            
        Returns:
            list: List of extracted tasks
        """
        # Get email content
        subject = email.get('subject', '')
        body = email.get('body', '')
        sender = email.get('sender', '')
        date = email.get('date', '')
        email_id = email.get('id', '')
        
        # Combine subject and body for analysis
        text = f"{subject}\n{body}"
        
        # Extract tasks
        tasks = []
        for pattern in self.task_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                task_description = match.group(1).strip()
                if task_description:
                    # Extract deadline for this specific task
                    deadline = self._extract_deadline_for_task(text, task_description)
                    
                    # Determine priority
                    priority = self._determine_task_priority(text, task_description, sender)
                    
                    # Create task object
                    task = {
                        'id': f"task_{email_id}_{len(tasks)}",
                        'description': task_description,
                        'source_email_id': email_id,
                        'sender': sender,
                        'date_received': date,
                        'deadline': deadline,
                        'priority': priority,
                        'status': 'pending',
                        'estimated_time': self.task_time_estimates.get(priority, 1.0),
                        'project': self._determine_project(text, task_description),
                        'dependencies': self._extract_dependencies(text, task_description)
                    }
                    
                    tasks.append(task)
        
        # If no tasks found but email seems to contain a request, extract a generic task
        if not tasks and self._contains_request(text):
            # Create a generic task based on the email subject
            task = {
                'id': f"task_{email_id}_0",
                'description': f"Review and respond to email: {subject}",
                'source_email_id': email_id,
                'sender': sender,
                'date_received': date,
                'deadline': self._extract_deadline(text),
                'priority': self._determine_task_priority(text, subject, sender),
                'status': 'pending',
                'estimated_time': 0.5,  # Default: 30 minutes for email review
                'project': self._determine_project(text, subject),
                'dependencies': []
            }
            
            tasks.append(task)
        
        return tasks
    
    def _extract_deadline_for_task(self, text, task_description):
        """
        Extract deadline specifically for a task.
        
        Args:
            text (str): Email text
            task_description (str): Task description
            
        Returns:
            dict: Deadline information
        """
        # First, look for deadlines in the vicinity of the task description
        task_context = self._get_context_around_text(text, task_description, 200)
        deadline_text = self._extract_deadline(task_context)
        
        # If no deadline found in context, check the entire text
        if not deadline_text:
            deadline_text = self._extract_deadline(text)
        
        # If still no deadline, return None
        if not deadline_text:
            return None
        
        # Parse the deadline text into a structured format
        return self._parse_deadline(deadline_text)
    
    def _get_context_around_text(self, text, target, context_size=200):
        """
        Get text context around a target string.
        
        Args:
            text (str): Full text
            target (str): Target string to find
            context_size (int): Number of characters to include before and after
            
        Returns:
            str: Context text
        """
        index = text.lower().find(target.lower())
        if index == -1:
            return ""
        
        start = max(0, index - context_size)
        end = min(len(text), index + len(target) + context_size)
        
        return text[start:end]
    
    def _extract_deadline(self, text):
        """
        Extract deadline information from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Extracted deadline text or None
        """
        for pattern in self.deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _parse_deadline(self, deadline_text):
        """
        Parse deadline text into structured format.
        
        Args:
            deadline_text (str): Deadline text
            
        Returns:
            dict: Structured deadline information
        """
        try:
            # Handle relative terms
            now = datetime.datetime.now()
            
            if re.search(r'\b(today)\b', deadline_text, re.IGNORECASE):
                deadline_date = now.date()
                deadline_time = datetime.time(17, 0)  # Default: 5:00 PM
                
            elif re.search(r'\b(tomorrow)\b', deadline_text, re.IGNORECASE):
                tomorrow = now + datetime.timedelta(days=1)
                deadline_date = tomorrow.date()
                deadline_time = datetime.time(17, 0)  # Default: 5:00 PM
                
            elif re.search(r'\b(this\s+week)\b', deadline_text, re.IGNORECASE):
                # End of this week (Friday)
                days_until_friday = (4 - now.weekday()) % 7
                if days_until_friday == 0:
                    days_until_friday = 7
                friday = now + datetime.timedelta(days=days_until_friday)
                deadline_date = friday.date()
                deadline_time = datetime.time(17, 0)  # Default: 5:00 PM
                
            elif re.search(r'\b(next\s+week)\b', deadline_text, re.IGNORECASE):
                # Middle of next week (Wednesday)
                days_until_next_wednesday = (9 - now.weekday()) % 7
                next_wednesday = now + datetime.timedelta(days=days_until_next_wednesday)
                deadline_date = next_wednesday.date()
                deadline_time = datetime.time(17, 0)  # Default: 5:00 PM
                
            elif re.search(r'\b(this\s+month)\b', deadline_text, re.IGNORECASE):
                # End of this month
                if now.month == 12:
                    deadline_date = datetime.date(now.year, 12, 31)
                else:
                    deadline_date = datetime.date(now.year, now.month + 1, 1) - datetime.timedelta(days=1)
                deadline_time = datetime.time(17, 0)  # Default: 5:00 PM
                
            elif re.search(r'\bwithin\s+(\d+)\s+(day|days|week|weeks|month|months)\b', deadline_text, re.IGNORECASE):
                # Within X days/weeks/months
                match = re.search(r'\bwithin\s+(\d+)\s+(day|days|week|weeks|month|months)\b', deadline_text, re.IGNORECASE)
                amount = int(match.group(1))
                unit = match.group(2).lower()
                
                if unit in ['day', 'days']:
                    deadline_date = (now + datetime.timedelta(days=amount)).date()
                elif unit in ['week', 'weeks']:
                    deadline_date = (now + datetime.timedelta(days=amount * 7)).date()
                elif unit in ['month', 'months']:
                    deadline_date = (now + relativedelta(months=amount)).date()
                
                deadline_time = datetime.time(17, 0)  # Default: 5:00 PM
                
            elif re.search(r'\bnext\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', deadline_text, re.IGNORECASE):
                # Next specific day of week
                match = re.search(r'\bnext\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', deadline_text, re.IGNORECASE)
                day_name = match.group(1).lower()
                day_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
                target_day = day_map.get(day_name, 0)
                
                days_until_day = (target_day - now.weekday()) % 7
                if days_until_day == 0:
                    days_until_day = 7
                
                next_day = now + datetime.timedelta(days=days_until_day)
                deadline_date = next_day.date()
                deadline_time = datetime.time(17, 0)  # Default: 5:00 PM
                
            else:
                # Try to parse as a date
                try:
                    parsed_date = parser.parse(deadline_text, fuzzy=True)
                    deadline_date = parsed_date.date()
                    deadline_time = parsed_date.time() if parsed_date.time() != datetime.time(0, 0) else datetime.time(17, 0)
                except:
                    # If parsing fails, default to one week from now
                    next_week = now + datetime.timedelta(days=7)
                    deadline_date = next_week.date()
                    deadline_time = datetime.time(17, 0)  # Default: 5:00 PM
            
            # Create deadline object
            deadline = {
                'date': deadline_date.strftime('%Y-%m-%d'),
                'time': deadline_time.strftime('%H:%M'),
                'datetime': datetime.datetime.combine(deadline_date, deadline_time),
                'original_text': deadline_text
            }
            
            return deadline
            
        except Exception as e:
            # If any error occurs, return a default deadline (one week from now)
            next_week = datetime.datetime.now() + datetime.timedelta(days=7)
            return {
                'date': next_week.date().strftime('%Y-%m-%d'),
                'time': '17:00',
                'datetime': datetime.datetime.combine(next_week.date(), datetime.time(17, 0)),
                'original_text': deadline_text
            }
    
    def _determine_task_priority(self, text, task_description, sender):
        """
        Determine priority of a task.
        
        Args:
            text (str): Email text
            task_description (str): Task description
            sender (str): Email sender
            
        Returns:
            str: Priority level
        """
        # Get context around the task description
        task_context = self._get_context_around_text(text, task_description, 200)
        
        # Check for urgency indicators
        for priority, indicators in self.urgency_indicators.items():
            for indicator in indicators:
                if re.search(r'\b' + re.escape(indicator) + r'\b', task_context, re.IGNORECASE):
                    return priority
        
        # Consider sender importance
        sender_priority = self.sender_importance.get(sender, 'm
(Content truncated due to size limit. Use line ranges to read in chunks)