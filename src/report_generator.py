# src/report_generator.py

import os
from datetime import date, timedelta
from logger import LOG  # 导入日志模块，用于记录日志信息

class ReportGenerator:
    def __init__(self, llm):
        self.llm = llm  # 初始化时接受一个LLM实例，用于后续生成报告

    def generate_daily_report(self, markdown_file_path, report_type="github"):
        # 读取 github 项目进展文件并调用 LLM 生成日报
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        report = self.llm.generate_report(report_type, markdown_content)  # 调用LLM生成报告

        report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)  # 写入生成的报告

        LOG.info(f"GitHub 项目报告已保存到 {report_file_path}")

        return report, report_file_path


    def generate_report_by_date_range(self, markdown_file_path, days):
        # 生成特定日期范围的报告，流程与日报生成类似
        with open(markdown_file_path, 'r',encoding='utf-8') as file:
            markdown_content = file.read()

        report = self.llm.generate_daily_report(markdown_content)

        report_file_path = os.path.splitext(markdown_file_path)[0] + f"_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)

        LOG.info(f"GitHub 项目报告已保存到 {report_file_path}")

        return report, report_file_path


    def generate_hacker_news_report(self, markdown_file_path):
        # 使用LLM生成hacker news的报告
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()

        with open("prompts/hacker_news_prompt.txt", "r", encoding='utf-8') as file:
            self.llm.system_prompt = file.read()

        report = self.llm.generate_daily_report(markdown_content)  # 调用LLM生成报告

        report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)  # 写入生成的报告

        LOG.info(f"Hacker News 项目报告已保存到 {report_file_path}")

        return report, report_file_path

