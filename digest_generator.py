"""
Inbox digest report generator for creating email summaries and reports.
"""

import datetime
from jinja2 import Template

class DigestGenerator:
    """
    Handles generation of email digest reports.
    """
    
    def __init__(self):
        """
        Initialize the digest generator.
        """
        # HTML template for digest report
        self.html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Digest</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .section {
                    margin-bottom: 30px;
                }
                .section-title {
                    font-size: 18px;
                    font-weight: bold;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                    margin-bottom: 15px;
                }
                .email-item {
                    background-color: #fff;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 15px;
                }
                .email-header {
                    margin-bottom: 10px;
                }
                .email-subject {
                    font-weight: bold;
                    font-size: 16px;
                }
                .email-sender {
                    color: #666;
                }
                .email-summary {
                    margin-bottom: 10px;
                }
                .email-actions {
                    margin-top: 10px;
                    font-size: 14px;
                }
                .priority-high {
                    border-left: 5px solid #ff4d4d;
                }
                .priority-medium {
                    border-left: 5px solid #ffcc00;
                }
                .priority-low {
                    border-left: 5px solid #66cc66;
                }
                .calendar-item {
                    background-color: #e6f7ff;
                    border: 1px solid #b3e0ff;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 15px;
                }
                .calendar-title {
                    font-weight: bold;
                }
                .calendar-time {
                    color: #666;
                }
                .calendar-description {
                    margin-top: 5px;
                }
                .footer {
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 30px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Email Digest</h1>
                <p>{{ date_time }}</p>
                <p>Total unread emails: {{ unread_count }}</p>
            </div>
            
            {% if important_emails %}
            <div class="section">
                <h2 class="section-title">Important Emails</h2>
                {% for email in important_emails %}
                <div class="email-item priority-{{ email.priority }}">
                    <div class="email-header">
                        <div class="email-subject">{{ email.subject }}</div>
                        <div class="email-sender">From: {{ email.sender }}</div>
                        <div class="email-sender">{{ email.date }}</div>
                    </div>
                    <div class="email-summary">
                        {{ email.summary }}
                    </div>
                    {% if email.action_items %}
                    <div class="email-actions">
                        <strong>Action Items:</strong>
                        <ul>
                            {% for action in email.action_items %}
                            <li>{{ action }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if calendar_events %}
            <div class="section">
                <h2 class="section-title">Proposed Calendar Events</h2>
                {% for event in calendar_events %}
                <div class="calendar-item">
                    <div class="calendar-title">{{ event.title }}</div>
                    <div class="calendar-time">{{ event.start_time }}</div>
                    <div class="calendar-description">{{ event.description }}</div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if unread_emails %}
            <div class="section">
                <h2 class="section-title">Other Unread Emails</h2>
                {% for email in unread_emails %}
                <div class="email-item priority-{{ email.priority }}">
                    <div class="email-header">
                        <div class="email-subject">{{ email.subject }}</div>
                        <div class="email-sender">From: {{ email.sender }}</div>
                        <div class="email-sender">{{ email.date }}</div>
                    </div>
                    <div class="email-summary">
                        {{ email.summary }}
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <div class="footer">
                <p>Generated by Email Management AI Agent</p>
            </div>
        </body>
        </html>
        """
    
    def generate_digest(self, emails, frequency='daily'):
        """
        Generate a digest report from a list of emails.
        
        Args:
            emails (list): List of processed email objects
            frequency (str): Frequency of the digest ('daily' or 'hourly')
            
        Returns:
            str: HTML digest report
        """
        # Get current date and time
        now = datetime.datetime.now()
        date_time = now.strftime('%A, %B %d, %Y at %I:%M %p')
        
        # Count unread emails
        unread_count = sum(1 for email in emails if email.get('is_unread', False))
        
        # Get important emails (high and medium priority)
        important_emails = [
            email for email in emails 
            if email.get('priority') == 'high' or 
               (email.get('priority') == 'medium' and email.get('is_unread', False))
        ]
        
        # Limit to top 5 important emails
        important_emails = sorted(
            important_emails, 
            key=lambda x: self._get_priority_value(x.get('priority', 'low')), 
            reverse=True
        )[:5]
        
        # Get proposed calendar events
        calendar_events = []
        for email in emails:
            if email.get('calendar_events'):
                for event in email.get('calendar_events', []):
                    calendar_proposal = {
                        'title': event.get('title', 'Meeting'),
                        'start_time': event.get('date', '') + ' ' + event.get('time', '') if event.get('date') else 'Date not specified',
                        'description': event.get('description', '')
                    }
                    calendar_events.append(calendar_proposal)
        
        # Get other unread emails (not in important emails)
        important_ids = [email.get('id') for email in important_emails]
        unread_emails = [
            email for email in emails 
            if email.get('is_unread', False) and email.get('id') not in important_ids
        ]
        
        # Render the template
        template = Template(self.html_template)
        html_digest = template.render(
            date_time=date_time,
            unread_count=unread_count,
            important_emails=important_emails,
            calendar_events=calendar_events,
            unread_emails=unread_emails
        )
        
        return html_digest
    
    def _get_priority_value(self, priority):
        """
        Convert priority string to numeric value for sorting.
        
        Args:
            priority (str): Priority level ('high', 'medium', or 'low')
            
        Returns:
            int: Priority value
        """
        priority_map = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_map.get(priority, 0)
    
    def generate_text_digest(self, emails, frequency='daily'):
        """
        Generate a plain text digest report from a list of emails.
        
        Args:
            emails (list): List of processed email objects
            frequency (str): Frequency of the digest ('daily' or 'hourly')
            
        Returns:
            str: Plain text digest report
        """
        # Get current date and time
        now = datetime.datetime.now()
        date_time = now.strftime('%A, %B %d, %Y at %I:%M %p')
        
        # Count unread emails
        unread_count = sum(1 for email in emails if email.get('is_unread', False))
        
        # Get important emails (high and medium priority)
        important_emails = [
            email for email in emails 
            if email.get('priority') == 'high' or 
               (email.get('priority') == 'medium' and email.get('is_unread', False))
        ]
        
        # Limit to top 5 important emails
        important_emails = sorted(
            important_emails, 
            key=lambda x: self._get_priority_value(x.get('priority', 'low')), 
            reverse=True
        )[:5]
        
        # Get proposed calendar events
        calendar_events = []
        for email in emails:
            if email.get('calendar_events'):
                for event in email.get('calendar_events', []):
                    calendar_proposal = {
                        'title': event.get('title', 'Meeting'),
                        'start_time': event.get('date', '') + ' ' + event.get('time', '') if event.get('date') else 'Date not specified',
                        'description': event.get('description', '')
                    }
                    calendar_events.append(calendar_proposal)
        
        # Get other unread emails (not in important emails)
        important_ids = [email.get('id') for email in important_emails]
        unread_emails = [
            email for email in emails 
            if email.get('is_unread', False) and email.get('id') not in important_ids
        ]
        
        # Build text digest
        text_digest = f"EMAIL DIGEST\n{date_time}\n"
        text_digest += f"Total unread emails: {unread_count}\n\n"
        
        if important_emails:
            text_digest += "IMPORTANT EMAILS\n"
            text_digest += "================\n\n"
            
            for email in important_emails:
                text_digest += f"Subject: {email.get('subject', 'No Subject')}\n"
                text_digest += f"From: {email.get('sender', 'Unknown')}\n"
                text_digest += f"Date: {email.get('date', '')}\n"
                text_digest += f"Priority: {email.get('priority', 'medium')}\n"
                text_digest += f"Summary: {email.get('summary', 'No summary available')}\n"
                
                if email.get('action_items'):
                    text_digest += "Action Items:\n"
                    for action in email.get('action_items', []):
                        text_digest += f"- {action}\n"
                
                text_digest += "\n"
        
        if calendar_events:
            text_digest += "PROPOSED CALENDAR EVENTS\n"
            text_digest += "========================\n\n"
            
            for event in calendar_events:
                text_digest += f"Title: {event.get('title', 'Meeting')}\n"
                text_digest += f"Time: {event.get('start_time', 'Time not specified')}\n"
                text_digest += f"Description: {event.get('description', '')}\n\n"
        
        if unread_emails:
            text_digest += "OTHER UNREAD EMAILS\n"
            text_digest += "===================\n\n"
            
            for email in unread_emails:
                text_digest += f"Subject: {email.get('subject', 'No Subject')}\n"
                text_digest += f"From: {email.get('sender', 'Unknown')}\n"
                text_digest += f"Date: {email.get('date', '')}\n"
                text_digest += f"Summary: {email.get('summary', 'No summary available')}\n\n"
        
        text_digest += "Generated by Email Management AI Agent"
        
        return text_digest
