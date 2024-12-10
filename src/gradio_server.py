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
hacker_news_client = HackerNewsClient()
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


def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径
    return report, report_file_path  # 返回报告内容和报告文件路径

# 定义一个函数，用于刷新订阅的GitHub项目
def refresh_subscription_list(subscription_list):
    repo = gr.update(**({"choices": subscription_list}))  # 更新订阅列表
    return repo

# 定义一个函数，用于刷新report_generator_app的下拉菜单
def refresh_list(repo):
    subscription_list = subscription_manager.list_subscriptions()  # 获取订阅列表
    repo=refresh_subscription_list(subscription_list)  # 更新订阅列表
    return repo

# 创建一个用于生成GitHub项目报告的Gradio界面
with gr.Blocks(title="GitHubSentinel") as report_generator_app:
    gr.Markdown(
        """
        # GitHubSentinel报告生成器
        ## 请选择订阅的GitHub项目，并选择生成报告的时间范围。
        """
    )
    with gr.Row():
        with gr.Column():
            api_name = gr.Dropdown(["ollama", "openai"], value=config.llm_model_type, label="API类型")
            switch_api_button = gr.Button("切换")
            switch_api_button.click(fn=switch_api, inputs=api_name, outputs=[])  # 点击按钮切换到API
            report_name = gr.Dropdown(
                subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
            )  # 下拉菜单选择订阅的GitHub项目
            refresh_button = gr.Button("刷新下拉菜单")  # 刷新按钮刷新下拉菜单
            refresh_button.click(refresh_list, inputs=report_name,outputs=report_name)
            report_days = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期",
                                    info="生成项目过去一段时间进展，单位：天")  # 滑动条选择报告的时间范围
        with gr.Column():
            generator_button = gr.Button("生成报告")  # 生成报告按钮
            generator_button.click(export_progress_by_date_range, inputs=[report_name, report_days],outputs=[gr.Markdown(), gr.File(label="下载报告")],)

# 定义一个函数，用于移除订阅的GitHub项目
def remove_subscription(removed_repo):
    result=subscription_manager.remove_subscription(removed_repo)  # 移除订阅
    subscription_list = subscription_manager.list_subscriptions()  # 获取订阅列表
    repo = refresh_subscription_list( subscription_list)  # 更新订阅列表
    return result, repo  # 返回订阅列表

# 定义一个函数，用于添加订阅的GitHub项目
def add_subscription(added_repo):
    url = f"https://api.github.com/repos/{added_repo}"  # 构造GitHub API地址
    response = requests.get(url)
    if response.status_code == 200: # 仓库存在
        result=subscription_manager.add_subscription(added_repo)  # 添加订阅
        subscription_list = subscription_manager.list_subscriptions()  # 获取订阅列表
        repo = refresh_subscription_list(subscription_list)  # 更新订阅列表
        return result, repo # 返回订阅列表
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
    with gr.Row():
        with gr.Column(): # 移除订阅
            remove_name=gr.Dropdown(subscription_manager.list_subscriptions(), label="移除订阅", info="移除已订阅GitHub项目"),  # 下拉菜单选择订阅的GitHub项目
            remove_result=gr.Textbox(label="操作结果"),  # 显示订阅列表
            gr.Button("移除订阅").click(fn=remove_subscription,inputs=remove_name,outputs=[remove_result[0],remove_name[0]]),
            # 传多个值：https://blog.csdn.net/weixin_45729192/article/details/139442890
            # 下拉菜单实时更新：https://blog.csdn.net/qq_41413211/article/details/131332555
        with gr.Column(): # 添加订阅
            add_name=gr.Textbox(label="添加订阅", info="添加订阅时，请按照格式输入：owner/repo"),  # 输入框输入GitHub项目名称
            add_result=gr.Textbox(label="操作结果"),  # 显示订阅列表
            gr.Button("添加订阅").click(fn=add_subscription,inputs=add_name,outputs=[add_result[0],remove_name[0]])

app = gr.mount_gradio_app(app, report_generator_app, path="/report_generator_app")
app = gr.mount_gradio_app(app, subscription_management_app, path="/subscription_management_app",auth=("Admin", "1234567"))
app = gr.mount_gradio_app(app, hacker_news_app, path="/hacker_news_app")

if __name__ == "__main__":
    # 启动FastAPI服务
    #uvicorn.run(app, port=8000)

    # gradio启动方式
    # report_generator_app.launch()
    # subscription_management_app.launch(auth=("Admin", "1234567"))
    hacker_news_app.launch()

