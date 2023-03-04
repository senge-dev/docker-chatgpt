[中文](README-zh.md) | [English](README.md)

## 前言

建议在国外服务器上搭建（不包括中国香港和中国台湾的服务器），搭建完成后可以通过国内直接访问。

该文档使用Flask API获取ChatGPT的回答，为了防止影响服务器上运行的其他程序，我特意将其打包成了Docker镜像。

该项目可以直接拉取镜像运行，也可以通过docker-compose安装

该项目使用AGPL开源，严禁商用，严禁用于收费项目

允许修改后再发布，但是修改后必须使用AGPL开源，严禁修改协议

## 安装

### **使用docker-compose安装**

新建一个目录用于存放docker-compose.yaml文件

```bash
mkdir -p /opt/docker/docker-chatgpt
```

在新建的目录下创建docker-compose.yaml文件并写入以下内容

```bash
version: '3'

services:
  web:
    image: sengedev/docker-chatgpt:latest
    ports:
      - "5000:5000"
    restart: always
```

切换目录到docker-compose.yaml所在目录并运行以下命令启动docker容器

```bash
docker-compose up -d
```

### 手动安装

从Docker Hub拉取镜像

```bash
docker pull sengedev/docker-chatgpt:latest
```

直接运行镜像

```bash
docker run -d -p 5000:5000 sengedev/docker-chatgpt:latest 
```

## **如何使用**

### 请求方式

假设你的服务器ip为`12.34.56.78`，端口号为`5000`，则可以通过以下方式获取回答

请求方法：`POST`，目录：`/`

| 参数   | 说明                               | 是否必需 |
| ------ | ---------------------------------- | -------- |
| api    | OpenAI的API 密钥                   | 是       |
| prompt | 向ChatGPT发送的消息                | 是       |
| model  | OpenAI模型，默认为text-davinci-003 | 否       |

### **示例代码**

- Python

```python
import requests
 
url = 'http://12.34.56.78:5000/'
data = {'api': 'your_api_key', 'prompt': 'your_message', 'model': 'text-davinci-003'}
 
response = requests.post(url, data=data)
 
print(response.text)
```

- Java

```java
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
 
public class HttpPostExample {
    public static void main(String[] args) throws Exception {
        String url = "http://12.34.56.78:5000/";
        String charset = "UTF-8";
        String api = "your_api_key";
        String prompt = "your_message";
        String model = "text-davinci-003";
        
        String query = String.format("api=%s&prompt=%s&model=%s",
                URLEncoder.encode(api, charset),
                URLEncoder.encode(prompt, charset),
                URLEncoder.encode(model, charset));
        
        HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection();
        connection.setRequestMethod("POST");
        connection.setDoOutput(true);
        connection.setRequestProperty("Accept-Charset", charset);
        connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded;charset=" + charset);
        connection.getOutputStream().write(query.getBytes(charset));
        
        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        String line = reader.readLine();
        while (line != null) {
            System.out.println(line);
            line = reader.readLine();
        }
        reader.close();
    }
}
```

- curl

```bash
curl --location --request POST 'http://12.34.56.78:5000/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'api=your_api_key' \
--data-urlencode 'prompt=your_message' \
--data-urlencode 'model=text-davinci-003'
```

- PHP

```php
<?php
$url = 'http://12.34.56.78:5000/';
$data = array('api' => 'your_api_key', 'prompt' => 'your_message', 'model' => 'text-davinci-003');
 
$options = array(
    'http' => array(
        'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
        'method'  => 'POST',
        'content' => http_build_query($data),
    ),
);
 
$context  = stream_context_create($options);
$result = file_get_contents($url, false, $context);
 
echo $result;
?>
```

- JavaScript

```javascript
const url = 'http://12.34.56.78:5000/';
const api = 'your_api_key';
const prompt = 'your_message';
const model = 'text-davinci-003';
 
const data = new URLSearchParams();
data.append('api', api);
data.append('prompt', prompt);
data.append('model', model);
 
fetch(url, {
  method: 'POST',
  body: data
})
.then(response => response.text())
.then(data => console.log(data));
```

