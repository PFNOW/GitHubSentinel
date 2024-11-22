import os # 导入os模块用于文件和目录操作
import requests # 导入requests库用于HTTP请求
from bs4 import BeautifulSoup # 使用BeautifulSoup解析网页
from datetime import datetime  # 导入日期处理模块
from logger import LOG  # 导入日志模块

class HackerNewsClient:
    def __init__(self):
        pass

    def fetch_hackernews_top_stories(self):
    # 获取 Hacker News 首页的热点新闻
        LOG.debug("准备获取Hacker News首页的热点新闻")
        url = 'https://news.ycombinator.com/'
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找包含新闻的所有 <tr> 标签
            stories = soup.find_all('tr', class_='athing')

            top_stories = []
            for story in stories:
                title_tag = story.find('span', class_='titleline').find('a')
                if title_tag:
                    title = title_tag.text
                    link = title_tag['href']
                    top_stories.append({'title': title, 'link': link})
            return top_stories
        except Exception as e:
            LOG.error(f"获取Hacker News首页的热点新闻失败: {e}")
            return None

    def export_hackernews_stories(self):
    # 导出 Hacker News 新闻内容
        LOG.debug("准备导出Hacker News新闻内容:")
        today = datetime.now().date().isoformat()  # 获取今天的日期
        stories=self.fetch_hackernews_top_stories() # 获取Hacker News首页的热点新闻

        repo_dir = os.path.join('daily_progress', 'hacker_news')  # 构建目录路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在

        # 更新文件名以包含日期范围
        date_str = f"{today}"
        file_path = os.path.join(repo_dir, f'{date_str}.md')  # 构建文件路径
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# Daily Progress for Hacker News ({today})\n\n")
            for id, story  in enumerate(stories, start=1):  # 写入每条新闻
                file.write(f"{id}. {story['title']}  Link: {story['link']}\n")

        LOG.info(f"Hacker News 报告生成： {file_path}")  # 记录日志
        return file_path

if __name__ == "__main__":
    stories = HackerNewsClient().export_hackernews_stories()
    if stories:
        print(f"Stories exported to {stories}")
    else:
        print("No stories found.")