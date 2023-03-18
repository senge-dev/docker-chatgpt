import requests
import json

# ChatGPT API Demo（连续对话模式）
url = "https://chatgpt.example.com/api"
sys_prompt = input("sys> ")

continuous_dialogue = [{"role": "system", "content": sys_prompt}]
while True:
    user_input = input("user> ")
    if user_input.lower() in ['exit', 'quit']:
        break
    data = {
        "system_content": sys_prompt,
        "user_content": user_input,
        "model": "gpt-3.5-turbo",
        "api_key": "sk-U3y83c7o8nOn8i4ONnoT5uA9B6Yd75xrl9BIKihk4vCmCMzi",  # 该API为 fake API Key，请换成自己的API Key
        "continuous": [],
        "max_tokens": 100
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        print(response.text)
        continue
    else:
        result = json.loads(response.text)
    print(f"ChatGPT回答：{result['current_response']}")
    # 连续对话迭代
    continuous_dialogue.append({"role": "user", "content": user_input})
    continuous_dialogue.append({"role": "assistant", "content": result['current_response']})
