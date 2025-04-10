"""
Contextual Learning module for Email Management AI Agent.
Enables the system to learn from user behavior and adapt to individual work patterns.
"""

import json
import os
import datetime
import numpy as np
from collections import defaultdict, Counter

class ContextualLearningSystem:
    """
    Handles learning from user behavior and adapting functionality to match individual work patterns.
    """
    
    def __init__(self, user_id, data_dir='/home/ubuntu/email_agent/data'):
        """
        Initialize the contextual learning system.
        
        Args:
            user_id (str): Unique identifier for the user
            data_dir (str): Directory to store learning data
        """
        self.user_id = user_id
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.join(data_dir, 'user_models'), exist_ok=True)
        
        # User model file path
        self.model_path = os.path.join(data_dir, 'user_models', f'{user_id}_model.json')
        
        # Initialize or load user model
        self.user_model = self._load_user_model()
        
        # Initialize behavior tracking
        self.behavior_tracking = {
            'email_interactions': [],
            'response_patterns': [],
            'time_patterns': [],
            'category_adjustments': []
        }
        
        # Learning parameters
        self.learning_rate = 0.2  # How quickly the model adapts to new behaviors
        self.min_observations = 5  # Minimum observations before making adaptations
    
    def _load_user_model(self):
        """
        Load user model from file or initialize a new one.
        
        Returns:
            dict: User model
        """
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading user model: {e}")
                return self._initialize_user_model()
        else:
            return self._initialize_user_model()
    
    def _initialize_user_model(self):
        """
        Initialize a new user model.
        
        Returns:
            dict: New user model
        """
        return {
            'user_id': self.user_id,
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat(),
            'version': '1.0',
            'interaction_count': 0,
            'preferences': {
                'email_processing': {
                    'preferred_times': [],
                    'processing_frequency': 'multiple_daily',
                    'batch_processing': False,
                    'auto_categorization': True,
                    'auto_prioritization': True
                },
                'response_preferences': {
                    'response_style': 'neutral',
                    'response_length': 'medium',
                    'greeting_style': 'standard',
                    'closing_style': 'standard',
                    'formality_level': 'neutral'
                },
                'notification_preferences': {
                    'notification_frequency': 'medium',
                    'urgent_only': False,
                    'quiet_hours': {
                        'enabled': False,
                        'start': '22:00',
                        'end': '08:00'
                    }
                },
                'ui_preferences': {
                    'default_view': 'inbox',
                    'theme': 'light',
                    'density': 'medium',
                    'sort_order': 'date_desc'
                }
            },
            'learned_patterns': {
                'email_importance': {},
                'sender_importance': {},
                'category_mapping': {},
                'response_patterns': {},
                'time_patterns': {
                    'active_hours': {},
                    'email_checking_times': [],
                    'response_times': {}
                },
                'topic_interests': {}
            },
            'custom_categories': [],
            'sender_relationships': {}
        }
    
    def _save_user_model(self):
        """
        Save user model to file.
        
        Returns:
            bool: Success indicator
        """
        try:
            # Update timestamp
            self.user_model['updated_at'] = datetime.datetime.now().isoformat()
            
            # Save to file
            with open(self.model_path, 'w') as f:
                json.dump(self.user_model, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving user model: {e}")
            return False
    
    def track_email_interaction(self, email_id, action, metadata=None):
        """
        Track user interaction with an email.
        
        Args:
            email_id (str): Email identifier
            action (str): Action performed (read, reply, delete, archive, flag, etc.)
            metadata (dict, optional): Additional metadata about the interaction
            
        Returns:
            bool: Success indicator
        """
        # Create interaction record
        interaction = {
            'email_id': email_id,
            'action': action,
            'timestamp': datetime.datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Add to behavior tracking
        self.behavior_tracking['email_interactions'].append(interaction)
        
        # Update interaction count
        self.user_model['interaction_count'] += 1
        
        # Process the interaction for learning
        self._process_interaction(interaction)
        
        # Save model periodically (every 10 interactions)
        if self.user_model['interaction_count'] % 10 == 0:
            self._save_user_model()
        
        return True
    
    def _process_interaction(self, interaction):
        """
        Process an interaction for learning.
        
        Args:
            interaction (dict): Interaction data
        """
        action = interaction['action']
        metadata = interaction['metadata']
        
        # Process based on action type
        if action == 'read':
            self._process_read_action(interaction)
        elif action == 'reply':
            self._process_reply_action(interaction)
        elif action in ['delete', 'archive']:
            self._process_disposition_action(interaction)
        elif action == 'flag':
            self._process_flag_action(interaction)
        elif action == 'categorize':
            self._process_categorize_action(interaction)
        elif action == 'prioritize':
            self._process_prioritize_action(interaction)
        
        # Track time patterns
        self._track_time_pattern(action, metadata)
    
    def _process_read_action(self, interaction):
        """
        Process a read action.
        
        Args:
            interaction (dict): Interaction data
        """
        metadata = interaction['metadata']
        
        # Extract relevant data
        email_id = interaction['email_id']
        sender = metadata.get('sender')
        category = metadata.get('category')
        subject = metadata.get('subject', '')
        time_spent = metadata.get('time_spent', 0)  # seconds spent reading
        
        # Update sender importance based on time spent
        if sender and time_spent > 0:
            self._update_sender_importance(sender, time_spent)
        
        # Update topic interests based on subject
        if subject:
            self._update_topic_interests(subject, time_spent)
    
    def _process_reply_action(self, interaction):
        """
        Process a reply action.
        
        Args:
            interaction (dict): Interaction data
        """
        metadata = interaction['metadata']
        
        # Extract relevant data
        email_id = interaction['email_id']
        sender = metadata.get('sender')
        category = metadata.get('category')
        response_time = metadata.get('response_time', 0)  # seconds between receiving and replying
        response_length = metadata.get('response_length', 0)  # characters in response
        
        # Update sender importance based on quick response
        if sender and response_time is not None:
            importance_factor = self._calculate_response_importance(response_time)
            self._update_sender_importance(sender, importance_factor)
        
        # Track response pattern
        if sender and response_time is not None and response_length is not None:
            self._track_response_pattern(sender, response_time, response_length)
    
    def _process_disposition_action(self, interaction):
        """
        Process a disposition action (delete/archive).
        
        Args:
            interaction (dict): Interaction data
        """
        metadata = interaction['metadata']
        
        # Extract relevant data
        email_id = interaction['email_id']
        sender = metadata.get('sender')
        category = metadata.get('category')
        read_before_action = metadata.get('read_before_action', False)
        
        # Update sender importance (negative if deleted without reading)
        if sender:
            if interaction['action'] == 'delete' and not read_before_action:
                self._update_sender_importance(sender, -5)  # Negative importance
    
    def _process_flag_action(self, interaction):
        """
        Process a flag action.
        
        Args:
            interaction (dict): Interaction data
        """
        metadata = interaction['metadata']
        
        # Extract relevant data
        email_id = interaction['email_id']
        sender = metadata.get('sender')
        category = metadata.get('category')
        flag_type = metadata.get('flag_type', 'important')
        
        # Update sender importance based on flagging
        if sender:
            importance_factor = 5 if flag_type == 'important' else 3
            self._update_sender_importance(sender, importance_factor)
        
        # Update email importance
        if email_id:
            self._update_email_importance(email_id, flag_type)
    
    def _process_categorize_action(self, interaction):
        """
        Process a categorize action.
        
        Args:
            interaction (dict): Interaction data
        """
        metadata = interaction['metadata']
        
        # Extract relevant data
        email_id = interaction['email_id']
        sender = metadata.get('sender')
        original_category = metadata.get('original_category')
        new_category = metadata.get('new_category')
        
        # Track category adjustment
        if original_category and new_category and original_category != new_category:
            self._track_category_adjustment(sender, original_category, new_category)
    
    def _process_prioritize_action(self, interaction):
        """
        Process a prioritize action.
        
        Args:
            interaction (dict): Interaction data
        """
        metadata = interaction['metadata']
        
        # Extract relevant data
        email_id = interaction['email_id']
        sender = metadata.get('sender')
        original_priority = metadata.get('original_priority')
        new_priority = metadata.get('new_priority')
        
        # Update sender importance based on priority change
        if sender and original_priority and new_priority:
            priority_change = self._calculate_priority_change(original_priority, new_priority)
            self._update_sender_importance(sender, priority_change)
    
    def _update_sender_importance(self, sender, importance_factor):
        """
        Update importance of a sender.
        
        Args:
            sender (str): Email sender
            importance_factor (float): Importance factor to apply
        """
        # Initialize if not exists
        if sender not in self.user_model['learned_patterns']['sender_importance']:
            self.user_model['learned_patterns']['sender_importance'][sender] = {
                'importance_score': 0,
                'interaction_count': 0,
                'last_interaction': None
            }
        
        # Get current data
        sender_data = self.user_model['learned_patterns']['sender_importance'][sender]
        
        # Update importance score with learning rate
        current_score = sender_data['importance_score']
        interaction_count = sender_data['interaction_count']
        
        # Apply diminishing learning rate as interactions increase
        effective_learning_rate = self.learning_rate / (1 + (interaction_count / 50))
        
        # Update score
        new_score = current_score + (importance_factor * effective_learning_rate)
        
        # Ensure score stays within reasonable bounds
        new_score = max(-10, min(10, new_score))
        
        # Update data
        sender_data['importance_score'] = new_score
        sender_data['interaction_count'] += 1
        sender_data['last_interaction'] = datetime.datetime.now().isoformat()
        
        # Update sender relationship if score changes significantly
        if abs(new_score - current_score) > 1:
            self._update_sender_relationship(sender, new_score)
    
    def _update_sender_relationship(self, sender, importance_score):
        """
        Update relationship status with a sender.
        
        Args:
            sender (str): Email sender
            importance_score (float): Current importance score
        """
        # Determine relationship status based on importance score
        if importance_score >= 7:
            relationship = 'vip'
        elif importance_score >= 4:
            relationship = 'important'
        elif importance_score >= 1:
            relationship = 'regular'
        elif importance_score >= -2:
            relationship = 'neutral'
        else:
            relationship = 'low_priority'
        
        # Update sender relationships
        self.user_model['sender_relationships'][sender] = relationship
    
    def _update_email_importance(self, email_id, flag_type):
        """
        Update importance of an email.
        
        Args:
            email_id (str): Email identifier
            flag_type (str): Type of flag
        """
        # Map flag types to importance scores
        importance_map = {
            'important': 5,
            'follow_up': 4,
            'to_do': 4,
            'custom': 3
        }
        
        importance_score = importance_map.get(flag_type, 3)
        
        # Update email importance
        self.user_model['learned_patterns']['email_importance'][email_id] = importance_score
    
    def _update_topic_interests(self, subject, time_spent):
        """
        Update topic interests based on email subject and time spent.
        
        Args:
            subject (str): Email subject
            time_spent (int): Time spent reading in seconds
        """
        # Extract keywords from subject
        keywords = self._extract_keywords(subject)
        
        # Calculate interest factor based on time spent
        interest_factor = min(time_spent / 60, 5)  # Cap at 5 minutes
        
        # Update topic interests
        for keyword in keywords:
            if keyword not in self.user_model['learned_patterns']['topic_interests']:
                self.user_model['learned_patterns']['topic_interests'][keyword] = {
                    'interest_score': 0,
                    'occurrence_count': 0
                }
            
            # Update interest score
            topic_data = self.user_model['learned_patterns']['topic_interests'][keyword]
            current_score = topic_dat
(Content truncated due to size limit. Use line ranges to read in chunks)