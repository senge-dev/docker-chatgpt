FROM python:slim

WORKDIR /app

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --upgrade pip && \
    pip install flask openai flask_limiter

COPY chatgpt.py .

EXPOSE 5000

CMD ["python", "chatgpt.py"]
