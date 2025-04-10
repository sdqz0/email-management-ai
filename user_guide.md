# Email Management AI Agent - User Guide

## Overview

The Email Management AI Agent is a powerful tool designed to help you manage your Gmail inbox more efficiently. It automatically retrieves, categorizes, summarizes, and suggests actions for your emails, providing you with a clear overview of your inbox and helping you focus on what matters most.

## Features

- **Email Retrieval**: Automatically fetches emails from your Gmail inbox
- **Priority Categorization**: Analyzes emails and assigns priority levels (high, medium, low)
- **Email Summarization**: Provides concise summaries of email content
- **Action Detection**: Identifies actionable items and required responses
- **Calendar Event Detection**: Detects meeting invitations and suggests calendar entries
- **Digest Reports**: Generates daily or hourly digest reports of your most important emails
- **User-friendly Interface**: Intuitive web interface for managing your emails

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- A Google account with Gmail
- Google Cloud project with Gmail API enabled

### Step 1: Set Up Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API for your project:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it

### Step 2: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "Internal" as the user type (for personal use)
3. Fill in the required information (app name, user support email, etc.)
4. Add the following scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/gmail.labels`
5. Save and continue

### Step 3: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Desktop app" as the application type
4. Enter a name for your credentials
5. Download the credentials JSON file

### Step 4: Install and Run the Application

1. Clone or download the Email Management AI Agent repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   cd email_agent/src
   python app.py
   ```
4. Open your web browser and navigate to `http://localhost:5000`

### Step 5: Authenticate with Gmail

1. Upload your credentials.json file on the application's home page
2. Click "Authenticate with Gmail" to grant the application access to your Gmail account
3. Follow the Google authentication flow to authorize the application

## Using the Application

### Dashboard Overview

The dashboard provides a quick overview of your email status:
- Unread email count
- High priority email count
- Calendar events detected
- Action items requiring attention

### Email Management

- **Fetch Emails**: Click the "Refresh Emails" button to retrieve the latest emails
- **View Emails**: Browse your emails sorted by priority
- **Filter Emails**: Use the filters to view emails by priority, category, or read status
- **Email Details**: Click on an email to view its details, summary, and suggested actions

### Digest Reports

- **Generate Digest**: Click the "Generate Digest" button to create a summary report
- **View Digest**: The digest shows your most important emails, calendar events, and action items
- **Frequency**: Configure digest frequency (daily or hourly) in the settings

### Calendar Events

- **View Events**: See calendar events detected from your emails
- **Accept/Decline**: Easily accept or decline meeting invitations
- **Add to Calendar**: Add suggested events to your calendar

### Settings

- **Email Preferences**: Configure email fetch interval and maximum emails to fetch
- **Priority Keywords**: Customize keywords used for priority determination
- **Digest Frequency**: Set your preferred digest frequency

## Troubleshooting

### Authentication Issues

- Ensure you've enabled the Gmail API in your Google Cloud project
- Verify that you've downloaded the correct credentials.json file
- Check that you've granted all required permissions during authentication

### Email Retrieval Problems

- Confirm your internet connection is stable
- Verify that your Gmail account is accessible
- Check if you've reached Gmail API quota limits

### Application Errors

- Check the console output for error messages
- Verify that all dependencies are correctly installed
- Restart the application if it becomes unresponsive

## Security Considerations

- Your email data is processed locally and is not sent to external servers
- Authentication tokens are stored securely on your device
- The application uses OAuth 2.0 for secure authentication with Gmail
- No passwords are stored by the application

## Support

If you encounter any issues or have questions about the Email Management AI Agent, please contact support at support@emailagent.example.com.

---

Thank you for using the Email Management AI Agent! We hope it helps you manage your inbox more efficiently.
