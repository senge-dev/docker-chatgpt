from flask import Flask, request                # Flask API，用于接收客户端的请求
import openai                                   # OpenAI API，用于调用OpenAI，实现题目的回答


app = Flask(__name__)


@app.route('/', methods=['POST'])
def sort_data():
    data = request.get_json()
    # 判断data是否合法
    if type(data) != dict:
        return "Invalid type, please read the docs at https://hub.docker.com/r/sengedev/docker-chatgpt", 400
    keys = data.keys()
    if 'model' in keys:
        model = data['model']
    else:
        model = 'text-davinci-003'
    needed_keys = ['key', 'prompt']
    # 比较两个keys，如果needed_keys不是keys的子集，说明缺少字段
    if not set(needed_keys).issubset(keys):
        return "Missing data, please read the docs at https://hub.docker.com/r/sengedev/docker-chatgpt", 400
    try:
        response = openai.Completion.create(
            model=model,
            prompt=data['prompt'],
            temperature=0.9,
            max_tokens=300,
            top_p=1,
            api_key=data['key'],
            frequency_penalty=0.0,
            presence_penalty=0.6,
            timeout=30
        )
    except Exception as e:
        return f'ChatGPT Error, the error code: {e}, please read the docs at https://hub.docker.com/r/sengedev/docker-chatgpt', 400
    # 解析输出结果（一般不会报错，但是为了保证程序的健壮性，此处仍然做了异常处理）
    try:
        result = response['choices'][0]['text']
    except KeyError:
        return 'Cannot resolve the answer of ChatGPT, please check your api key, for more info, please read the docs at https://hub.docker.com/r/sengedev/docker-chatgpt', 401
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
