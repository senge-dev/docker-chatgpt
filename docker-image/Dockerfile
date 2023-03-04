FROM python:slim

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install flask openai 

COPY . .

EXPOSE 5000

CMD ["python", "chatgpt.py"]
