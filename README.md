# Docker项目：ChatGPT API 平台

## 自行搭建

复制下列代码，并自行修改配置

```yaml
version: '3'

# GPL协议开源，禁止商用，禁止修改后闭源，禁止盈利！！！

services:
  web:
    image: sengedev/chatgpt:latest   # 镜像地址
    ports:
      - "5000:5000" # 端口号，如果端口冲突，请修改
    restart: always # 重启策略
    environment:
      API_KEY: YourOpenAIApiKey # 请替换为你的OpenAI API Key，前往https://platform.openai.com/account/api-keys获取
      HOUR_LIMIT: 50  # 限制每小时调用次数，如果不想限制，则不设置该变量
      MINUTE_LIMIT: 3 # 限制每分钟调用次数，如果不想限制，则不设置该变量
      SECOND_LIMIT: 1 # 限制每秒调用次数，如果不想限制，则不设置该变量
      ROUTE: api  # 路由，如果不想设置，则不设置该环境变量
    volumes:
      - ./logs:/app/logs # 日志保存路径
```

字段含义

| 字段         | 含义                                                         |
| ------------ | ------------------------------------------------------------ |
| volumes      | 持久化配置，文件映射                                         |
| API_KEY      | API密钥，配置后无需请求头即可完成调用，不建议设置，除非你开启了IP地址白名单 |
| HOUR_LIMIT   | 每小时调用次数限制，如果设置为0则无限制                      |
| MINUTE_LIMIT | 每分钟调用次数限制，如果设置为0则无限制                      |
| SECOND_LIMIT | 每秒调用次数限制，如果设置为0则无限制                        |
| ROUTE        | 例如你的网站是https://api.example.com，路由为route，则请求链接为https://api.example.com/route |

## 实例介绍

### 使用教程

下方是一个示例API地址，请替换为您自己的IP/域名。

API链接: https://api.example.com/

获取ChatGPT回答

请求方式：`GET`，路由：`/chatgpt`

#### 请求头

| 请求头 | 描述                                          | 是否必需 |
| ------ | --------------------------------------------- | -------- |
| ApiKey | ChatGPT的API密钥                              | 是`*1`   |
| Model  | ChatGPT API模型，默认使用text-davinci-003模型 | 否       |

#### 请求数据

| 数据   | 描述                | 是否必需 |
| ------ | ------------------- | -------- |
| prompt | 向ChatGPT发送的文本 | 是       |

#### 返回值

- 成功

```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "response": "ChatGPT回答的内容"
    }
}
```

- 失败

```json
{
    "code": 4xx,
    "msg": "failed",
    "data": {
        "response": "请求失败的原因"
    }
}
```

- 常见返回值

| code | 描述                                                         |
| ---- | ------------------------------------------------------------ |
| 200  | 成功                                                         |
| 400  | 请求参数错误(API未填写或填写错误、模型使用错误、缺少prompt或prompt为空) |
| 401  | 未授权                                                       |
| 403  | 禁止访问                                                     |
| 404  | 请求路径不存在                                               |
| 500  | 服务器内部错误                                               |
| 429  | 请求过于频繁                                                 |

#### 默认调用次数限制（每个IP）

API完全开放使用，无需申请，但是需要自行申请API Key

| 时间段 | 频率   |
| ------ | ------ |
| 天     | 无限制 |
| 小时   | 50次   |
| 分钟   | 3次    |
| 秒     | 1次    |

## 示例代码

将https://api.example.com替换为你的服务器IP/域名地址

### Python

```python
import requests

url = "https://api.example.com/chatgpt"

headers = {
    "ApiKey": "YourApiKey",
    "Model": "text-davinci-003"
}

params = {
    "prompt": "Hello"
}

response = requests.get(url, headers=headers, params=params)

print(response.json()["data"]["response"])
```

### Java

```java
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import java.io.IOException;

public class ChatGPTClient {
    public static void main(String[] args) throws IOException {
        OkHttpClient client = new OkHttpClient();

        String apiKey = "YourApiKey";
        String model = "text-davinci-003";
        String prompt = "Hello";
        String url = "https://api.example.com/chatgpt?prompt=" + prompt;

        Request request = new Request.Builder()
                .url(url)
                .addHeader("ApiKey", apiKey)
                .addHeader("Model", model)
                .get()
                .build();

        Response response = client.newCall(request).execute();
        System.out.println(response.body().string());
    }
}
```

### JavaScript

```javascript
const axios = require('axios');

const url = "https://api.example.com/chatgpt";
const apiKey = "YourApiKey";
const model = "text-davinci-003";
const prompt = "Hello";

axios.get(url, {
    headers: {
        ApiKey: apiKey,
        Model: model
    },
    params: {
        prompt: prompt
    }
})
.then(response => {
    console.log(response.data.data.response);
})
.catch(error => {
    console.log(error.response.data.data.response);
});
```

### curl

```bash
curl -H "ApiKey: YourApiKey" -H "Model: text-davinci-003" -X GET "https://api.example.com/chatgpt?prompt=Hello"
```

### GoLang

```go
package main

import (
	"fmt"
	"net/http"
	"io/ioutil"
)

func main() {

	url := "https://api.example.com/chatgpt?prompt=Hello"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("ApiKey", "YourApiKey")
	req.Header.Add("Model", "text-davinci-003")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := ioutil.ReadAll(res.Body)

	fmt.Println(string(body))
}
```

### PHP

```php
<?php

$url = "https://api.example.com/chatgpt";
$apiKey = "YourApiKey";
$model = "text-davinci-003";
$prompt = "Hello";

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url . "?prompt=" . $prompt);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    "ApiKey: " . $apiKey,
    "Model: " . $model
));
$response = curl_exec($ch);
curl_close($ch);

$response = json_decode($response, true);
echo $response["data"]["response"];

?>
```
