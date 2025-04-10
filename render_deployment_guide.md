# Render Deployment Guide for Email Management AI Agent

This guide provides step-by-step instructions for deploying your Email Management AI Agent to Render for permanent hosting.

## Prerequisites

- A Render account (sign up at [render.com](https://render.com))
- The deployment package (`email_agent_permanent_deploy.zip`)

## Deployment Steps

### 1. Create a Render Account

1. Go to [render.com](https://render.com) and sign up for a free account
2. Verify your email address and complete the registration process

### 2. Prepare Your Code Repository

You have two options:

#### Option A: Deploy via GitHub/GitLab (Recommended)

1. Create a new repository on GitHub or GitLab
2. Extract the deployment package and push the code to your repository:
   ```bash
   unzip email_agent_permanent_deploy.zip -d email_management_app
   cd email_management_app
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repository-url>
   git push -u origin main
   ```

#### Option B: Deploy via Direct Upload

1. Extract the deployment package to a local folder
2. You'll upload this directly to Render in the next steps

### 3. Create a New Web Service on Render

1. Log in to your Render dashboard
2. Click the "New +" button in the top right corner
3. Select "Web Service" from the dropdown menu

### 4. Configure Your Web Service

#### If using GitHub/GitLab (Option A):

1. Connect your GitHub/GitLab account when prompted
2. Select the repository you created
3. Click "Connect"

#### If using Direct Upload (Option B):

1. Select "Upload Files" option
2. Upload all files from your extracted deployment package

### 5. Configure Deployment Settings

Fill in the following settings:

- **Name**: `email-management-ai` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose the region closest to your users
- **Branch**: `main` (or your default branch)
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn app:app`
- **Plan**: Select the "Free" plan

### 6. Environment Variables (Optional)

If you want to connect to a real Gmail account later, you'll need to add these environment variables:
- `GOOGLE_CLIENT_ID`: Your Google API client ID
- `GOOGLE_CLIENT_SECRET`: Your Google API client secret
- `FLASK_SECRET_KEY`: A random string for Flask session security

### 7. Deploy Your Application

1. Click "Create Web Service"
2. Render will start building and deploying your application
3. This process may take 5-10 minutes to complete

### 8. Access Your Deployed Application

Once deployment is complete:

1. Render will provide a permanent URL for your application (e.g., `https://email-management-ai.onrender.com`)
2. Click on this URL to access your application
3. Your Email Management AI Agent is now permanently deployed!

## Troubleshooting

If you encounter any issues during deployment:

1. Check the build logs in the Render dashboard
2. Ensure all dependencies are correctly listed in `requirements.txt`
3. Verify that the `build.sh` script is executable
4. Check that your `Procfile` contains the correct start command

## Maintaining Your Deployment

- Your application will remain deployed permanently on the free tier
- The free tier may have some limitations on usage and may sleep after periods of inactivity
- To keep your application always active, consider upgrading to a paid plan

## Next Steps

After successful deployment:

1. Test all features of your Email Management AI Agent
2. Set up Google API credentials if you want to connect to a real Gmail account
3. Share your application URL with team members who need access
