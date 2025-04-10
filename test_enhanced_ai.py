"""
Test script for enhanced AI features of the Email Management AI Agent.
"""

import os
import sys
import json
import unittest
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from src.smart_response import SmartResponseGenerator
from src.workload_manager import WorkloadManager
from src.sentiment_analyzer import SentimentAnalyzer
from src.contextual_learning import ContextualLearningSystem
from src.advanced_nlp import AdvancedNLPUnderstanding
from src.proactive_notifications import ProactiveNotificationSystem

class TestEnhancedAIFeatures(unittest.TestCase):
    """Test case for enhanced AI features."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test data directory
        os.makedirs('/home/ubuntu/email_agent/data/test', exist_ok=True)
        
        # Initialize test user ID
        self.user_id = 'test_user'
        
        # Initialize test data
        self.test_emails = self._create_test_emails()
        
        # Initialize components
        self.smart_response = SmartResponseGenerator()
        self.workload_manager = WorkloadManager()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.contextual_learning = ContextualLearningSystem(
            user_id=self.user_id,
            data_dir='/home/ubuntu/email_agent/data/test'
        )
        self.advanced_nlp = AdvancedNLPUnderstanding()
        self.proactive_notifications = ProactiveNotificationSystem(
            user_id=self.user_id,
            data_dir='/home/ubuntu/email_agent/data/test'
        )
        
        # Register notification handler
        self.notifications_received = []
        self.proactive_notifications.register_notification_handler(self._notification_handler)
    
    def _notification_handler(self, notification, method):
        """Handle notifications for testing."""
        self.notifications_received.append({
            'notification': notification,
            'method': method
        })
    
    def _create_test_emails(self):
        """Create test email data."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)
        
        return [
            {
                'id': 'email1',
                'sender': 'boss@example.com',
                'recipient': 'user@example.com',
                'subject': 'Urgent: Project Deadline',
                'body': """
                Hi Team,
                
                I need the project report by tomorrow. This is very urgent as the client is waiting for it.
                
                Please make sure to include:
                1. Executive summary
                2. Key findings
                3. Recommendations
                
                Let me know if you have any questions.
                
                Thanks,
                Boss
                """,
                'date': now.isoformat(),
                'read': False,
                'category': 'inbox',
                'priority': 'high',
                'attachments': []
            },
            {
                'id': 'email2',
                'sender': 'colleague@example.com',
                'recipient': 'user@example.com',
                'subject': 'Meeting Notes from Yesterday',
                'body': """
                Hi,
                
                Attached are the notes from yesterday's meeting. We discussed the following:
                
                - Project timeline updates
                - Budget allocation
                - Resource planning
                
                Please review and let me know if I missed anything.
                
                Best,
                Colleague
                """,
                'date': yesterday.isoformat(),
                'read': True,
                'category': 'inbox',
                'priority': 'medium',
                'attachments': [
                    {'name': 'meeting_notes.pdf', 'type': 'application/pdf'}
                ]
            },
            {
                'id': 'email3',
                'sender': 'newsletter@example.com',
                'recipient': 'user@example.com',
                'subject': 'Weekly Industry Updates',
                'body': """
                Hello,
                
                Here are this week's industry updates:
                
                - New product launches
                - Market trends
                - Competitor analysis
                
                Click here to read more.
                
                Regards,
                Newsletter Team
                """,
                'date': last_week.isoformat(),
                'read': True,
                'category': 'newsletters',
                'priority': 'low',
                'attachments': []
            },
            {
                'id': 'email4',
                'sender': 'client@example.com',
                'recipient': 'user@example.com',
                'subject': 'Feedback on Proposal',
                'body': """
                Hello,
                
                Thank you for sending the proposal. I've reviewed it and have some feedback:
                
                The pricing structure seems a bit high compared to other vendors. Could you provide a more competitive quote?
                
                I like the approach you've outlined, but I'm concerned about the timeline. Can we accelerate the delivery?
                
                Please let me know your thoughts.
                
                Best regards,
                Client
                """,
                'date': yesterday.isoformat(),
                'read': False,
                'category': 'inbox',
                'priority': 'high',
                'attachments': []
            },
            {
                'id': 'email5',
                'sender': 'support@example.com',
                'recipient': 'user@example.com',
                'subject': 'Your Support Ticket #12345',
                'body': """
                Dear User,
                
                Your support ticket #12345 has been resolved. Here's a summary of the issue and resolution:
                
                Issue: Unable to access the system
                Resolution: Reset user permissions and updated access controls
                
                If you continue to experience issues, please let us know.
                
                Thank you,
                Support Team
                """,
                'date': last_week.isoformat(),
                'read': True,
                'category': 'support',
                'priority': 'medium',
                'attachments': []
            }
        ]
    
    def test_smart_response_generation(self):
        """Test smart response generation."""
        print("\n=== Testing Smart Response Generation ===")
        
        # Test response generation for different email types
        for email in self.test_emails:
            response = self.smart_response.generate_response(email)
            
            print(f"Email: {email['subject']}")
            print(f"Generated Response: {response['text'][:100]}...")
            
            # Assertions
            self.assertIsNotNone(response)
            self.assertIn('text', response)
            self.assertIn('confidence', response)
            self.assertIn('suggestions', response)
            
            # Check response relevance
            if 'urgent' in email['subject'].lower():
                self.assertIn('urgent', response['text'].lower())
            
            if 'meeting' in email['subject'].lower():
                self.assertIn('meeting', response['text'].lower())
            
            # Check for greeting and signature
            self.assertTrue(response['text'].startswith('Hi') or 
                           response['text'].startswith('Hello') or 
                           response['text'].startswith('Dear'))
            
            self.assertTrue('regards' in response['text'].lower() or 
                           'thanks' in response['text'].lower() or 
                           'sincerely' in response['text'].lower())
        
        # Test response customization
        custom_style = {
            'tone': 'formal',
            'length': 'concise',
            'include_greeting': True,
            'include_signature': True,
            'signature': 'Best regards,\nUser'
        }
        
        response = self.smart_response.generate_response(
            self.test_emails[0],
            style=custom_style
        )
        
        print(f"Custom Style Response: {response['text'][:100]}...")
        
        # Assertions for custom style
        self.assertIn(custom_style['signature'], response['text'])
        
        # Test response templates
        template_response = self.smart_response.generate_from_template(
            'meeting_acceptance',
            {'meeting_time': '3:00 PM', 'meeting_date': 'tomorrow'}
        )
        
        print(f"Template Response: {template_response['text'][:100]}...")
        
        # Assertions for template
        self.assertIn('meeting', template_response['text'].lower())
        self.assertIn('3:00 pm', template_response['text'].lower())
        self.assertIn('tomorrow', template_response['text'].lower())
    
    def test_workload_management(self):
        """Test workload management system."""
        print("\n=== Testing Workload Management System ===")
        
        # Extract tasks from emails
        tasks = []
        for email in self.test_emails:
            extracted_tasks = self.workload_manager.extract_tasks_from_email(email)
            tasks.extend(extracted_tasks)
            
            print(f"Email: {email['subject']}")
            print(f"Extracted Tasks: {len(extracted_tasks)}")
            for task in extracted_tasks:
                print(f"  - {task['description'][:50]}...")
        
        # Assertions
        self.assertTrue(len(tasks) > 0)
        
        # Test task prioritization
        prioritized_tasks = self.workload_manager.prioritize_tasks(tasks)
        
        print(f"Prioritized Tasks: {len(prioritized_tasks)}")
        for i, task in enumerate(prioritized_tasks[:3]):
            print(f"  {i+1}. {task['description'][:50]}... (Priority: {task['priority']})")
        
        # Assertions
        self.assertEqual(len(tasks), len(prioritized_tasks))
        
        # Check if high priority email tasks are prioritized higher
        high_priority_tasks = [t for t in prioritized_tasks if t.get('email_priority') == 'high']
        if high_priority_tasks:
            self.assertTrue(high_priority_tasks[0]['priority'] in ['critical', 'high'])
        
        # Test workload metrics
        metrics = self.workload_manager.get_workload_metrics(tasks)
        
        print(f"Workload Metrics:")
        print(f"  Total Tasks: {metrics['total_tasks']}")
        print(f"  High Priority: {metrics['priority_counts'].get('high', 0)}")
        print(f"  Medium Priority: {metrics['priority_counts'].get('medium', 0)}")
        print(f"  Low Priority: {metrics['priority_counts'].get('low', 0)}")
        
        # Assertions
        self.assertEqual(metrics['total_tasks'], len(tasks))
        self.assertIn('priority_counts', metrics)
        self.assertIn('due_today', metrics)
        
        # Test workload recommendations
        recommendations = self.workload_manager.get_workload_recommendations(tasks)
        
        print(f"Workload Recommendations:")
        for rec in recommendations[:3]:
            print(f"  - {rec[:100]}...")
        
        # Assertions
        self.assertTrue(len(recommendations) > 0)
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis capabilities."""
        print("\n=== Testing Sentiment Analysis ===")
        
        # Analyze sentiment for each email
        for email in self.test_emails:
            sentiment = self.sentiment_analyzer.analyze_sentiment(email)
            
            print(f"Email: {email['subject']}")
            print(f"  Primary Emotion: {sentiment['emotions']['primary']}")
            print(f"  Urgency Level: {sentiment['urgency']['level']}")
            print(f"  Overall Sentiment: {sentiment['overall_sentiment']}")
            print(f"  Requires Attention: {sentiment['requires_attention']}")
        
            # Assertions
            self.assertIn('emotions', sentiment)
            self.assertIn('urgency', sentiment)
            self.assertIn('passive_aggressive', sentiment)
            self.assertIn('overall_sentiment', sentiment)
            self.assertIn('requires_attention', sentiment)
            
            # Check specific emails
            if 'urgent' in email['subject'].lower():
                self.assertIn(sentiment['urgency']['level'], ['critical', 'high'])
                self.assertTrue(sentiment['requires_attention'])
            
            if 'feedback' in email['subject'].lower():
                self.assertIn(sentiment['emotions']['primary'], ['concern', 'frustration'])
        
        # Test relationship analysis
        relationship = self.sentiment_analyzer.analyze_relationship(
            [e for e in self.test_emails if e['sender'] == 'boss@example.com']
        )
        
        print(f"Relationship Analysis for boss@example.com:")
        print(f"  Status: {relationship['status']}")
        print(f"  Common Topics: {relationship['common_topics']}")
        print(f"  Suggestions: {relationship['maintenance_suggestions'][:1]}")
        
        # Assertions
        self.assertIn('status', relationship)
        self.assertIn('metrics', relationship)
        self.assertIn('common_topics', relationship)
        self.assertIn('maintenance_suggestions', relationship)
        
        # Test sentiment summary
        summary = self.sentiment_analyzer.get_sentiment_summary(self.test_emails)
        
        print(f"Sentiment Summary:")
        print(f"  Total Emails: {summary['total_emails']}")
        print(f"  Sentiment Percentages: {summary['sentiment_percentages']}")
        print(f"  Dominant Emotions: {summary['dominant_emotions']}")
        
        # Assertions
        self.assertEqual(summary['total_emails'], len(self.test_emails))
        self.assertIn('sentiment_percentages', summary)
        self.assertIn('dominant_emotions', summary)
    
    def test_contextual_learning(self):
        """Test contextual learning features."""
        print("\n=== Testing Contextual Learning ===")
        
        # Track email interactions
        for i, email in enumerate(self.test_emails):
            action = 'read' if i % 2 == 0 else 'reply'
            metadata = {
                'sender': email['sender'],
                'category': email['category'],
                'subject': email['subject'],
                'time_spent': 60 + i * 30,  # Simulated time spent
                'response_time': 300 + i * 60 if action == 'reply' else None,
                'response_length': 200 + i * 50 if action == 'reply' else None
            }
            
            self.contextual_learning.track_email_interaction(
                email['id'],
                action,
                metadata
            )
            
            print(f"Tracked {action} interaction for: {email['subject']}")
        
        # Analyze behavior patterns
        insights = self.contextual_learning.analyze_behavior_patterns()
        
        print(f"Behavior Insights:")
        if insights['status'] == 'success':
            if 'time_insights' in insights:
                print(f"  Time Insights: {insights['time_insights']}")
            if 'response_insights' in insights:
                print(f"  Response Insights: {insights['response_ins
(Content truncated due to size limit. Use line ranges to read in chunks)