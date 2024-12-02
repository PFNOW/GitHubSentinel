import json
import os
class Config:
    def __init__(self):
        self.email = None
        self.update_interval = None
        self.subscriptions_file = None
        self.notification_settings = None
        self.openai_token=os.getenv("OPENAI_TOKEN")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.openai_url=os.getenv("OPENAI_URL")

        self.load_config()
    
    def load_config(self):
        with open('config.json', 'r') as f:
            config = json.load(f)

            # 如果环境变量中没有GitHub Token，则从配置文件中读取
            if not self.github_token:
                self.github_token = config.get('github_token')

            self.notification_settings = config.get('notification_settings')

            # 初始化电子邮件设置
            self.email = config.get('email', {})
            # 使用环境变量或配置文件中的电子邮件密码
            self.email['password'] = os.getenv('EMAIL_PASSWORD', self.email.get('password', ''))

            self.subscriptions_file = config.get('subscriptions_file')
            # 默认每天执行
            self.freq_days = config.get('github_progress_frequency_days', 1)
            # 默认早上8点更新 (操作系统默认时区是 UTC +0，08点刚好对应北京时间凌晨12点)
            self.exec_time = config.get('github_progress_execution_time', "08:00")
