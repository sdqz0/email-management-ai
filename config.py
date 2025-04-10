"""
Modified configuration file for Email Management AI Agent.
Adjusted for production deployment on Render.
"""

import os

# Web server configuration
WEB_HOST = '0.0.0.0'  # Listen on all interfaces
WEB_PORT = int(os.environ.get('PORT', 5000))  # Use PORT environment variable provided by Render
DEBUG_MODE = False  # Disable debug mode in production

# Gmail API configuration
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

# Application paths
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Email processing configuration
MAX_EMAILS_TO_FETCH = 50
EMAIL_FETCH_INTERVAL = 15  # minutes
