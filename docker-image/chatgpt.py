#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openai
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import requests     # 检测服务器的IP所在国家是否受OpenAI支持


class ChatGPTError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


api_limiter = []    # 调用次数限制
hour = os.environ.get('HOUR_LIMIT')     # 限制每小时调用次数
minute = os.environ.get('MINUTE_LIMIT')     # 限制每分钟调用次数
second = os.environ.get('SECOND_LIMIT')     # 限制每秒调用次数
api_route = os.environ.get('ROUTE')     # API路由
sys_api = os.environ.get('API_KEY')     # API Key
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
    msg = f'请求过于频繁，请稍后再试，请求次数限制：每秒：{second}次、每分钟：{minute}次、每小时：{hour}次'
    return jsonify({'code': 429, 'msg': msg}), 429


@app.route(f'/{api_route}', methods=['GET'])
def chatgpt_get():
    # 如果请求方式为GET，则拒绝访问
    msg = '拒绝访问'
    return jsonify({'code': 403, 'msg': msg}), 403


@app.errorhandler(404)
def not_found():
    # 如果请求方式为GET，则拒绝访问
    msg = '请求错误，请检查您的请求方式'
    return jsonify({'code': 404, 'msg': msg}), 404


@app.errorhandler(500)
def internal_server_error(error):
    # 如果请求方式为GET，则拒绝访问
    msg_with_err_code = f'服务器内部错误，请联系管理员，错误代码：{error}'
    msg = '服务器内部错误，请联系管理员'
    if error is not None:
        return jsonify({'code': 500, 'msg': msg_with_err_code}), 500
    return jsonify({'code': 500, 'msg': msg}), 500


@app.errorhandler(400)
def bad_request():
    # 如果请求方式为GET，则拒绝访问
    msg = '请求参数错误'
    return jsonify({'code': 400, 'msg': msg}), 400


@app.errorhandler(401)
def unauthorized(error):
    # 如果请求方式为GET，则拒绝访问
    msg = f'未授权，请检查您的API Key，错误代码：{error}'
    return jsonify({'code': 401, 'msg': msg}), 401


def success(result, answer):
    # 返回连续对话结果和回答
    msg = '请求成功'
    return jsonify({'code': 200, 'msg': msg, 'result': result, 'answer': answer}), 200


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
    result = continuous_dialogue + [question, response]
    # 返回结果正确的结果
    success(result, answer)


if __name__ == '__main__':
    authorized_countries = {
        "AL": "阿尔巴尼亚",
        "DZ": "阿尔及利亚",
        "AD": "安道尔",
        "AO": "安哥拉",
        "AG": "安提瓜和巴布达",
        "AR": "阿根廷",
        "AM": "亚美尼亚",
        "AU": "澳大利亚",
        "AT": "奥地利",
        "AZ": "阿塞拜疆",
        "BS": "巴哈马",
        "BD": "孟加拉国",
        "BB": "巴巴多斯",
        "BE": "比利时",
        "BZ": "伯利兹",
        "BJ": "贝宁",
        "BT": "不丹",
        "BA": "波斯尼亚和黑塞哥维那",
        "BW": "博茨瓦纳",
        "BR": "巴西",
        "BG": "保加利亚",
        "BF": "布基纳法索",
        "CV": "佛得角",
        "CA": "加拿大",
        "CL": "智利",
        "CO": "哥伦比亚",
        "KM": "科摩罗",
        "CR": "哥斯达黎加",
        "HR": "克罗地亚",
        "CY": "塞浦路斯",
        "DK": "丹麦",
        "DJ": "吉布提",
        "DM": "多米尼克",
        "DO": "多米尼加共和国",
        "EC": "厄瓜多尔",
        "SV": "萨尔瓦多",
        "EE": "爱沙尼亚",
        "FJ": "斐济",
        "FI": "芬兰",
        "FR": "法国",
        "GA": "加蓬",
        "GM": "冈比亚",
        "GE": "格鲁吉亚",
        "DE": "德国",
        "GH": "加纳",
        "GR": "希腊",
        "GD": "格林纳达",
        "GT": "危地马拉",
        "GN": "几内亚",
        "GW": "几内亚比绍",
        "GY": "圭亚那",
        "HT": "海地",
        "HN": "洪都拉斯",
        "HU": "匈牙利",
        "IS": "冰岛",
        "IN": "印度",
        "ID": "印度尼西亚",
        "IQ": "伊拉克",
        "IE": "爱尔兰",
        "IL": "以色列",
        "IT": "意大利",
        "JM": "牙买加",
        'JP': '日本',
        'JO': '约旦',
        'KZ': '哈萨克斯坦',
        'KE': '肯尼亚',
        'KI': '基里巴斯',
        'KW': '科威特',
        'KG': '吉尔吉斯斯坦',
        'LV': '拉脱维亚',
        'LB': '黎巴嫩',
        'LS': '莱索托',
        'LR': '利比里亚',
        'LI': '列支敦士登',
        'LT': '立陶宛',
        'LU': '卢森堡',
        'MG': '马达加斯加',
        'MW': '马拉维',
        'MY': '马来西亚',
        'MV': '马尔代夫',
        'ML': '马里',
        'MT': '马耳他',
        'MH': '马绍尔群岛',
        'MR': '毛里塔尼亚',
        'MU': '毛里求斯',
        'MX': '墨西哥',
        'MC': '摩纳哥',
        'MN': '蒙古',
        'ME': '黑山',
        'MA': '摩洛哥',
        'MZ': '莫桑比克',
        'MM': '缅甸',
        'NA': '纳米比亚',
        'NR': '瑙鲁',
        'NP': '尼泊尔',
        'NL': '荷兰',
        'NZ': '新西兰',
        'NI': '尼加拉瓜',
        'NE': '尼日尔',
        'NG': '尼日利亚',
        'MK': '北马其顿',
        'NO': '挪威',
        'OM': '阿曼',
        'PK': '巴基斯坦',
        'PW': '帕劳',
        'PA': '巴拿马',
        'PG': '巴布亚新几内亚',
        'PE': '秘鲁',
        'PH': '菲律宾',
        'PL': '波兰',
        'PT': '葡萄牙',
        'QA': '卡塔尔',
        'RO': '罗马尼亚',
        'RW': '卢旺达',
        'KN': '圣基茨和尼维斯',
        'LC': '圣卢西亚',
        'VC': '圣文森特和格林纳丁斯',
        'WS': '萨摩亚',
        'SM': '圣马力诺',
        'ST': '圣多美和普林西比',
        'SN': '塞内加尔',
        'RS': '塞尔维亚',
        'SC': '塞舌尔',
        'SL': '塞拉利昂',
        'SG': '新加坡',
        'SK': '斯洛伐克',
        'SI': '斯洛文尼亚',
        'SB': '所罗门群岛',
        'ZA': '南非',
        'ES': '西班牙',
        'LK': '斯里兰卡',
        'SR': '苏里南',
        'SE': '瑞典',
        'CH': '瑞士',
        'TH': '泰国',
        'TG': '多哥',
        'TO': '汤加',
        'TT': '特立尼达和多巴哥',
        'TN': '突尼斯',
        'TR': '土耳其',
        'TV': '图瓦卢',
        'UG': '乌干达',
        'AE': '阿联酋',
        'US': '美国',
        'UY': '乌拉圭',
        'VU': '瓦努阿图',
        'ZM': '赞比亚',
        'BO': '玻利维亚',
        'BN': '文莱',
        'CG': '刚果（布）',
        'CZ': '捷克共和国',
        'VA': '梵蒂冈',
        'FM': '密克罗尼西亚联邦',
        'MD': '摩尔多瓦',
        'PS': '巴勒斯坦',
        'KR': '韩国',
        'TW': '中国台湾',
        'TZ': '坦桑尼亚',
        'TL': '东帝汶',
        'GB': '英国'
    }
    unauthorized_countries = {
        'RU': '俄罗斯',
        'CN': '中国大陆',
        'HK': '中国香港',
        'IR': '伊朗',
        'AF': '阿富汗',
        'SY': '叙利亚',
        'ET': '埃塞俄比亚',
        'KP': '北朝鲜',
        'SD': '苏丹',
        'TD': '乍得',
        'LY': '利比亚',
        'ZW': '津巴布韦',
        'SO': '索马里',
        'CM': '喀麦隆',
        'SZ': '在斯瓦特',
        'CF': '中非共和国',
        'CV': '佛得角',
        'BI': '布隆迪',
        'ER': '厄立特里亚',
        'UA': '乌克兰'
    }
    supported_countries_list = authorized_countries.keys()
    # 判断国家代码是否在支持的国家代码列表中
    data = requests.get('https://ipinfo.io/json').json()
    country_code = data['country']
    ip = data['ip']
    # 获取国家代码
    if country_code in supported_countries_list:
        country = authorized_countries[country_code]
        print(f"您的服务器所在国家为{country}，IP地址为：{ip}正在启动OpenAI API服务")
        # 启动服务
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        country = unauthorized_countries[country_code]
        raise ChatGPTError(msg=f"您的服务器所在国家为{country}，IP地址为：{ip}暂不支持使用OpenAI API服务")

