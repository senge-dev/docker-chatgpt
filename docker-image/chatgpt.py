#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openai  # OpenAI API，用于调用OpenAI，实现题目的回答
import os
from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


api_limiter = []
chatgpt_api_key = os.environ.get('API_KEY')
hour = os.environ.get('HOUR_LIMIT')
minute = os.environ.get('MINUTE_LIMIT')
second = os.environ.get('SECOND_LIMIT')
route = os.environ.get('ROUTE')
if route == 'null':
    route = ''
if not (hour is None or hour == '0'):
    api_limiter.append(f"{hour} per hour")
if not (minute is None or minute == '0'):
    api_limiter.append(f"{minute} per minute")
if not (second is None or second == '0'):
    api_limiter.append(f"{second} per second")


app = Flask(__name__)


if api_limiter:     # 只有在Docker Compose中设置了限制时才会启用限制
    limiter = Limiter(
        get_remote_address,
        app=app,
        # 调用次数限制
        default_limits=api_limiter
    )


# 如果调用次数超出限制，则返回错误信息，返回值为429
@app.errorhandler(429)
def ratelimit_handler(e):
    result = {
        'status': 'failed',
        'code': 429,
        'data': {
            'response': '请求次数超出限制，请稍后再试'
        }
    }
    return result, 429


@app.route(f'/{route}', methods=['GET'])
def sort_data():
    # 获取请求头
    try:
        chatgpt_api = request.headers.get('Api-Key')
    except Exception:
        if chatgpt_api_key == 'YourOpenAIApiKey':
            result = {
                'status': 'failed',
                'code': 400,
                'data': {
                    'response': '未提供合法的API Key，请阅读 https://senge.dev/index.php/docker-chatgpt'
                }
            }
            return result, 400
        else:
            chatgpt_api = chatgpt_api_key
    try:
        chatgpt_model = request.headers.get('Model')
    except Exception:
        chatgpt_model = 'text-davinci-003'
    supported_model = ['gpt-3.5-turbo', 'gpt-3.5-turbo-0301', 'text-davinci-003', 'text-davinci-002']
    if chatgpt_model not in supported_model:
        result = {
            'status': 'failed',
            'code': 400,
            'data': {
                'response': f'未知的模型{chatgpt_model}, 目前支持的模型有：gpt-3.5-turbo、gpt-3.5-turbo-0301、text-davinci-003和text-davinci-002'
            }
        }
        return result, 400
    # 获取请求的数据
    data = request.get_json()
    try:
        prompt = data['prompt']
    except Exception:
        result = {
            'status': 'failed',
            'code': 400,
            'data': {
                'response': '未提供prompt'
            }
        }
        return result, 400
    if prompt == '':
        result = {
            'status': 'failed',
            'code': 400,
            'data': {
                'response': 'prompt不能为空'
            }
        }
        return result, 400
    try:
        response = openai.Completion.create(
            model=chatgpt_model,
            prompt=data['prompt'],
            temperature=0.9,
            max_tokens=300,
            top_p=1,
            api_key=chatgpt_api,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            timeout=30
        )
    except Exception as e:
        if e == 'This is a chat model and not supported in the v1/completions endpoint. Did you mean to use v1/chat/completions?':
            response = 'ChatGPT请求失败，原因是您的OpenAI账户不支持gpt-3.5-turbo系列的模型，请使用text-davinci-003或text-davinci-002代替'
        else:
            response = f'ChatGPT请求失败，可能的原因是：您选择的模型已经被OpenAI移除、您的API Key无效或已被移除或封禁，请阅读OpenAI官方文档: https://platform.openai.com/docs，错误代码：{e}'
        result = {
            'status': 'failed',
            'code': 401,
            'data': {
                'response': response
            }
        }
        return result, 401
    chatgpt_response = response['choices'][0]['text']
    result = {
        'status': 'success',
        'code': 200,
        'data': {
            'response': chatgpt_response
        }
    }
    return result, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
