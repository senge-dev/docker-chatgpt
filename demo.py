import requests
import json
import sys

# ChatGPT API Demo（非连续对话模式）
url = "https://chatgpt.example.com/api"
sys_prompt = input("sys> ")

user_input = input("user> ")
data = {
    "system_content": sys_prompt,
    "user_content": user_input,
    "model": "gpt-3.5-turbo",
    "api_key": "sk-U3y83c7o8nOn8i4ONnoT5uA9B6Yd75xrl9BIKihk4vCmCMzi",  # 该API为 fake API Key，请换成自己的API Key
    "max_tokens": 100
}
response = requests.post(url, json=data)
if response.status_code != 200:
    print(f"请求失败，状态码：{response.status_code}")
    print(response.text)
    sys.exit(1)
else:
    result = json.loads(response.text)
print(f"ChatGPT回答：{result['current_response']}")
