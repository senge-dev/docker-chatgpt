#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openai
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os


class ChatGPTError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


locales = {
    "en_US": {
        "request_too_often": "Your request is too frequent, the limit is %s per hour, %s per minute, %s per second",
        "access_denied": "Access denied, you do not have access to this website.",
        "server_error": "Server internal error!",
        "server_error_with_err_code": "Server internal error! Error code: %s",
        "parameter_error": "Request parameter error!",
        "unauthorized": "Unauthorized access, please check your OpenAI API Key.",
        "access_successful": "Access successful."
    },
    "zh_CN": {
        "request_too_often": "您的请求过于频繁，限制为每小时%s次，每分钟%s次，每秒%s次",
        "access_denied": "访问被拒绝，您没有此网站的访问权限。",
        "server_error": "服务器内部错误！",
        "server_error_with_err_code": "服务器内部错误！错误代码：%s",
        "parameter_error": "请求参数错误！",
        "unauthorized": "未授权访问，请检查您的OpenAI API Key。",
        "access_successful": "请求成功"
    },
    "zh_TW": {
        "request_too_often": "您的請求過於頻繁，限制為每小時%s次，每分鐘%s次，每秒%s次",
        "access_denied": "訪問被拒絕，您沒有此網站的訪問權限。",
        "server_error": "服務器內部錯誤！",
        "server_error_with_err_code": "服務器內部錯誤！錯誤代碼：%s",
        "parameter_error": "請求參數錯誤！",
        "unauthorized": "未授權訪問，請檢查您的OpenAI API Key。",
        "access_successful": "請求成功"
    },
    "ru_RU": {
        "request_too_often": "Ваш запрос слишком часто, лимит %s в час, %s в минуту, %s в секунду",
        "access_denied": "Доступ запрещен, у вас нет доступа к этому сайту.",
        "server_error": "Внутренняя ошибка сервера!",
        "server_error_with_err_code": "Внутренняя ошибка сервера! Код ошибки: %s",
        "parameter_error": "Ошибка параметра запроса!",
        "unauthorized": "Неавторизованный доступ, пожалуйста, проверьте свой ключ API OpenAI.",
        "access_successful": "Доступ успешный."
    }
}


api_limiter = []    # 调用次数限制
hour = os.environ.get('HOUR_LIMIT')     # 限制每小时调用次数
minute = os.environ.get('MINUTE_LIMIT')     # 限制每分钟调用次数
second = os.environ.get('SECOND_LIMIT')     # 限制每秒调用次数
api_route = os.environ.get('ROUTE')     # API路由
sys_api = os.environ.get('API_KEY')     # API Key
language = os.environ.get('LANG')   # 语言
if api_route is None:
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
# 语言处理
if language is None:
    language = 'en_US'  # 默认语言为英文
if language.startswith('en'):
    language = 'en_US'
if language.startswith('zh') and language != 'zh_CN' and language != 'zh':
    language = 'zh_TW'  # 繁体中文
if language == 'zh_CN' or language == 'zh':
    language = 'zh_CN'  # 简体中文
if language.startswith('ru'):
    language = 'ru_RU'  # 俄语


app = Flask(__name__)
# 防止ASCII乱码
app.config['JSON_AS_ASCII'] = False

if api_limiter:  # 只有在Docker Compose中设置了限制时才会启用限制
    limiter = Limiter(
        get_remote_address,
        app=app,
        # 调用次数限制
        default_limits=api_limiter
    )


@app.errorhandler(429)
def ratelimit_handler():
    # 根据不同的语言返回不同的提示
    msg = locales[language]['request_too_often'] % (hour, minute, second)
    return jsonify({'code': 429, 'msg': msg}), 429


@app.route(f'/{api_route}', methods=['GET'])
def chatgpt_get():
    msg = locales[language]['access_denied']
    return jsonify({'code': 403, 'msg': msg}), 403


@app.errorhandler(403)
def denied():
    msg = locales[language]['access_denied']
    return jsonify({'code': 403, 'msg': msg}), 403


@app.errorhandler(500)
def internal_server_error(error):
    msg_with_err_code = locales[language]['server_error_with_err_code'] % error
    msg = locales[language]['server_error']
    if error is not None:
        return jsonify({'code': 500, 'msg': msg_with_err_code}), 500
    return jsonify({'code': 500, 'msg': msg}), 500


@app.errorhandler(400)
def bad_request():
    msg = locales[language]['parameter_error']
    return jsonify({'code': 400, 'msg': msg}), 400


@app.errorhandler(401)
def unauthorized(error):
    msg = locales[language]['unauthorized']
    return jsonify({'code': 401, 'msg': msg}), 401


def success(result, answer):
    # 返回连续对话结果和回答
    msg = locales[language]['access_successful']
    return jsonify({'code': 200, 'msg': msg, 'result': result, 'current_response': answer}), 200


@app.route(f'/{api_route}', methods=['POST'])
def chatgpt_post():
    # 如果请求方式为POST，则返回聊天结果
    # 获取请求参数
    request_data = request.get_json()
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
    params = request_data.keys()
    # 判断是否存在集合的包含关系
    if not set(needed_params).issubset(set(params)):
        # 返回错误信息，使用Error Handler
        return bad_request()
    # 获取参数，非必需参数使用try...except...处理异常，如果捕获到异常，则使用默认值
    user_content = request_data['user_content']
    try:
        api_key = request_data['api_key']
    except KeyError:
        # 使用系统API Key
        api_key = sys_api
    try:
        system_content = request_data['system_content']
    except KeyError:
        system_content = ''
    try:
        model = request_data['model']
    except KeyError:
        model = 'text-davinci-003'
    try:
        max_tokens = request_data['max_tokens']
    except KeyError:
        max_tokens = 64
    # 连续对话模式
    try:
        continuous_dialogue = request_data['continuous_dialogue']
    except KeyError:
        continuous_dialogue = []
    # 设置API密钥
    openai.api_key = api_key
    # print(api_key)
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
    # 对正确的返回结果进行处理
    answer = chatgpt_response.choices[0].message['content']  # 回复内容
    question = {'role': 'user', 'content': user_content}
    response = {'role': 'assistant', 'content': answer}
    print(response['content'])
    result = continuous_dialogue + [question, response]
    # 返回结果正确的结果
    return success(result, answer)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
