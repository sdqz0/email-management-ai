"""
Proactive Notification System for Email Management AI Agent.
Provides smart alerts for time-sensitive matters and important communications.
"""

import datetime
import time
import threading
import json
import os
from collections import defaultdict

class ProactiveNotificationSystem:
    """
    Handles proactive notifications for important emails and time-sensitive matters.
    """
    
    def __init__(self, user_id, data_dir='/home/ubuntu/email_agent/data'):
        """
        Initialize the proactive notification system.
        
        Args:
            user_id (str): Unique identifier for the user
            data_dir (str): Directory to store notification data
        """
        self.user_id = user_id
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.join(data_dir, 'notifications'), exist_ok=True)
        
        # Notification settings file path
        self.settings_path = os.path.join(data_dir, 'notifications', f'{user_id}_settings.json')
        
        # Notification history file path
        self.history_path = os.path.join(data_dir, 'notifications', f'{user_id}_history.json')
        
        # Initialize or load notification settings
        self.settings = self._load_settings()
        
        # Initialize or load notification history
        self.history = self._load_history()
        
        # Initialize notification queue
        self.notification_queue = []
        
        # Initialize notification thread
        self.notification_thread = None
        self.thread_running = False
        
        # Initialize notification handlers
        self.notification_handlers = []
    
    def _load_settings(self):
        """
        Load notification settings from file or initialize new ones.
        
        Returns:
            dict: Notification settings
        """
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading notification settings: {e}")
                return self._initialize_settings()
        else:
            return self._initialize_settings()
    
    def _initialize_settings(self):
        """
        Initialize new notification settings.
        
        Returns:
            dict: New notification settings
        """
        settings = {
            'user_id': self.user_id,
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat(),
            'enabled': True,
            'notification_types': {
                'urgent_emails': {
                    'enabled': True,
                    'threshold': 'high',  # high, medium, low
                    'delivery_method': ['web', 'email'],
                    'quiet_hours': {
                        'enabled': False,
                        'start': '22:00',
                        'end': '08:00'
                    }
                },
                'important_senders': {
                    'enabled': True,
                    'threshold': 'medium',  # high, medium, low
                    'delivery_method': ['web', 'email'],
                    'quiet_hours': {
                        'enabled': False,
                        'start': '22:00',
                        'end': '08:00'
                    }
                },
                'action_items': {
                    'enabled': True,
                    'threshold': 'medium',  # high, medium, low
                    'delivery_method': ['web', 'email'],
                    'quiet_hours': {
                        'enabled': False,
                        'start': '22:00',
                        'end': '08:00'
                    }
                },
                'deadlines': {
                    'enabled': True,
                    'threshold': 'medium',  # high, medium, low
                    'delivery_method': ['web', 'email'],
                    'quiet_hours': {
                        'enabled': False,
                        'start': '22:00',
                        'end': '08:00'
                    },
                    'advance_notice': {
                        'enabled': True,
                        'days': 1
                    }
                },
                'follow_ups': {
                    'enabled': True,
                    'threshold': 'medium',  # high, medium, low
                    'delivery_method': ['web', 'email'],
                    'quiet_hours': {
                        'enabled': False,
                        'start': '22:00',
                        'end': '08:00'
                    },
                    'days_without_response': 3
                },
                'digest': {
                    'enabled': True,
                    'frequency': 'daily',  # daily, twice_daily, hourly
                    'delivery_method': ['web', 'email'],
                    'scheduled_time': '09:00',
                    'include_summary': True,
                    'include_actions': True,
                    'include_deadlines': True
                }
            },
            'delivery_methods': {
                'web': {
                    'enabled': True
                },
                'email': {
                    'enabled': True,
                    'address': '',
                    'format': 'html'  # html, text
                },
                'mobile': {
                    'enabled': False,
                    'device_id': ''
                }
            },
            'global_quiet_hours': {
                'enabled': False,
                'start': '22:00',
                'end': '08:00'
            },
            'workdays': {
                'monday': True,
                'tuesday': True,
                'wednesday': True,
                'thursday': True,
                'friday': True,
                'saturday': False,
                'sunday': False
            }
        }
        
        # Save settings
        self._save_settings(settings)
        
        return settings
    
    def _save_settings(self, settings=None):
        """
        Save notification settings to file.
        
        Args:
            settings (dict, optional): Settings to save
            
        Returns:
            bool: Success indicator
        """
        if settings is None:
            settings = self.settings
        
        try:
            # Update timestamp
            settings['updated_at'] = datetime.datetime.now().isoformat()
            
            # Save to file
            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving notification settings: {e}")
            return False
    
    def _load_history(self):
        """
        Load notification history from file or initialize new one.
        
        Returns:
            dict: Notification history
        """
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading notification history: {e}")
                return self._initialize_history()
        else:
            return self._initialize_history()
    
    def _initialize_history(self):
        """
        Initialize new notification history.
        
        Returns:
            dict: New notification history
        """
        history = {
            'user_id': self.user_id,
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat(),
            'notifications': [],
            'stats': {
                'total_sent': 0,
                'by_type': {
                    'urgent_emails': 0,
                    'important_senders': 0,
                    'action_items': 0,
                    'deadlines': 0,
                    'follow_ups': 0,
                    'digest': 0
                },
                'by_delivery_method': {
                    'web': 0,
                    'email': 0,
                    'mobile': 0
                }
            }
        }
        
        # Save history
        self._save_history(history)
        
        return history
    
    def _save_history(self, history=None):
        """
        Save notification history to file.
        
        Args:
            history (dict, optional): History to save
            
        Returns:
            bool: Success indicator
        """
        if history is None:
            history = self.history
        
        try:
            # Update timestamp
            history['updated_at'] = datetime.datetime.now().isoformat()
            
            # Save to file
            with open(self.history_path, 'w') as f:
                json.dump(history, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving notification history: {e}")
            return False
    
    def update_settings(self, settings_update):
        """
        Update notification settings.
        
        Args:
            settings_update (dict): Settings to update
            
        Returns:
            dict: Updated settings
        """
        # Update settings recursively
        self._update_dict_recursive(self.settings, settings_update)
        
        # Save updated settings
        self._save_settings()
        
        return self.settings
    
    def _update_dict_recursive(self, target, update):
        """
        Update dictionary recursively.
        
        Args:
            target (dict): Target dictionary
            update (dict): Update dictionary
        """
        for key, value in update.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict_recursive(target[key], value)
            else:
                target[key] = value
    
    def register_notification_handler(self, handler):
        """
        Register a notification handler.
        
        Args:
            handler (callable): Notification handler function
            
        Returns:
            bool: Success indicator
        """
        if callable(handler):
            self.notification_handlers.append(handler)
            return True
        return False
    
    def start_notification_thread(self):
        """
        Start the notification thread.
        
        Returns:
            bool: Success indicator
        """
        if self.thread_running:
            return False
        
        self.thread_running = True
        self.notification_thread = threading.Thread(target=self._notification_worker)
        self.notification_thread.daemon = True
        self.notification_thread.start()
        
        return True
    
    def stop_notification_thread(self):
        """
        Stop the notification thread.
        
        Returns:
            bool: Success indicator
        """
        if not self.thread_running:
            return False
        
        self.thread_running = False
        if self.notification_thread:
            self.notification_thread.join(timeout=1.0)
            self.notification_thread = None
        
        return True
    
    def _notification_worker(self):
        """
        Worker function for notification thread.
        """
        while self.thread_running:
            # Process notification queue
            while self.notification_queue:
                notification = self.notification_queue.pop(0)
                self._process_notification(notification)
            
            # Check for scheduled notifications
            self._check_scheduled_notifications()
            
            # Sleep for a short time
            time.sleep(1.0)
    
    def _process_notification(self, notification):
        """
        Process a notification.
        
        Args:
            notification (dict): Notification data
        """
        # Check if notifications are enabled
        if not self.settings['enabled']:
            return
        
        # Check if notification type is enabled
        notification_type = notification.get('type')
        if notification_type not in self.settings['notification_types'] or not self.settings['notification_types'][notification_type]['enabled']:
            return
        
        # Check quiet hours
        if self._is_quiet_hours(notification_type):
            # If in quiet hours, queue for later unless urgent
            if notification.get('urgency') == 'critical':
                pass  # Process even in quiet hours
            else:
                # Store for later delivery
                notification['delayed'] = True
                notification['original_timestamp'] = notification.get('timestamp')
                notification['timestamp'] = datetime.datetime.now().isoformat()
                self._store_delayed_notification(notification)
                return
        
        # Check delivery methods
        delivery_methods = self.settings['notification_types'][notification_type]['delivery_method']
        
        # Deliver notification through each enabled method
        for method in delivery_methods:
            if self.settings['delivery_methods'][method]['enabled']:
                self._deliver_notification(notification, method)
        
        # Add to history
        self._add_to_history(notification)
        
        # Update stats
        self._update_stats(notification)
    
    def _is_quiet_hours(self, notification_type):
        """
        Check if current time is within quiet hours.
        
        Args:
            notification_type (str): Type of notification
            
        Returns:
            bool: True if in quiet hours, False otherwise
        """
        now = datetime.datetime.now()
        current_time = now.strftime('%H:%M')
        
        # Check global quiet hours
        if self.settings['global_quiet_hours']['enabled']:
            start = self.settings['global_quiet_hours']['start']
            end = self.settings['global_quiet_hours']['end']
            
            if self._is_time_between(current_time, start, end):
                return True
        
        # Check notification type specific quiet hours
        if self.settings['notification_types'][notification_type]['quiet_hours']['enabled']:
            start = self.settings['notification_types'][notification_type]['quiet_hours']['start']
            end = self.settings['notification_types'][notification_type]['quiet_hours']['end']
            
            if self._is_time_between(current_time, start, end):
                return True
        
        # Check workdays
        weekday = now.strftime('%A').lower()
        if not self.settings['workdays'][weekday]:
            return True
        
        return False
    
    def _is_time_between(self, current_time, start_time, end_time):
        """
        Check if current time is between start and end times.
        
        Args:
            current_time (str): Current time in HH:MM format
            start_time (str): Start time in HH:MM format
            end_time (str): End time in HH:MM format
            
        Returns:
            bool: True if current time is between start and end times, False otherwise
        """
        # Convert to datetime objects for comparison
        current = datetime.datetime.strptime(current_time, '%H:%M')
        start = datetime.datetime.strptime(start_time, '%H:%M')
        end = datetime.datetime.strptime(end_time, '%H:%M')
        
        # Handle overnight ranges (e.g., 22:00 to 08:00)
        if start > end:
            return current >
(Content truncated due to size limit. Use line ranges to read in chunks)