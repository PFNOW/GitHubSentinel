import sys
import os
import unittest
from unittest.mock import patch, Mock, MagicMock

# 将 src 目录添加到模块搜索路径，方便导入项目中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.hacker_news_client import HackerNewsClient

class TestHackerNewsClient(unittest.TestCase):
    def setUp(self):
        """
        在每个测试方法运行前执行，初始化 LLM 实例和测试数据。
        """
        self.client = HackerNewsClient()

    @patch('hacker_news_client.requests.get')
    @patch('hacker_news_client.BeautifulSoup')
    def test_fetch_hackernews_top_stories(self, mock_bs, mock_get):
        """
        测试 fetch_hackernews_top_stories 方法是否正确爬取信息。
        """
        # 创建模拟响应
        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <table>
                    <tr class="athing">
                        <td>
                            <span class="titleline">
                                <a href="https://example.com/news1">News Title 1</a>
                            </span>
                        </td>
                    </tr>
                    <tr class="athing">
                        <td>
                            <span class="titleline">
                                <a href="https://example.com/news2">News Title 2</a>
                            </span>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        client = HackerNewsClient()
        top_stories = client.fetch_hackernews_top_stories()

        self.assertEqual(len(top_stories), 2)
        self.assertEqual(top_stories[0]['title'], 'News Title 1')
        self.assertEqual(top_stories[0]['link'], 'https://example.com/news1')
        self.assertEqual(top_stories[1]['title'], 'News Title 2')
        self.assertEqual(top_stories[1]['link'], 'https://example.com/news2')


    @patch('github_client.requests.get')
    def test_export_hackernews_stories(self, mock_get):
        # 模拟 API 响应
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.status_code = 200
        mock_get.return_value = mock_response  # 将模拟的响应赋值给 mock_get


if __name__ == '__main__':
    unittest.main()
