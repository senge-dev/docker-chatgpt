# docker chatgpt

[中文](README-zh.md)|[English](README.md)

This project is using Flask API to get the answer from ChatGPT, in order to prevent affecting the other programs running on the server, I specially packaged it into a Docker image.

It can be run directly by pulling the image, or it can be installed by docker-compose

## Install using docker-compose

Create a new directory to place the docker-compose file

```bash
mkdir -p /opt/docker/docker-chatgpt
```

Create docker-compose.yaml file in the new directory and write the following content

```yaml
version: '3'

services:
  web:
    image: sengedev/docker-chatgpt:0.1.0
    ports:
      - "5000:5000"
    restart: always
```

Change to the docker directory and run the following command to start the docker container

```bash
docker-compose up -d
```

## Install this image manually

Pull the image from Docker Hub

```bash
docker pull sengedev/docker-chatgpt:0.1.0
```

Run the image

```bash
docker run -d -p 5000:5000 sengedev/docker-chatgpt:0.1.0
```

## How to use

### HTTP Request

if your server ip is 12.34.56.78, the port is 5000, you can use this method to get the answer.

Method: `POST`, Directory: `/`

Required parameters

| Parameters | Description | Must Include |
| ------------------- | ------------------ | ------------ |
| api              | API Key | Yes |
| prompt | send message to ChatGPT | Yes |
| model | OpenAI model, default is text-davinci-003 | No |

### Sample Code

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
