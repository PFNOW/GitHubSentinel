import os
from datetime import datetime
import requests
import time
from logger import LOG

class WOSClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.BASE_URL = "https://api.clarivate.com/apis/wos-starter/v1"
        self.ENDPOINT = "/documents"

    def fetch_data(self, query, limit=10, page=1):
        headers = {"X-ApiKey": self.api_key, "Accept": "application/json"}
        params = {"q": f"TS=({query})", "limit": limit, "page": page}
        try:
            response = requests.get(f"{self.BASE_URL}{self.ENDPOINT}", headers=headers, params=params)
            if response.status_code == 429:  # Rate limit exceeded
                LOG.warning("Rate limit exceeded. Retrying after 60 seconds...")
                time.sleep(60)
                response = requests.get(f"{self.BASE_URL}{self.ENDPOINT}", headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            LOG.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            LOG.error(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            LOG.error(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            LOG.error(f"An error occurred: {req_err}")
        return None

    def export_articles(self, query, limit=10, page=1):
        articles=self.fetch_data(query,limit,page)
        content = str(articles)
        if not articles:
            LOG.warning("未找到任何文章。")
            return None

        # 如果未提供 date 和 hour 参数，使用当前日期和时间
        date = datetime.now().strftime('%Y-%m-%d')
        hour = datetime.now().strftime('%H-%M-%S')

        # 构建存储路径
        dir_path = os.path.join('WOS', date)
        os.makedirs(dir_path, exist_ok=True)  # 验证存储目录
        file_path = os.path.join(dir_path, f'{hour}.md')  # 定义文件路径
        LOG.info(f"正在保存 Web of Science 文献到：{file_path}")
        with open(file_path, mode="w", encoding="utf-8") as file:
            file.write(content)

        LOG.info(f"Web of Science 文献保存在：{file_path}")
        return dir_path