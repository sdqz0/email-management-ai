"""
Integration test script for Email Management AI Agent.
This script tests the integration between different components.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules to test
from src.auth import GmailAuthenticator
from src.email_retriever import EmailRetriever
from src.email_categorizer import EmailCategorizer
from src.email_summarizer import EmailSummarizer
from src.action_detector import ActionDetector
from src.digest_generator import DigestGenerator

class TestEmailAgentIntegration(unittest.TestCase):
    """Test the integration between different components of the Email Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the Gmail service
        self.mock_gmail_service = MagicMock()
        
        # Initialize components
        self.email_retriever = EmailRetriever(self.mock_gmail_service)
        self.email_categorizer = EmailCategorizer()
        self.email_summarizer = EmailSummarizer()
        self.action_detector = ActionDetector()
        self.digest_generator = DigestGenerator()
        
        # Create sample email data
        self.sample_emails = self._create_sample_emails()
    
    def _create_sample_emails(self):
        """Create sample email data for testing."""
        return [
            {
                'id': '12345',
                'thread_id': 'thread1',
                'subject': 'URGENT: Meeting tomorrow',
                'sender': 'boss@example.com',
                'recipient': 'user@example.com',
                'date': 'Mon, 7 Apr 2025 10:00:00 +0000',
                'body': 'We need to discuss the project status ASAP. Please prepare a status report for our meeting tomorrow at 2:00 PM.',
                'snippet': 'We need to discuss the project status ASAP.',
                'labels': ['INBOX', 'UNREAD'],
                'is_unread': True
            },
            {
                'id': '67890',
                'thread_id': 'thread2',
                'subject': 'Weekly team meeting',
                'sender': 'manager@example.com',
                'recipient': 'user@example.com',
                'date': 'Mon, 7 Apr 2025 11:00:00 +0000',
                'body': 'Our weekly team meeting will be held on Friday at 10:00 AM. Please prepare updates on your assigned tasks.',
                'snippet': 'Our weekly team meeting will be held on Friday at 10:00 AM.',
                'labels': ['INBOX', 'UNREAD'],
                'is_unread': True
            },
            {
                'id': 'abcde',
                'thread_id': 'thread3',
                'subject': 'Newsletter: Weekly updates',
                'sender': 'newsletter@example.com',
                'recipient': 'user@example.com',
                'date': 'Mon, 7 Apr 2025 09:00:00 +0000',
                'body': 'Check out our latest newsletter with promotions and updates on our products.',
                'snippet': 'Check out our latest newsletter with promotions.',
                'labels': ['INBOX'],
                'is_unread': False
            }
        ]
    
    def test_full_email_processing_pipeline(self):
        """Test the full email processing pipeline."""
        processed_emails = []
        
        # Mock the email retrieval
        with patch.object(self.email_retriever, 'get_emails', return_value=self.sample_emails):
            # Retrieve emails
            emails = self.email_retriever.get_emails()
            
            # Process each email through the pipeline
            for email in emails:
                # Categorize email
                categorized_email = self.email_categorizer.categorize_email(email)
                
                # Summarize email
                summarized_email = self.email_summarizer.summarize_email(categorized_email)
                
                # Detect actions
                email_with_actions = self.action_detector.detect_actions(summarized_email)
                
                # Add to processed emails
                processed_emails.append(email_with_actions)
        
        # Generate digest
        html_digest = self.digest_generator.generate_digest(processed_emails)
        text_digest = self.digest_generator.generate_text_digest(processed_emails)
        
        # Assertions for the processed emails
        self.assertEqual(len(processed_emails), 3)
        
        # Check first email (urgent meeting)
        self.assertEqual(processed_emails[0]['priority'], 'high')
        self.assertTrue(processed_emails[0]['has_calendar_event'])
        self.assertTrue(len(processed_emails[0]['action_items']) > 0)
        
        # Check second email (weekly meeting)
        self.assertEqual(processed_emails[1]['priority'], 'medium')
        self.assertTrue(processed_emails[1]['has_calendar_event'])
        
        # Check third email (newsletter)
        self.assertEqual(processed_emails[2]['priority'], 'low')
        self.assertFalse(processed_emails[2]['has_calendar_event'])
        
        # Check digest generation
        self.assertIn('URGENT: Meeting tomorrow', html_digest)
        self.assertIn('Weekly team meeting', html_digest)
        self.assertIn('URGENT: Meeting tomorrow', text_digest)
        self.assertIn('Weekly team meeting', text_digest)

if __name__ == '__main__':
    unittest.main()
