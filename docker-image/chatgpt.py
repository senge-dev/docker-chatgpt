#!/usr/bin/env python
# -*- coding: utf-8 -*-


import openai
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os


api_limiter = []
hour = os.environ.get('HOUR_LIMIT')
minute = os.environ.get('MINUTE_LIMIT')
second = os.environ.get('SECOND_LIMIT')
api_route = os.environ.get('ROUTE')
sys_api = os.environ.get('API_KEY')
save_logs = os.environ.get('SAVE_LOGS')
if api_route == 'null' or api_route is None:
    api_route = ''
if not (hour is None or hour == '0' or not hour.isdigit()):
    if int(hour) > 0:
        api_limiter.append(f"{hour} per hour")
if not (minute is None or minute == '0' or not minute.isdigit()):
    if int(minute) > 0:
        api_limiter.append(f"{minute} per minute")
if not (second is None or second == '0' or not second.isdigit()):
    if int(second) > 0:
        api_limiter.append(f"{second} per second")


app = Flask(__name__)
# 防止ASCII乱码
app.config['JSON_AS_ASCII'] = False


if api_limiter:     # 只有在Docker Compose中设置了限制时才会启用限制
    limiter = Limiter(
        get_remote_address,
        app=app,
        # 调用次数限制
        default_limits=api_limiter
    )


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'code': 429, 'msg': f'请求过于频繁，请稍后再试，请求次数限制：每秒：{second}次、每分钟：{minute}次、每小时：{hour}次'}), 429


@app.route(f'/{api_route}', methods=['GET'])
def chatgpt_get():
    # 如果请求方式为GET，则拒绝访问
    return jsonify({'code': 403, 'msg': '拒绝访问'}), 403


@app.errorhandler(404)
def not_found():
    # 如果请求方式为GET，则拒绝访问
    return jsonify({'code': 404, 'msg': '请求错误'}), 404


@app.errorhandler(500)
def internal_server_error(error):
    # 如果请求方式为GET，则拒绝访问
    if error is not None:
        return jsonify({'code': 500, 'msg': f'服务器内部错误，请联系管理员，错误代码：{error}'}), 500
    return jsonify({'code': 500, 'msg': f'服务器内部错误，请联系管理员'}), 500


@app.errorhandler(400)
def bad_request():
    # 如果请求方式为GET，则拒绝访问
    return jsonify({'code': 400, 'msg': '请求参数错误'}), 400


@app.errorhandler(401)
def unauthorized(error):
    # 如果请求方式为GET，则拒绝访问
    return jsonify({'code': 401, 'msg': f'未授权，请检查您的API Key，错误代码：{error}'}), 401


@app.route(f'/{api_route}', methods=['POST'])
def chatgpt_post():
    # 如果请求方式为POST，则返回聊天结果
    # 获取请求参数
    data = request.get_json()
    # 获取请求参数中的内容，需要的参数有（带*的为必填项）：
    # system_content: 系统的回复内容，给ChatGPT的限制或提示
    # *user_content: 用户的回复内容，用户对ChatGPT的输入内容
    # model: 模型名称，
    # *api_key: API密钥
    # max_tokens: 最大生成的token数量
    # continuous_dialogue: 连续对话模式，如果为空，则使用默认值，否则进行连续对话
    needed_params = ['user_content']
    # 判断sys_api是否为空，如果非空，则不进行API Key的检查
    if sys_api is None or sys_api == '':
        needed_params.append('api_key')
    params = data.keys()
    # 判断是否存在集合的包含关系
    if not set(needed_params).issubset(set(params)):
        # 返回错误信息，使用Error Handler
        return bad_request()
    # 获取参数，非必需参数使用try...except...处理异常，如果捕获到异常，则使用默认值
    user_content = data['user_content']
    try:
        api_key = data['api_key']
    except KeyError:
        # 使用系统API Key
        api_key = sys_api
    try:
        system_content = data['system_content']
    except KeyError:
        system_content = ''
    try:
        model = data['model']
    except KeyError:
        model = 'text-davinci-003'
    try:
        max_tokens = data['max_tokens']
    except KeyError:
        max_tokens = 64
    # 连续对话模式
    try:
        continuous_dialogue = data['continuous_dialogue']
    except KeyError:
        continuous_dialogue = []
    # 设置API密钥
    openai.api_key = api_key
    # 拼接参数
    messages = [{"role": "system", "content": system_content}, {"role": "user", "content": user_content}]
    # 判断连续对话参数内是否有system，如果没有，则添加，如果有，则将system的内容替换为当前的system内容
    if len(continuous_dialogue) == 0:
        continuous_dialogue.append({"role": "system", "content": system_content})
    # 连接参数
    prompts = continuous_dialogue + messages
    # 调用API
    try:
        chatgpt_response = openai.ChatCompletion.create(
            model=model,
            messages=prompts,
            max_tokens=max_tokens
        )
    except openai.error.AuthenticationError as e:
        # 返回错误信息，使用Error Handler
        return unauthorized(e)
    except Exception as e:
        # 返回错误信息，使用Error Handler
        return internal_server_error(e)
    # 返回结果
    answer = chatgpt_response.choices[0].message['content'] # 回复内容
    question = {'role': 'user', 'content': user_content}
    response = {'role': 'assistant', 'content': answer}
    result = continuous_dialogue + [question, response]
    return jsonify({'code': 200, 'msg': '请求成功', 'result': result, 'current_response': answer}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
