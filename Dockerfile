FROM python:3.10

# 设置工作目录
WORKDIR /app

# 先复制 requirements.txt 单独安装依赖，利用 Docker 缓存
# COPY requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到容器
COPY . /app

# 安装依赖
RUN pip install -r requirements.txt

# 运行 Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
