"""
Email retrieval module for fetching emails from Gmail.
"""

import base64
import time
from googleapiclient.errors import HttpError
from config import MAX_EMAILS_PER_FETCH, BATCH_SIZE

class EmailRetriever:
    """
    Handles retrieval of emails from Gmail API.
    """
    
    def __init__(self, gmail_service):
        """
        Initialize the email retriever with Gmail API service.
        
        Args:
            gmail_service: Authenticated Gmail API service instance
        """
        self.gmail_service = gmail_service
    
    def get_emails(self, max_results=MAX_EMAILS_PER_FETCH, query=None, label_ids=None):
        """
        Fetch emails from Gmail inbox.
        
        Args:
            max_results (int): Maximum number of emails to retrieve
            query (str): Gmail search query
            label_ids (list): List of label IDs to filter by
            
        Returns:
            list: List of email messages
        """
        try:
            # Prepare request parameters
            request = {
                'userId': 'me',
                'maxResults': max_results
            }
            
            if query:
                request['q'] = query
                
            if label_ids:
                request['labelIds'] = label_ids
            
            # Get message IDs
            response = self.gmail_service.users().messages().list(**request).execute()
            messages = response.get('messages', [])
            
            # If no messages found
            if not messages:
                return []
            
            # Fetch full message details in batches
            email_list = []
            for i in range(0, len(messages), BATCH_SIZE):
                batch = messages[i:i+BATCH_SIZE]
                batch_emails = self._get_email_details(batch)
                email_list.extend(batch_emails)
                
                # Avoid rate limiting
                if i + BATCH_SIZE < len(messages):
                    time.sleep(1)
            
            return email_list
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def _get_email_details(self, message_list):
        """
        Get detailed information for a batch of email messages.
        
        Args:
            message_list (list): List of message objects with IDs
            
        Returns:
            list: List of detailed email messages
        """
        emails = []
        
        for message in message_list:
            msg_id = message['id']
            try:
                # Get the message details
                message = self.gmail_service.users().messages().get(
                    userId='me', 
                    id=msg_id, 
                    format='full'
                ).execute()
                
                # Extract email details
                email_data = self._parse_email_message(message)
                emails.append(email_data)
                
            except HttpError as error:
                print(f'Error retrieving message {msg_id}: {error}')
                continue
                
        return emails
    
    def _parse_email_message(self, message):
        """
        Parse Gmail API message into a more usable format.
        
        Args:
            message (dict): Gmail API message object
            
        Returns:
            dict: Parsed email data
        """
        # Get headers
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
        to = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Unknown')
        
        # Get message body
        body = self._get_message_body(message['payload'])
        
        # Get labels
        labels = message.get('labelIds', [])
        
        # Check if message is unread
        is_unread = 'UNREAD' in labels
        
        # Create email object
        email = {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': subject,
            'sender': sender,
            'recipient': to,
            'date': date,
            'body': body,
            'labels': labels,
            'is_unread': is_unread,
            'snippet': message.get('snippet', '')
        }
        
        return email
    
    def _get_message_body(self, payload):
        """
        Extract the message body from the payload.
        
        Args:
            payload (dict): Message payload
            
        Returns:
            str: Message body text
        """
        # Check if the payload has parts
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif 'parts' in part:
                    # Recursive call for multipart messages
                    body = self._get_message_body(part)
                    if body:
                        return body
        
        # If no parts, check if body contains data
        elif 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return "No body content found"
