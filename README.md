# Загрузчик информации о кандидатах в Хантфлоу

Данный скрипт позволяет выполнить перенос информации о кандидатах и их привязки к вакансиям из файловой базы данных в Хантфлоу, используя [Хантфлоу API](https://github.com/huntflow/api).
В случае прерывания работы, при повторном запуске скрипта перененос информации возобновляется с прерванного места.

## Как запустить

Для своей работы скрипт требует установки интерпретатора Python версии не ниже 3.7

* Скачать репозиторий и перейти в папку с проектом:
```bash

$ git clone https://github.com/ivan-shishkov/huntflow-applicants-loader.git
$ cd huntflow-applicants-loader/

```

* Создать виртуальное окружение и активировать его:
```bash

$ python -m venv venv
$ source venv/bin/activate

```

* Установить все необходимые зависимости:
```bash

$ pip install -r requirements.txt

```

* Выполнить запуск скрипта, задав все необходимые параметры:
```bash

$ python loader.py --help
usage: loader.py [-h] --path PATH --endpoint ENDPOINT --token TOKEN

If an arg is specified in more than one place, then commandline values
override environment variables which override defaults.

optional arguments:
  -h, --help           show this help message and exit
  --path PATH          Путь к директории с исходной файловой базой данных [env
                       var: SOURCE_DATABASE_PATH]
  --endpoint ENDPOINT  URL-адрес сервера с Хантфлоу API [env var:
                       HUNTFLOW_API_ENDPOINT_URL]
  --token TOKEN        Персональный токен для работы с Хантфлоу API [env var:
                       HUNTFLOW_API_TOKEN]

```
