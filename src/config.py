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

            # 如果环境变量中没有GitHub Token，则从配置文件中读取
            if not self.github_token:
                self.github_token = config.get('github_token')

            self.notification_settings = config.get('notification_settings')
            self.subscriptions_file = config.get('subscriptions_file')
            self.update_interval = config.get('update_interval', 24 * 60 * 60)  # 默认24小时
