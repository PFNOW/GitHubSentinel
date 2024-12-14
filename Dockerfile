# Dockerfile

# 使用官方的 Python 基础镜像
FROM python:3.12-slim

# 创建 app 目录
RUN mkdir /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目的所有文件到容器
ADD ./ /app

# 设置工作目录
WORKDIR app/src
EXPOSE 8000

# 复制并执行 validate_tests.sh 脚本
COPY ./validate_tests.sh /app
RUN ls -la /app/validate_tests.sh
RUN chmod +x /app/validate_tests.sh
RUN /app/validate_tests.sh


# 设置容器入口
#CMD ["python", "gradio_server.py"]
CMD ["python", "gradio_server.py", "--host", "0.0.0.0", "--port", "8000"]
