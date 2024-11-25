from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块

class LLM:
    def __init__(self,openai_token,openai_url):
        # 创建一个OpenAI客户端实例
        self.client = OpenAI(base_url =openai_url, api_key = openai_token)
        # 配置日志文件，当文件大小达到1MB时自动轮转，日志级别为DEBUG
        LOG.add("daily_progress/llm_logs.log", rotation="1 MB", level="DEBUG")

    def generate_daily_report(self, markdown_content, dry_run=False):
        # 构建一个用于生成报告的提示文本，要求生成的报告包含新增功能、主要改进和问题修复
        system_prompt=f"角色设定：你现在是一位优秀的程序员，能够理解GithubAPI返回内容的格式，完成总结工作。\n任务目标：总结信息，合并相似的功能和内容，形成一份简报，包含以下内容：1）新增功能；2）主要改进；3）修复问题。对于无法识别和总结的功能和内容，单独放在“其他更新”中，不做任何修改。\n规则约束：让我们说中文；让我们一步步来做；启用联网搜索功能。"
        user_prompt = f"以下是项目的最新进展:\n\n{markdown_content}"
        
        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(system_prompt)
                f.write(user_prompt)
            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("Starting report generation using GPT model.")
        
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # 指定使用的模型版本
                messages=[
                    {"role": "system", "content":system_prompt},
                    {"role": "user", "content": user_prompt}  # 提交用户角色的消息
                ]
            )
            LOG.debug("GPT response: {}", response)
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the report: {}", e)
            raise
