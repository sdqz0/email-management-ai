"""
WSGI entry point for the Email Management AI Agent.
Used for production deployment.
"""

from app import app

if __name__ == "__main__":
    app.run()
