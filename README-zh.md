# docker chatgpt

This document is also avaliable for Chinese, Chinese user please visit [https://senge.dev/index.php/docker-chatgpt/](https://senge.dev/index.php/docker-chatgpt/)
该文档有中文翻译，国内用户请访问 [https://senge.dev/index.php/docker-chatgpt/](https://senge.dev/index.php/docker-chatgpt/)

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