# Docker專案：ChatGPT API 平台

該文檔同時提供了以下語言的翻譯

[English](README.md) | [简体中文](README-zh_CN.md) | [繁體中文](README-zh_TW.md) | [Русский](README-ru_RU.md)

## 自行搭建

複製下列程式碼，並自行修改配置

```yaml
version: '3'

# GPL協議開源，禁止商用，禁止修改後閉源，禁止盈利！！！

services:
  web:
    image: sengedev/chatgpt:latest   # 鏡像地址
    ports:
      - "5000:5000" # 端口號，如果端口衝突，請修改
    restart: always # 重啟策略
    environment:
      API_KEY: YourOpenAIApiKey # 請替換為你的OpenAI API Key，前往https://platform.openai.com/account/api-keys獲取
      HOUR_LIMIT: 50  # 限制每小時調用次數，如果不想限制，則不設置該變量
      MINUTE_LIMIT: 3 # 限制每分鐘調用次數，如果不想限制，則不設置該變量
      SECOND_LIMIT: 1 # 限制每秒調用次數，如果不想限制，則不設置該變量
      ROUTE: api  # 路由，如果不想設置，則不設置該環境變量
      LANG: zh_TW # 語言，目前支持簡體中文、繁體中文、英文、俄語
```

字段含義

| 字段         | 含義                                                         |
| ------------ | ------------------------------------------------------------ |
| API_KEY      | API密鑰，配置後無需請求頭即可完成調用，不建議設置，除非你開啟了IP地址白名單 |
| HOUR_LIMIT   | 每小時調用次數限制，如果設置為0則無限制                      |
| MINUTE_LIMIT | 每分鐘調用次數限制，如果設置為0則無限制                      |
| SECOND_LIMIT | 每秒調用次數限制，如果設置為0則無限制                        |
| ROUTE        | 例如你的網站是https://chatgpt.example.com ，路由為api，則請求鏈接為 https://chatgpt.example.com/api |

## 實例介紹

### 使用教程

下方是一個示例API地址，請替換為您自己的IP/域名。

API鏈接: https://chatgpt.example.com/

獲取ChatGPT回答

請求方式：`POST`，路由：`/api`

#### 請求參數

| 數據           | 描述                                      | 是否必需 |
|--------------|-----------------------------------------|------|
| sys_content  | 系統配置，對ChatGPT的一些限制                      | 否    |
| user_content | 向ChatGPT發送的內容                           | 是    |
| model        | 模型，默認使用text-davinci-003模型               | 是    |
| api_key      | API密鑰，必須配置，除非你在Docker-comppose中添加了API密鑰 | 否    |
| max_tokens   | 最大生成的token數量，默認為100，最大為3500             | 否    |
| continuous   | 連續對話參數，可以進行迭代來實現上下文對話操作            | 否    |

#### 返回值

- 成功

```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "response": "ChatGPT回答的內容"
    }
}
```

- 失敗

```json
{
    "code": "4xx",
    "msg": "failed",
    "data": {
        "response": "請求失敗的原因"
    }
}
```

- 常見返回值

| code | 描述                                           |
|------|----------------------------------------------|
| 200  | 成功                                           |
| 400  | 請求參數錯誤(API未填寫或填寫錯誤、模型使用錯誤、缺少prompt或prompt為空) |
| 401  | 未授權                                          |
| 403  | 禁止訪問                                         |
| 404  | 請求路徑不存在                                      |
| 500  | 服務器內部錯誤                                      |
| 429  | 請求過於頻繁                                       |

#### 默認調用次數限制（每個IP）

API完全開放使用，無需申請，但是需要自行申請API Key

| 時間段 | 頻率  |
|-----|-----|
| 天   | 無限制 |
| 小時  | 50次 |
| 分鐘  | 3次  |
| 秒   | 1次  |

## 示例代码

將https://chatgpt.example.com/api 替換為你的服務器IP/域名地址

### Python（連續對話）

```python
import requests
import json


token = {
    "api_key": "Your API Key",  # 替換成你自己的API Key
    "url": "https://chatgpt.example.com/api"    # 替換成你自己搭建的實例
}


# ChatGPT API Demo
url = token["url"]
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
        "api_key": token["api_key"],
        "continuous": [],
        "max_tokens": 3000
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"請求失敗，狀態碼：{response.status_code}，服務器返回值：{response.text}")
        continue
    else:
        result = json.loads(response.text)
    print(f"ChatGPT> {result['current_response']}")
    # 連續對話迭代
    continuous_dialogue.append({"role": "user", "content": user_input})
    continuous_dialogue.append({"role": "assistant", "content": result['current_response']})

print("程序已退出")
```

### Python（非連續對話）

```python
import sys
import requests
import json


token = {
    "api_key": "Your API Key",  # 替換成你自己的API Key
    "url": "https://chatgpt.example.com/api"    # 替換成你自己搭建的實例
}


# ChatGPT API Demo
url = token["url"]
sys_prompt = input("sys> ")
user_input = input("user> ")
data = {
    "system_content": sys_prompt,
    "user_content": user_input,
    "model": "gpt-3.5-turbo",
    "api_key": token["api_key"],
    "continuous": [],
    "max_tokens": 3000
}
response = requests.post(url, json=data)
if response.status_code != 200:
    print(f"請求失敗，狀態碼：{response.status_code}，服務器返回值：{response.text}")
    sys.exit(1)
else:
    result = json.loads(response.text)
print(f"ChatGPT> {result['current_response']}")
```
