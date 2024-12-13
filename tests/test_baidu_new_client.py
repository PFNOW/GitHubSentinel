import sys
import unittest
from unittest.mock import patch, Mock
from datetime import datetime
import os
from io import StringIO

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.baidu_news_client import BaiduNewsClient  # 假设代码保存在 baidu_news_client.py 中


class TestBaiduNewsClient(unittest.TestCase):
    def setUp(self):
        self.client = BaiduNewsClient()

    @patch('requests.get')
    def test_fetch_news_hot(self, mock_get):
        # 模拟返回的 HTTP 响应
        mock_response = Mock()
        mock_response.text = '<html><body><div class="hotnews"><a href="http://news1" >Title1</a></div></body></html>'
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response

        client = BaiduNewsClient()
        news = client.fetch_news('hot_news')

        # 测试 fetch_news 方法的行为
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['title'], 'Title1')
        self.assertEqual(news[0]['link'], 'http://news1')

    @patch('requests.get')
    def test_fetch_news_latest(self, mock_get):
        # 模拟返回的 HTTP 响应
        mock_response = Mock()
        mock_response.text = '''
            <html><body>
            <ul class="ulist focuslistnews">
                <li><a href="http://news2">Title2</a></li>
            </ul>
            </body></html>
        '''
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response

        client = BaiduNewsClient()
        news = client.fetch_news('latest_news')

        # 测试 fetch_news 方法的行为
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['title'], 'Title2')
        self.assertEqual(news[0]['link'], 'http://news2')

    @patch('requests.get')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_export_news(self, mock_open, mock_makedirs, mock_get):
        # 模拟返回的 HTTP 响应
        mock_response = Mock()
        mock_response.text = '<html><body><div class="hotnews"><a href="http://news1" >Title1</a></div></body></html>'
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response

        # 模拟 open 方法
        mock_file = mock_open.return_value
        mock_file.__enter__.return_value = mock_file  # 显式指定支持上下文管理器
        mock_file.__exit__.return_value = None

        client = BaiduNewsClient()
        result = client.export_news('hot_news')

        # 检查文件生成路径
        now = datetime.now().strftime('%H-%M-%S')
        expected_file_path = os.path.join('baidu_news', datetime.now().strftime('%Y-%m-%d'), f'{now}.md')

        # 验证路径是否正确
        mock_open.assert_called_with(expected_file_path, 'w', encoding='utf-8')
        mock_file.write.assert_called()

        # 检查是否正确返回路径
        self.assertTrue(result.endswith(f'{now}.md'))

    @patch('requests.get')
    def test_log_exception_on_fetch_news_failure(self, mock_get):
        # 模拟请求失败
        mock_get.side_effect = Exception("Network Error")

        client = BaiduNewsClient()

        with self.assertRaises(Exception):
            client.fetch_news('hot_news')


if __name__ == '__main__':
    unittest.main()
