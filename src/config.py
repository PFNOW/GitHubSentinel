import json
import os

class Config:
    def __init__(self):
        self.slack_webhook_url = None
        self.report_types = None
        self.llm_model_type = None
        self.openai_model_name = None
        self.ollama_model_name = None
        self.ollama_api_url = None
        self.ollama_api_key = None
        self.exec_time = None
        self.freq_days = None
        self.email = None
        self.update_interval = None
        self.subscriptions_file = None
        self.notification_settings = None
        self.openai_token=os.getenv("OPENAI_TOKEN")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.openai_url=os.getenv("OPENAI_URL")

        # 加载配置
        self.load_config()
    
    def load_config(self):
        # 尝试从环境变量获取配置或使用 config.json 文件中的配置作为回退
        with open('../src/config.json', 'r') as f:
            config = json.load(f)
            
            # 使用环境变量或配置文件的 GitHub Token
            self.github_token = os.getenv('GITHUB_TOKEN', config.get('github_token'))

            self.notification_settings = config.get('notification_settings')

            # 初始化电子邮件设置
            self.email = config.get('email', {})
            # 使用环境变量或配置文件中的电子邮件密码
            self.email['password'] = os.getenv('EMAIL_PASSWORD', self.email.get('password', ''))

            # 加载 GitHub 相关配置
            github_config = config.get('github', {})
            self.github_token = os.getenv('GITHUB_TOKEN', github_config.get('token'))
            self.subscriptions_file = github_config.get('subscriptions_file')
            self.freq_days = github_config.get('progress_frequency_days', 1)
            self.exec_time = github_config.get('progress_execution_time', "08:00")

            # 加载 LLM 相关配置
            llm_config = config.get('llm', {})
            self.openai_token = os.getenv("OPENAI_TOKEN", llm_config.get('openai_token'))
            self.openai_url = os.getenv("OPENAI_URL", llm_config.get('openai_url'))
            self.llm_model_type = llm_config.get('model_type', 'openai')
            self.openai_model_name = llm_config.get('openai_model_name', 'gpt-4o-mini')
            self.ollama_model_name = llm_config.get('ollama_model_name', 'llama3')
            self.ollama_api_url = llm_config.get('ollama_api_url', 'http://localhost:3000/api/chat/completions')
            self.ollama_api_key = os.getenv("OLLAMA_API_KEY", llm_config.get('ollama_api_key'))

            # 加载报告类型配置
            self.report_types = config.get('report_types', ["github", "hacker_news"])  # 默认报告类型

            # 加载 Slack 配置
            slack_config = config.get('slack', {})
            self.slack_webhook_url = slack_config.get('webhook_url')
