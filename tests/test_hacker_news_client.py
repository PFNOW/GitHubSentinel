import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from io import StringIO

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.hacker_news_client import HackerNewsClient
from src.logger import LOG  # 导入日志记录器


class TestHackerNewsClient(unittest.TestCase):
    def setUp(self):
        """
        在每个测试方法运行前执行，初始化 LLM 实例和测试数据。
        """
        self.client = HackerNewsClient()

    @patch('hacker_news_client.requests.get')
    def test_fetch_top_stories_success(self, mock_get):
        # 模拟HTTP响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <tr class="athing">
            <td class="title">
                <span class="titleline">
                    <a href="https://news.ycombinator.com/">Story 1</a>
                </span>
            </td>
        </tr>
        '''
        mock_get.return_value = mock_response

        # 调用方法并验证返回值
        top_stories = self.client.fetch_top_stories()
        self.assertEqual(len(top_stories), 1)
        self.assertEqual(top_stories[0]['title'], 'Story 1')
        self.assertEqual(top_stories[0]['link'], 'https://news.ycombinator.com/')

    @patch('hacker_news_client.requests.get')
    def test_fetch_top_stories_failure(self, mock_get):
        # 模拟HTTP请求失败
        mock_get.side_effect = Exception("Connection error")

        # 调用方法并验证返回值
        top_stories = self.client.fetch_top_stories()
        self.assertEqual(top_stories, [])


    @patch('hacker_news_client.requests.get')
    @patch('hacker_news_client.os.makedirs')
    @patch('hacker_news_client.open', new_callable=unittest.mock.mock_open)
    def test_export_top_stories(self, mock_open, mock_makedirs, mock_get):
        # 模拟HTTP响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <tr class="athing">
            <td class="title">
                <span class="titleline">
                    <a href="https://news.ycombinator.com/">Story 1</a>
                </span>
            </td>
        </tr>
        '''
        mock_get.return_value = mock_response

        # 调用方法
        file_path = self.client.export_top_stories(date="2024-09-01", hour="14")
        print(file_path)
        # 验证目录和文件创建
        expected_path = os.path.normpath('hacker_news/2024-09-01')
        actual_path = os.path.normpath(mock_makedirs.call_args[0][0])
        self.assertEqual(expected_path, actual_path)


    @patch('hacker_news_client.requests.get')
    @patch('hacker_news_client.os.makedirs')
    @patch('hacker_news_client.open', new_callable=unittest.mock.mock_open)
    def test_export_top_stories_no_stories(self, mock_open, mock_makedirs, mock_get):
        # 模拟HTTP响应为空
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response

        # 调用方法
        file_path = self.client.export_top_stories(date="2024-09-01", hour="14")

        # 验证没有创建文件
        mock_makedirs.assert_not_called()
        mock_open.assert_not_called()
        self.assertIsNone(file_path)

if __name__ == '__main__':
    unittest.main()
