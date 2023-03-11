FROM python:slim

WORKDIR /app
# 该镜像为本地构建，并发布到海外服务器中，由于本地构建，所以构建时使用的是大陆的镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --upgrade pip && \
    pip install flask openai>=0.27.0 flask_limiter

COPY chatgpt.py .

EXPOSE 5000

CMD ["python", "chatgpt.py"]
