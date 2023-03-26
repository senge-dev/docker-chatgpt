# Проект Docker: платформа ChatGPT API

Этот документ также содержит переводы для следующих языков

[English](README.md) | [简体中文](README-zh_CN.md) | [繁體中文](README-zh_TW.md) | [Русский](README-ru_RU.md)

## Самостоятельное создание

Скопируйте следующий код и измените конфигурацию самостоятельно

```yaml
version: '3'

# GPL-лицензия с открытым исходным кодом, запрещено коммерческое использование, запрещено изменение и закрытие исходного кода после изменения, запрещена прибыль!

services:
  web:
    image: sengedev/chatgpt:latest   # Адрес зеркала
    ports:
      - "5000:5000" # Номер порта, если порт занят, измените его
    restart: always # Стратегия перезапуска
    environment:
      API_KEY: YourOpenAIApiKey # Замените на свой ключ OpenAI API, перейдите на https://platform.openai.com/account/api-keys для получения
      HOUR_LIMIT: 50  # Ограничение количества вызовов в час, если вы не хотите ограничивать, не устанавливайте эту переменную
      MINUTE_LIMIT: 3 # Ограничение количества вызовов в минуту, если вы не хотите ограничивать, не устанавливайте эту переменную
      SECOND_LIMIT: 1 # Ограничение количества вызовов в секунду, если вы не хотите ограничивать, не устанавливайте эту переменную
      ROUTE: api  # Маршрут, если вы не хотите устанавливать, не устанавливайте эту переменную
      LANG: zh_CN # Язык, в настоящее время поддерживаются упрощенный китайский, традиционный китайский, английский и русский языки
```

Значение поля

| Поле         | Значение                                                         |
| ------------ | ------------------------------------------------------------ |
| API_KEY      | API-ключ, после настройки вызов может быть завершен без заголовка запроса, не рекомендуется устанавливать, если вы не включили белый список IP-адресов |
| HOUR_LIMIT   | Ограничение количества вызовов в час, если установлено значение 0, ограничений нет |
| MINUTE_LIMIT | Ограничение количества вызовов в минуту, если установлено значение 0, ограничений нет |
| SECOND_LIMIT | Ограничение количества вызовов в секунду, если установлено значение 0, ограничений нет |
| ROUTE        | Например, если ваш сайт - https://chatgpt.example.com , маршрут - api, то ссылка запроса будет https://chatgpt.example.com/api |

## Описание примера

### Руководство по использованию

Ниже приведен пример адреса API, замените его на свой IP / домен.

API-ссылка: https://chatgpt.example.com/

Получить ответ ChatGPT

Метод запроса: `POST`, маршрут: `/api`


#### Параметры запроса

|данные |описание |требуемые |
|---------------------- | -------|------|
|sys_content|Конфигурация системы, некоторые ограничения на ChatGPT |Нет|
|user_content |Контент, отправленный в ChatGPT |Да |
|model|модель, по умолчанию текст-davinci-003 модель |Нет |
|api_key|Ключ API, должен быть настроен, если только вы не добавляли ключ API в Docker-compose |Нет|
|max_tokens|Максимальное количество генерируемых токенов, по умолчанию 100, максимальное 3500 |Нет|
|непрерывный |Непрерывный диалоговый параметр, может повторяться для реализации контекстных диалоговых операций |Нет |

#### возвращаемое значение

- успех

```json
{
     "код": 200,
     "msg": "успех",
     "данные": {
         "response": "Содержимое ответа ChatGPT"
     }
}
```

- неудача

```json
{
     "код": "4xx",
     "msg": "не удалось",
     "данные": {
         "response": "Причина отклонения запроса"
     }
}
```

- Общие возвращаемые значения

|код |описание |
|-----|------------|
|200 |Успех |
|400 |Ошибка параметра запроса (API не заполнен или заполнен неверно, модель используется неправильно, подсказка отсутствует или пустая подсказка) |
|401 |Неавторизованный |
|403 |Запрещено |
|404 |Путь запроса не существует |
|500 |Внутренняя ошибка сервера |
|429 |Запрос слишком частый |

#### Лимит звонков по умолчанию (на IP)

API полностью открыт для использования, приложение не требуется, но вам необходимо подать заявку на ключ API самостоятельно.

|период времени |частота |
|-----|-----|
|дней |без ограничений |
|час |50 раз |
|мин |3 раза |
|второй |1 раз |

## образец кода

Замените https://chatgpt.example.com на IP/адрес доменного имени вашего сервера заранее.

### Python (непрерывный диалог)

```python
import requests
import json


token = {
    "api_key": "Your API Key",  # Замените своим ключом API
    "url": "https://chatgpt.example.com/api"    # Замените его своим экземпляром
}


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
        print(f"Запрос не выполнен с кодом состояния: {response.status_code}, Возвращаемое значение сервера: {response.text}")
        continue
    else:
        result = json.loads(response.text)
    print(f"ChatGPT> {result['current_response']}")
    # Непрерывная итерация диалога
    continuous_dialogue.append({"role": "user", "content": user_input})
    continuous_dialogue.append({"role": "assistant", "content": result['current_response']})

print("программа вышла")
```

### Python (непоследовательный диалог)

```python
import sys
import requests
import json


token = {
    "api_key": "Your API Key",  # Замените своим ключом API
    "url": "https://chatgpt.example.com/api"    # Замените его своим экземпляром
}


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
    print(f"Запрос не выполнен с кодом состояния: {response.status_code}, Возвращаемое значение сервера: {response.text}")
    sys.exit(1)
else:
    result = json.loads(response.text)
print(f"ChatGPT> {result['current_response']}")
```
