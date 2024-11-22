import json
import os
class Config:
    def __init__(self):
        self.update_interval = None
        self.subscriptions_file = None
        self.notification_settings = None
        self.openAI_token=os.getenv("OPENAI_TOKEN")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.openAI_URL=os.getenv("OPENAI_URL")
        
        self.load_config()
    
    def load_config(self):
        
        with open('config.json', 'r') as f:
            config = json.load(f)
            self.notification_settings = config.get('notification_settings')
            self.subscriptions_file = config.get('subscriptions_file')
            self.update_interval = config.get('update_interval', 24 * 60 * 60)  # Default to 24 hours
