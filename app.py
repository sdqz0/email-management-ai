"""
Main application module for the Email Management AI Agent.
Integrates all components and provides a web interface.
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# Import custom modules
from auth import GmailAuthenticator
from email_retriever import EmailRetriever
from email_categorizer import EmailCategorizer
from email_summarizer import EmailSummarizer
from action_detector import ActionDetector
from digest_generator import DigestGenerator
from config import WEB_HOST, WEB_PORT, DEBUG_MODE

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
gmail_auth = GmailAuthenticator()
email_categorizer = EmailCategorizer()
email_summarizer = EmailSummarizer()
action_detector = ActionDetector()
digest_generator = DigestGenerator()

# Global variables
processed_emails = []
last_fetch_time = None

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/auth')
def auth():
    """Handle Gmail API authentication."""
    try:
        # Authenticate with Gmail API
        gmail_service = gmail_auth.authenticate()
        session['authenticated'] = True
        return redirect(url_for('dashboard'))
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/dashboard')
def dashboard():
    """Render the main dashboard after authentication."""
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    
    return render_template('dashboard.html')

@app.route('/fetch_emails')
def fetch_emails():
    """Fetch and process emails from Gmail."""
    global processed_emails, last_fetch_time
    
    try:
        # Get Gmail service
        gmail_service = gmail_auth.get_service()
        
        # Initialize email retriever
        email_retriever = EmailRetriever(gmail_service)
        
        # Fetch emails
        emails = email_retriever.get_emails(query="is:unread")
        
        # Process emails
        processed_emails = []
        for email in emails:
            # Categorize email
            categorized_email = email_categorizer.categorize_email(email)
            
            # Summarize email
            summarized_email = email_summarizer.summarize_email(categorized_email)
            
            # Detect actions
            email_with_actions = action_detector.detect_actions(summarized_email)
            
            # Add to processed emails
            processed_emails.append(email_with_actions)
        
        # Update last fetch time
        last_fetch_time = datetime.now()
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully fetched {len(processed_emails)} emails',
            'count': len(processed_emails)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching emails: {str(e)}'
        })

@app.route('/get_digest')
def get_digest():
    """Generate and return an email digest."""
    global processed_emails
    
    if not processed_emails:
        return jsonify({
            'status': 'error',
            'message': 'No emails to generate digest'
        })
    
    try:
        # Generate HTML digest
        html_digest = digest_generator.generate_digest(processed_emails)
        
        # Save digest to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        digest_filename = f'digest_{timestamp}.html'
        digest_path = os.path.join(app.config['UPLOAD_FOLDER'], digest_filename)
        
        with open(digest_path, 'w', encoding='utf-8') as f:
            f.write(html_digest)
        
        return jsonify({
            'status': 'success',
            'message': 'Digest generated successfully',
            'digest_url': url_for('static', filename=f'uploads/{digest_filename}')
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating digest: {str(e)}'
        })

@app.route('/get_email_list')
def get_email_list():
    """Return the list of processed emails."""
    global processed_emails
    
    # Prepare simplified email list for display
    email_list = []
    for email in processed_emails:
        email_list.append({
            'id': email.get('id'),
            'subject': email.get('subject', 'No Subject'),
            'sender': email.get('sender', 'Unknown'),
            'date': email.get('date', ''),
            'priority': email.get('priority', 'medium'),
            'category': email.get('category', 'primary'),
            'is_unread': email.get('is_unread', False),
            'has_calendar_event': bool(email.get('calendar_events')),
            'requires_response': email.get('requires_response', False)
        })
    
    return jsonify({
        'status': 'success',
        'emails': email_list
    })

@app.route('/get_email_details/<email_id>')
def get_email_details(email_id):
    """Return details for a specific email."""
    global processed_emails
    
    # Find the email with the given ID
    email = next((e for e in processed_emails if e.get('id') == email_id), None)
    
    if not email:
        return jsonify({
            'status': 'error',
            'message': f'Email with ID {email_id} not found'
        })
    
    # Prepare calendar event proposals if available
    calendar_proposals = []
    if email.get('calendar_events'):
        for event in email.get('calendar_events', []):
            proposal = action_detector.propose_calendar_event({'calendar_events': [event]})
            if proposal:
                calendar_proposals.append(proposal)
    
    # Return email details
    return jsonify({
        'status': 'success',
        'email': {
            'id': email.get('id'),
            'thread_id': email.get('thread_id'),
            'subject': email.get('subject', 'No Subject'),
            'sender': email.get('sender', 'Unknown'),
            'recipient': email.get('recipient', 'Unknown'),
            'date': email.get('date', ''),
            'body': email.get('body', ''),
            'summary': email.get('summary', ''),
            'priority': email.get('priority', 'medium'),
            'category': email.get('category', 'primary'),
            'is_unread': email.get('is_unread', False),
            'action_items': email.get('action_items', []),
            'calendar_events': email.get('calendar_events', []),
            'calendar_proposals': calendar_proposals,
            'requires_response': email.get('requires_response', False)
        }
    })

@app.route('/upload_credentials', methods=['POST'])
def upload_credentials():
    """Handle upload of Gmail API credentials file."""
    if 'credentials_file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No file part'
        })
    
    file = request.files['credentials_file']
    
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No selected file'
        })
    
    if file:
        filename = secure_filename('credentials.json')
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Update credentials file path in authenticator
        gmail_auth.client_secrets_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        return jsonify({
            'status': 'success',
            'message': 'Credentials file uploaded successfully'
        })

if __name__ == '__main__':
    app.run(host=WEB_HOST, port=WEB_PORT, debug=DEBUG_MODE)
