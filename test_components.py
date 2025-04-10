"""
Test script for Email Management AI Agent.
This script tests the functionality of the various components.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules to test
from src.email_retriever import EmailRetriever
from src.email_categorizer import EmailCategorizer
from src.email_summarizer import EmailSummarizer
from src.action_detector import ActionDetector
from src.digest_generator import DigestGenerator

class TestEmailRetriever(unittest.TestCase):
    """Test the EmailRetriever class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_gmail_service = MagicMock()
        self.email_retriever = EmailRetriever(self.mock_gmail_service)
    
    def test_get_emails(self):
        """Test retrieving emails."""
        # Mock the Gmail API response
        mock_response = {
            'messages': [
                {'id': '12345'},
                {'id': '67890'}
            ]
        }
        self.mock_gmail_service.users().messages().list().execute.return_value = mock_response
        
        # Mock the message details
        mock_message_1 = {
            'id': '12345',
            'threadId': 'thread1',
            'labelIds': ['INBOX', 'UNREAD'],
            'snippet': 'This is a test email',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'Date', 'value': 'Mon, 7 Apr 2025 10:00:00 +0000'},
                    {'name': 'To', 'value': 'user@example.com'}
                ],
                'body': {'data': 'VGhpcyBpcyBhIHRlc3QgZW1haWwgYm9keQ=='}  # "This is a test email body" in base64
            }
        }
        
        mock_message_2 = {
            'id': '67890',
            'threadId': 'thread2',
            'labelIds': ['INBOX'],
            'snippet': 'Another test email',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Another Test'},
                    {'name': 'From', 'value': 'another@example.com'},
                    {'name': 'Date', 'value': 'Mon, 7 Apr 2025 11:00:00 +0000'},
                    {'name': 'To', 'value': 'user@example.com'}
                ],
                'body': {'data': 'QW5vdGhlciB0ZXN0IGVtYWlsIGJvZHk='}  # "Another test email body" in base64
            }
        }
        
        # Configure the mock to return the message details
        self.mock_gmail_service.users().messages().get().execute.side_effect = [
            mock_message_1,
            mock_message_2
        ]
        
        # Call the method
        emails = self.email_retriever.get_emails(max_results=2)
        
        # Assertions
        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[0]['id'], '12345')
        self.assertEqual(emails[0]['subject'], 'Test Subject')
        self.assertEqual(emails[0]['sender'], 'test@example.com')
        self.assertTrue(emails[0]['is_unread'])
        self.assertEqual(emails[1]['id'], '67890')
        self.assertEqual(emails[1]['subject'], 'Another Test')
        self.assertEqual(emails[1]['sender'], 'another@example.com')
        self.assertFalse(emails[1]['is_unread'])

class TestEmailCategorizer(unittest.TestCase):
    """Test the EmailCategorizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.categorizer = EmailCategorizer()
    
    def test_determine_priority(self):
        """Test priority determination."""
        # High priority email
        high_priority_email = {
            'subject': 'URGENT: Meeting tomorrow',
            'sender': 'boss@example.com',
            'body': 'We need to discuss this ASAP.',
            'snippet': 'We need to discuss this ASAP.'
        }
        
        # Medium priority email
        medium_priority_email = {
            'subject': 'Team meeting next week',
            'sender': 'colleague@example.com',
            'body': 'Let\'s schedule a meeting to review progress.',
            'snippet': 'Let\'s schedule a meeting to review progress.'
        }
        
        # Low priority email
        low_priority_email = {
            'subject': 'Newsletter: Weekly updates',
            'sender': 'newsletter@example.com',
            'body': 'Check out our latest newsletter with promotions.',
            'snippet': 'Check out our latest newsletter with promotions.'
        }
        
        # Test priority determination
        categorized_high = self.categorizer.categorize_email(high_priority_email)
        categorized_medium = self.categorizer.categorize_email(medium_priority_email)
        categorized_low = self.categorizer.categorize_email(low_priority_email)
        
        self.assertEqual(categorized_high['priority'], 'high')
        self.assertEqual(categorized_medium['priority'], 'medium')
        self.assertEqual(categorized_low['priority'], 'low')
    
    def test_detect_calendar_event(self):
        """Test calendar event detection."""
        # Email with calendar event
        calendar_email = {
            'subject': 'Meeting invitation',
            'sender': 'colleague@example.com',
            'body': 'Let\'s meet tomorrow at 3:00 PM to discuss the project.',
            'snippet': 'Let\'s meet tomorrow at 3:00 PM to discuss the project.'
        }
        
        # Email without calendar event
        non_calendar_email = {
            'subject': 'Project update',
            'sender': 'colleague@example.com',
            'body': 'Here\'s the latest update on the project.',
            'snippet': 'Here\'s the latest update on the project.'
        }
        
        # Test calendar event detection
        categorized_calendar = self.categorizer.categorize_email(calendar_email)
        categorized_non_calendar = self.categorizer.categorize_email(non_calendar_email)
        
        self.assertTrue(categorized_calendar['has_calendar_event'])
        self.assertFalse(categorized_non_calendar['has_calendar_event'])

class TestEmailSummarizer(unittest.TestCase):
    """Test the EmailSummarizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.summarizer = EmailSummarizer()
    
    def test_summarize_email(self):
        """Test email summarization."""
        # Create a test email with a long body
        email = {
            'subject': 'Project Update',
            'sender': 'colleague@example.com',
            'body': """
            Hello team,
            
            I wanted to provide an update on the project status. We have completed the first phase of development and are now moving to the testing phase.
            
            Key accomplishments:
            1. Completed the user interface design
            2. Implemented the backend API
            3. Set up the database schema
            
            Next steps:
            1. Begin unit testing
            2. Conduct integration testing
            3. Prepare for user acceptance testing
            
            Please let me know if you have any questions or concerns.
            
            Best regards,
            John
            """
        }
        
        # Summarize the email
        summarized_email = self.summarizer.summarize_email(email)
        
        # Assertions
        self.assertIn('summary', summarized_email)
        self.assertTrue(len(summarized_email['summary']) < len(email['body']))
        self.assertGreater(len(summarized_email['summary']), 0)

class TestActionDetector(unittest.TestCase):
    """Test the ActionDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.action_detector = ActionDetector()
    
    def test_detect_actions(self):
        """Test action item detection."""
        # Email with action items
        action_email = {
            'subject': 'Action Required: Review Document',
            'sender': 'manager@example.com',
            'body': """
            Hi,
            
            Please review the attached document by Friday.
            
            Also, can you update the project timeline and send it to the team?
            
            Thanks,
            Manager
            """
        }
        
        # Email without action items
        non_action_email = {
            'subject': 'FYI: Project Update',
            'sender': 'colleague@example.com',
            'body': """
            Hi,
            
            Just wanted to let you know that the project is progressing well.
            
            Thanks,
            Colleague
            """
        }
        
        # Test action detection
        email_with_actions = self.action_detector.detect_actions(action_email)
        email_without_actions = self.action_detector.detect_actions(non_action_email)
        
        self.assertTrue(len(email_with_actions['action_items']) > 0)
        self.assertEqual(len(email_without_actions['action_items']), 0)
    
    def test_requires_response(self):
        """Test response requirement detection."""
        # Email requiring response
        response_email = {
            'subject': 'Question about project',
            'sender': 'colleague@example.com',
            'body': 'What do you think about the new design? Let me know your thoughts.'
        }
        
        # Email not requiring response
        non_response_email = {
            'subject': 'FYI: Project Update',
            'sender': 'colleague@example.com',
            'body': 'Just wanted to keep you updated on the project progress.'
        }
        
        # Test response requirement detection
        email_requires_response = self.action_detector.detect_actions(response_email)
        email_no_response = self.action_detector.detect_actions(non_response_email)
        
        self.assertTrue(email_requires_response['requires_response'])
        self.assertFalse(email_no_response['requires_response'])

class TestDigestGenerator(unittest.TestCase):
    """Test the DigestGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.digest_generator = DigestGenerator()
    
    def test_generate_digest(self):
        """Test digest generation."""
        # Create test emails
        emails = [
            {
                'id': '12345',
                'subject': 'URGENT: Meeting tomorrow',
                'sender': 'boss@example.com',
                'date': 'Mon, 7 Apr 2025 10:00:00 +0000',
                'body': 'We need to discuss this ASAP.',
                'summary': 'Urgent meeting discussion needed.',
                'priority': 'high',
                'is_unread': True,
                'action_items': ['Prepare for meeting', 'Bring project documents']
            },
            {
                'id': '67890',
                'subject': 'Project Update',
                'sender': 'colleague@example.com',
                'date': 'Mon, 7 Apr 2025 11:00:00 +0000',
                'body': 'Here\'s the latest update on the project.',
                'summary': 'Project progress update provided.',
                'priority': 'medium',
                'is_unread': True,
                'action_items': []
            },
            {
                'id': 'abcde',
                'subject': 'Newsletter: Weekly updates',
                'sender': 'newsletter@example.com',
                'date': 'Mon, 7 Apr 2025 09:00:00 +0000',
                'body': 'Check out our latest newsletter with promotions.',
                'summary': 'Weekly newsletter with promotions.',
                'priority': 'low',
                'is_unread': False,
                'action_items': []
            }
        ]
        
        # Generate HTML digest
        html_digest = self.digest_generator.generate_digest(emails)
        
        # Generate text digest
        text_digest = self.digest_generator.generate_text_digest(emails)
        
        # Assertions
        self.assertIn('URGENT: Meeting tomorrow', html_digest)
        self.assertIn('Project Update', html_digest)
        self.assertIn('boss@example.com', html_digest)
        
        self.assertIn('URGENT: Meeting tomorrow', text_digest)
        self.assertIn('Project Update', text_digest)
        self.assertIn('boss@example.com', text_digest)

if __name__ == '__main__':
    unittest.main()
