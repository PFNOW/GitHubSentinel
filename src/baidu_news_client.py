import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from logger import LOG
class BaiduNewsClient:
    def __init__(self):
        self.url = "https://news.baidu.com/" # 百度新闻的URL

    def fetch_news(self, news_type):
        # 发送请求，获取网页内容
        response = requests.get(self.url)
        response.encoding = 'utf-8'  # 设置正确的编码格式
        news = []
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        LOG.info("获取到百度新闻的HTML内容")
        if news_type == 'hot_news':
            news = self._fetch_hot_news(soup)
        elif news_type == 'latest_news':
            news = self._fetch_latest_news(soup)
        elif news_type == 'all':
            hot_news = self._fetch_hot_news(soup)
            latest_news = self._fetch_latest_news(soup)
            news = hot_news + latest_news
        else:
            LOG.error("unknown_news_type")
            raise ValueError("unknown_news_type")
        return news

    def export_news(self, news_type):
        LOG.debug("准备导出新闻。")
        news=self.fetch_news(news_type)
        if not news:
            LOG.warning("未找到任何新闻。")
            return None

        # 如果未提供 date 和 hour 参数，使用当前日期和时间
        date = datetime.now().strftime('%Y-%m-%d')
        hour = datetime.now().strftime('%H-%M-%S')

        # 构建存储路径
        dir_path = os.path.join('baidu_news', date)
        os.makedirs(dir_path, exist_ok=True)  # 验证存储目录
        file_path = os.path.join(dir_path, f'{news_type}-{hour}.md')  # 定义文件路径
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# {news_type}-({date} {hour})\n\n")
            for idx, news in enumerate(news, start=1):
                file.write(f"{idx}. [{news['title'].strip("\n")}]({news['link']})\n")

        LOG.info(f"新闻记录生成：{file_path}")
        return dir_path


    def _fetch_hot_news(self, soup):
        # 找到新闻热点的部分
        LOG.info("获取热点新闻")
        hot_news_section = soup.find('div', class_='hotnews')
        hot_news=[]
        # 找到当前div中的所有新闻链接
        news_items = hot_news_section.find_all('a')
        for item in news_items:
            title = item.get_text()
            link = item.get('href')
            hot_news.append({'title': title, 'link': link})
        LOG.info(f"成功解析 {len(hot_news)} 条热点新闻。")
        return hot_news


    def _fetch_latest_news(self, soup):
        # 找到最新新闻的部分
        LOG.info("获取最新新闻")
        latest_news_section = soup.find_all('ul', class_='ulist focuslistnews')
        latest_news=[]
        # 获取所有热点新闻的链接和标题
        for index, section in enumerate(latest_news_section, 1):
            news_items = section.find_all('li')
            for item in news_items:
                title = item.get_text()
                link = item.find_all('a')[0].get('href')
                latest_news.append({'title': title, 'link': link})
        LOG.info(f"成功解析 {len(latest_news)} 条最新新闻。")
        return latest_news


if __name__ == '__main__':
    client = BaiduNewsClient()
    client.export_news('hot_news')
    client.export_news('latest_news')