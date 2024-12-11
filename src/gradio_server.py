import gradio as gr  # 导入gradio库用于创建GUI
import requests
import uvicorn
from fastapi import FastAPI  # 导入FastAPI库用于创建多个gradio接口
from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from hacker_news_client import HackerNewsClient  # 导入爬取Hacker News的包
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
hacker_news_client = HackerNewsClient() # 创建 Hacker News 客户端实例
llm = LLM(config)  # 创建语言模型实例
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)
app = FastAPI()# 定义FastAPI应用
@app.get("/")
def read_main():
    return {"message":
    """
    This is your main app. You can access the report generator app at http://localhost:8000/report_generator_app , access the subscription management app at http://localhost:8000/subscription_management_app , and access the hacker news app at http://localhost:8000/hacker_news_app 
    """}

# 定义一个用于生成hacker news报告的Gradio界面
def generate_hacker_news():
# 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    markdown_file_path = hacker_news_client.export_hackernews_stories()  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_daily_report(markdown_file_path, "hacker_news") # 生成并获取报告内容及文件路径
    return report, report_file_path  # 返回报告内容和报告文件路径

# 切换API类型
def switch_api(api_name):
    print(f"Switching to {api_name} API")
    report_generator.switch_api(api_name)  # 切换API类型

# 创建Hacker news的Gradio界面
with gr.Blocks(title="hacker news") as hacker_news_app:
    gr.Markdown(
        """
        # Hacker news报告生成器
        """
    )
    with gr.Row():
        with gr.Column():
            api_name = gr.Dropdown(["ollama", "openai"], value=config.llm_model_type,label="API类型")
            switch_api_button = gr.Button("切换")
            switch_api_button.click(fn=switch_api, inputs=api_name, outputs=[])  # 点击按钮切换到API
        with gr.Column():
            generator_button = gr.Button("生成报告")  # 生成报告按钮
            generator_button.click(generate_hacker_news, inputs=[],
                                   outputs=[gr.Markdown(), gr.File(label="下载报告")], )


def generate_github_report(model_type, model_name, repo, days):
    config.llm_model_type = model_type

    if model_type == "openai":
        config.openai_model_name = model_name
    else:
        config.ollama_model_name = model_name

    llm = LLM(config)  # 创建语言模型实例
    report_generator = ReportGenerator(llm, config.report_types)  # 创建报告生成器实例

    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_github_report(raw_file_path)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def generate_hn_hour_topic(model_type, model_name):
    config.llm_model_type = model_type

    if model_type == "openai":
        config.openai_model_name = model_name
    else:
        config.ollama_model_name = model_name

    llm = LLM(config)  # 创建语言模型实例
    report_generator = ReportGenerator(llm, config.report_types)  # 创建报告生成器实例

    markdown_file_path = hacker_news_client.export_top_stories()
    report, report_file_path = report_generator.generate_hn_topic_report(markdown_file_path)

    return report, report_file_path  # 返回报告内容和报告文件路径


# 定义一个回调函数，用于根据 Radio 组件的选择返回不同的 Dropdown 选项
def update_model_list(model_type):
    if model_type == "openai":
        return gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], label="选择模型")
    elif model_type == "ollama":
        return gr.Dropdown(choices=["llama3.1", "gemma2:2b", "qwen2:7b"], label="选择模型")


# 创建 Gradio 界面
with gr.Blocks(title="GitHubSentinel") as demo:
    # 创建 GitHub 项目进展 Tab
    with gr.Tab("GitHub 项目进展"):
        gr.Markdown("## GitHub 项目进展")  # 添加小标题

        # 创建 Radio 组件
        model_type = gr.Radio(["openai", "ollama"], label="模型类型", info="使用 OpenAI GPT API 或 Ollama 私有化模型服务")

        # 创建 Dropdown 组件
        model_name = gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], label="选择模型")

        # 创建订阅列表的 Dropdown 组件
        subscription_list = gr.Dropdown(subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目")

        # 创建 Slider 组件
        days = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天")

        # 使用 radio 组件的值来更新 dropdown 组件的选项
        model_type.change(fn=update_model_list, inputs=model_type, outputs=model_name)

        # 创建按钮来生成报告
        button = gr.Button("生成报告")

        # 设置输出组件
        markdown_output = gr.Markdown()
        file_output = gr.File(label="下载报告")

        # 将按钮点击事件与导出函数绑定
        button.click(generate_github_report, inputs=[model_type, model_name, subscription_list, days], outputs=[markdown_output, file_output])

    # 创建 Hacker News 热点话题 Tab
    with gr.Tab("Hacker News 热点话题"):
        gr.Markdown("## Hacker News 热点话题")  # 添加小标题

        # 创建 Radio 组件
        model_type = gr.Radio(["openai", "ollama"], label="模型类型", info="使用 OpenAI GPT API 或 Ollama 私有化模型服务")

        # 创建 Dropdown 组件
        model_name = gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], label="选择模型")

        # 使用 radio 组件的值来更新 dropdown 组件的选项
        model_type.change(fn=update_model_list, inputs=model_type, outputs=model_name)

        # 创建按钮来生成报告
        button = gr.Button("生成最新热点话题")

        # 设置输出组件
        markdown_output = gr.Markdown()
        file_output = gr.File(label="下载报告")

        # 将按钮点击事件与导出函数绑定
        button.click(generate_hn_hour_topic, inputs=[model_type, model_name,], outputs=[markdown_output, file_output])



if __name__ == "__main__":
    # 启动FastAPI服务
    #uvicorn.run(app, port=8000)

    # gradio启动方式
    # report_generator_app.launch()
    # subscription_management_app.launch(auth=("Admin", "1234567"))
    hacker_news_app.launch()

