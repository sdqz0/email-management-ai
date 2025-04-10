"""
Authentication module for Gmail API access.
Handles OAuth 2.0 flow and token management.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import (
    GMAIL_API_SCOPES,
    CLIENT_SECRETS_FILE,
    TOKEN_PICKLE_FILE,
    API_SERVICE_NAME,
    API_VERSION
)

class GmailAuthenticator:
    """
    Handles authentication with Gmail API using OAuth 2.0.
    """
    
    def __init__(self):
        """
        Initialize the authenticator with required configuration.
        """
        self.scopes = GMAIL_API_SCOPES
        self.client_secrets_file = CLIENT_SECRETS_FILE
        self.token_pickle_file = TOKEN_PICKLE_FILE
        self.api_service_name = API_SERVICE_NAME
        self.api_version = API_VERSION
        self.credentials = None
        self.service = None
    
    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth 2.0.
        
        Returns:
            googleapiclient.discovery.Resource: Gmail API service instance
        """
        # Check if token pickle file exists
        if os.path.exists(self.token_pickle_file):
            with open(self.token_pickle_file, 'rb') as token:
                self.credentials = pickle.load(token)
        
        # If credentials don't exist or are invalid, get new ones
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.scopes)
                self.credentials = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_pickle_file, 'wb') as token:
                pickle.dump(self.credentials, token)
        
        # Build the Gmail API service
        self.service = build(
            self.api_service_name, 
            self.api_version, 
            credentials=self.credentials
        )
        
        return self.service
    
    def get_service(self):
        """
        Get the Gmail API service instance.
        If not authenticated, authenticate first.
        
        Returns:
            googleapiclient.discovery.Resource: Gmail API service instance
        """
        if not self.service:
            return self.authenticate()
        return self.service
