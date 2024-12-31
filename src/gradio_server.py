import gradio as gr  # 导入gradio库用于创建GUI
import requests
from fastapi import FastAPI
import uvicorn
from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from hacker_news_client import HackerNewsClient  # 导入爬取Hacker News的包
from baidu_news_client import BaiduNewsClient  # 导入爬取百度新闻的包
from  WOS_client import WOSClient  # 导入爬取Web of Science的包
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
hacker_news_client = HackerNewsClient() # 创建 Hacker News 客户端实例
baidu_news_client = BaiduNewsClient() # 创建百度新闻客户端实例
wos_client = WOSClient(config.wos_api_key)  # 创建Web of Science客户端实例
subscription_manager = SubscriptionManager(config.subscriptions_file)

# 定义一个函数，用于刷新订阅的GitHub项目
def refresh_subscription_list(repo):
    subscription_list = subscription_manager.list_subscriptions()  # 获取订阅列表
    repo = gr.update(**({"choices": subscription_list}))  # 更新订阅列表
    return repo

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
        return gr.Dropdown(choices=["llamafamily/llama3-chinese-8b-instruct:latest", "opencoder:1.5b"], label="选择模型")

def generate_baidu_news_report(model_type, model_name, news_type):
    config.llm_model_type = model_type
    if model_type == "openai":
        config.openai_model_name = model_name
    else:
        config.ollama_model_name = model_name
    if news_type == "全部":
        news_type = "all"
    elif news_type == "热门新闻":
        news_type = "hot_news"
    elif news_type == "最新新闻":
        news_type = "latest_news"
    llm = LLM(config)  # 创建语言模型实例
    report_generator = ReportGenerator(llm, config.report_types)
    markdown_dir_path = baidu_news_client.export_news(news_type)
    report, report_file_path = report_generator.generate_baidu_news_report(markdown_dir_path)
    return report, report_file_path  # 返回报告内容和报告文件路径

def generate_wos_report(model_type, model_name, query, page, limit):
    config.llm_model_type = model_type
    if model_type == "openai":
        config.openai_model_name = model_name
    else:
        config.ollama_model_name = model_name
    llm = LLM(config)  # 创建语言模型实例
    report_generator = ReportGenerator(llm, config.report_types)
    markdown_file_path = wos_client.export_articles(query, limit, page)
    report, report_file_path = report_generator.generate_wos_report(markdown_file_path)
    return report, report_file_path


# 创建 Gradio 界面
with gr.Blocks(title="GitHubSentinel") as report_generator_app:
    with gr.Tab("Web of Science文献获取"):
        gr.Markdown("# Web of Science文献获取")
        model_type = gr.Radio(["openai", "ollama"], label="模型类型", info="使用 OpenAI GPT API 或 Ollama 私有化模型服务")
        model_name = gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], label="选择模型")
        model_type.change(fn=update_model_list, inputs=model_type, outputs=model_name)
        query = gr.Textbox(label="输入查询关键词", placeholder="输入查询关键词", info="输入查询关键词，多个关键词请用空格分隔")
        page = gr.Number(value=1, label="页码", minimum=1, maximum=5, step=1, info="查询页码，最大5")
        limit = gr.Slider(value=10, label="每页数量", minimum=1, maximum=50, step=1, info="查询数量，最大50")
        button = gr.Button("获取文献列表")
        markdown_output = gr.Markdown()
        file_output = gr.File(label="下载整理好的文献列表")
        button.click(generate_wos_report, inputs=[model_type, model_name, query, page, limit], outputs=[markdown_output, file_output])

    with gr.Tab("百度新闻获取"):
        gr.Markdown("# 新闻获取")
        model_type = gr.Radio(["openai", "ollama"], label="模型类型", info="使用 OpenAI GPT API 或 Ollama 私有化模型服务")
        model_name = gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], label="选择模型")
        model_type.change(fn=update_model_list, inputs=model_type, outputs=model_name)
        news_type = gr.Radio(choices=["全部", "热门新闻", "最新新闻"], value="全部", label="新闻类型", info="获取最新新闻还是热门新闻")
        button = gr.Button("生成报告")
        markdown_output = gr.Markdown()
        file_output = gr.File(label="下载报告")
        button.click(generate_baidu_news_report, inputs=[model_type, model_name, news_type], outputs=[markdown_output, file_output])
    # 创建 GitHub 项目进展 Tab
    with gr.Tab("GitHub 项目进展"):
        gr.Markdown("# GitHub 项目进展")  # 添加小标题
        gr.Markdown("## [订阅管理页面](/subscription_management_app)")  # 添加小标题
        # 创建 Radio 组件
        model_type = gr.Radio(["openai", "ollama"], label="模型类型", info="使用 OpenAI GPT API 或 Ollama 私有化模型服务")
        # 创建 Dropdown 组件
        model_name = gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], label="选择模型")
        # 创建订阅列表的 Dropdown 组件
        subscription_list = gr.Dropdown(subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目")
        report_generator_app.load(fn=refresh_subscription_list, inputs=subscription_list, outputs=subscription_list)  # 刷新订阅列表
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


# 定义一个函数，用于移除订阅的GitHub项目
def remove_subscription(removed_repo):
    result=subscription_manager.remove_subscription(removed_repo)  # 移除订阅
    subscription_list = subscription_manager.list_subscriptions()  # 获取订阅列表
    removed_repo = gr.update(**({"choices": subscription_list}))  # 更新订阅列表
    print(subscription_manager.subscriptions)
    return result, removed_repo # 返回订阅列表

# 定义一个函数，用于添加订阅的GitHub项目
def add_subscription(added_repo):
    url = f"https://api.github.com/repos/{added_repo}"  # 构造GitHub API地址
    response = requests.get(url)
    if response.status_code == 200: # 仓库存在
        result=subscription_manager.add_subscription(added_repo)  # 添加订阅
        subscription_list = subscription_manager.list_subscriptions()  # 获取订阅列表
        removed_repo = gr.update(**({"choices": subscription_list}))  # 更新订阅列表
        return result, removed_repo # 返回订阅列表
    else:
        return "仓库不存在", added_repo  # 返回订阅列表

# 创建管理界面
with gr.Blocks (title="GitHubSentinel管理界面") as subscription_management_app: # 设置界面标题
    gr.Markdown(
        """
        # GitHubSentinel管理界面
        ## 管理订阅的GitHub项目，请慎重操作。
        """
    )
    gr.Markdown("## [报告生成页面](/report_generator_app)")  # 添加小标题
    with gr.Row():
        with gr.Column(): # 移除订阅
            remove_name=gr.Dropdown(subscription_manager.list_subscriptions(), label="移除订阅", info="移除已订阅GitHub项目")  # 下拉菜单选择订阅的GitHub项目
            subscription_management_app.load(fn=refresh_subscription_list, inputs=remove_name, outputs=remove_name)  # 刷新订阅列表
            remove_result=gr.Textbox(label="操作结果"),  # 显示订阅列表
            gr.Button("移除订阅").click(fn=remove_subscription,inputs=remove_name, outputs=[remove_result[0], remove_name])
            # 传多个值：https://blog.csdn.net/weixin_45729192/article/details/139442890
            # 下拉菜单实时更新：https://blog.csdn.net/qq_41413211/article/details/131332555
        with gr.Column(): # 添加订阅
            add_name=gr.Textbox(label="添加订阅", info="添加订阅时，请按照格式输入：owner/repo")  # 输入框输入GitHub项目名称
            add_result=gr.Textbox(label="操作结果"),  # 显示订阅列表
            gr.Button("添加订阅").click(fn=add_subscription, inputs=add_name, outputs=[add_result[0], remove_name])

app = FastAPI()
@app.get("/")
def read_main():
    return {"message": "This is the main page of GitHubSentinel. You can access the report generator app at localhost:8000/report_generator_app and the subscription management app at localhost:8000/subscription_management_app  "}
app = gr.mount_gradio_app(app, subscription_management_app, path="/subscription_management_app", auth=("Admin", "1234567"))
app = gr.mount_gradio_app(app, report_generator_app, path="/report_generator_app")

if __name__ == "__main__":
    # 启动FastAPI服务
    uvicorn.run(app, port=8000)

    # gradio启动方式
    # demo.launch()
    # subscription_management_app.launch(auth=("Admin", "1234567"))

