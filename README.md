# Docker Project: ChatGPT API Platform

This document is also supported for the following languages

[English](README.md) | [简体中文](README-zh_CN.md) | [繁體中文](README-zh_TW.md) | [Русский](README-ru_RU.md)

## Self Built

Copy the following code and modify the configuration yourself

```yaml
version: '3'

# GPL protocol open source, no commercial use, no modification and closure after modification, no profit!!!

services:
  web:
    image: sengedev/chatgpt:latest   # Mirror address
    ports:
      - "5000:5000" # Port number, if the port conflicts, please modify it
    restart: always # Restart strategy
    environment:
      API_KEY: YourOpenAIApiKey # Please replace it with your OpenAI API Key, go to https://platform.openai.com/account/api-keys to get it
      HOUR_LIMIT: 50  # Limit the number of calls per hour, if you don't want to limit it, don't set this variable
      MINUTE_LIMIT: 3 # Limit the number of calls per minute, if you don't want to limit it, don't set this variable
      SECOND_LIMIT: 1 # Limit the number of calls per second, if you don't want to limit it, don't set this variable
      ROUTE: api  # Route, if you don't want to set it, don't set this environment variable
      LANG: zh_CN # Language, currently supports Simplified Chinese, Traditional Chinese, English, and Russian
```

Field meaning

| Field         | Meaning                                                     |
| ------------ | ------------------------------------------------------------ |
| API_KEY      | API key, after configuration, the call can be completed without the request header, it is not recommended to set it, unless you have enabled the IP address whitelist |
| HOUR_LIMIT   | The number of calls per hour is limited. If it is set to 0, there is no limit |
| MINUTE_LIMIT | The number of calls per minute is limited. If it is set to 0, there is no limit |
| SECOND_LIMIT | The number of calls per second is limited. If it is set to 0, there is no limit |
| ROUTE        | For example, if your website is https://api.example.com and the route is route, the request link is https://api.example.com/route |

## Instance Introduction


### Tutorial

Here is an example API address, please replace it with your own IP/domain.

API link: https://chatgpt.example.com/

Get ChatGPT answer

Request method: `POST`, route: `/api`

#### Request Parameters


| Data           | Description                                      | Required |
|--------------|-----------------------------------------|------|
| sys_content  | System configuration, some restrictions on ChatGPT                      | No    |
| user_content | Content sent to ChatGPT                           | Yes    |
| model        | Model, default to text-davinci-003 model               | No    |
| api_key      | API key, must be configured, unless you add an API key in Docker-comppose | No    |
| max_tokens   | The maximum number of tokens generated, default is 100, maximum is 3500             | No    |
| continuous   | Continuous dialogue parameters, can be iterated to achieve context dialogue operations            | No    |

#### Response


- Success

```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "response": "Content answered by ChatGPT"
    }
}
```

- Failure

```json
{
    "code": "4xx",
    "msg": "failed",
    "data": {
        "response": "Reason for request failure"
    }
}
```

- Common response values

| code | Description                                           |
|------|-------------------------------------------------------|
| 200  | Success                                               |
| 400  | Request parameter error (API not filled in or filled in incorrectly, model usage error, prompt missing or prompt empty) |
| 401  | Unauthorized                                           |
| 403  | Forbidden                                              |
| 404  | Request path does not exist                            |
| 500  | Internal server error                                  |
| 429  | Request too frequent                                   |

#### Default call limit (per IP)

The API is completely open for use without application, but you need to apply for an API Key yourself.

| Time period | Frequency |
|-------------|-----------|
| Day         | Unlimited |
| Hour        | 50 times  |
| Minute      | 3 times   |
| Second      | 1 time    |

## Example Code


Replace https://api.example.com with your server IP/domain address

### Python (Continuous Dialogue)

```python
import requests
import json


token = {
    "api_key": "Your API Key",  # Replace with your own API Key
    "url": "https://chatgpt.example.com/api"    # Replace with your own instance
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
        print(f"Request failed, status code: {response.status_code}, server response: {response.text}")
        continue
    else:
        result = json.loads(response.text)
    print(f"ChatGPT> {result['current_response']}")
    # Continuous dialogue iteration
    continuous_dialogue.append({"role": "user", "content": user_input})
    continuous_dialogue.append({"role": "assistant", "content": result['current_response']})

print("Program has exited")
```

### Python (Non-Continuous Dialogue)

```python
import sys
import requests
import json


token = {
    "api_key": "Your API Key",  # Replace with your own API Key
    "url": "https://chatgpt.example.com/api"    # Replace with your own instance
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
    print(f"Request failed, status code: {response.status_code}, server response: {response.text}")
    sys.exit(1)
else:
    result = json.loads(response.text)
print(f"ChatGPT> {result['current_response']}")
```
