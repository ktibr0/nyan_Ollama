Измените подключение к локальному серверу с Ollama и название модели в:

/nyan/openai.py (в двух местах) (строки  101 - модель, 12,13, 17 - строка подключения, в 78 строке сделайте вызов ollama_client)

/nyan/topics.py - название модели (строка 132)

/nyan/clusters.py - название модели (строка 161)


# НЯН

[![Tests Status](https://github.com/NyanNyanovich/nyan/actions/workflows/python.yml/badge.svg)](https://github.com/NyanNyanovich/nyan/actions/workflows/python.yml)
[![https://t.me/nyannews](https://img.shields.io/badge/Telegram-nyannews-blue.svg?logo=telegram)](https://t.me/nyannews)
[![License](https://img.shields.io/github/license/NyanNyanovich/nyan)](https://github.com/NyanNyanovich/nyan/blob/master/LICENSE)

<img width="1189" alt="изображение" src="https://user-images.githubusercontent.com/104140467/193427932-f5b3ecdd-835f-493f-9901-553c03bdff9b.png">

НЯН (Nyan) is a news aggregator that scrapes news from different Telegram channels, clusters similar posts, and forms a united feed. All sources are split into several groups, so anyone can understand whether they can trust them.

Channel itself: [NyanNews](https://t.me/nyannews)

Extensive description (in Russian): [Whitepaper](https://telegra.ph/NYAN-Whitepaper-04-03)

Detailed instruction (in Russian): [Как поднять свой НЯН](https://github.com/NyanNyanovich/nyan/wiki/%D0%9A%D0%B0%D0%BA-%D0%BF%D0%BE%D0%B4%D0%BD%D1%8F%D1%82%D1%8C-%D1%81%D0%B2%D0%BE%D0%B9-%D0%9D%D0%AF%D0%9D)


## Install

Install git and pip
```
sudo apt-get install git python3-pip
```

Clone repo
```
git clone https://github.com/NyanNyanovich/nyan
```

Install Python requirements
```
pip3 install -r requirements.txt
```

Download models
```
bash download_models.sh
```

Install Docker and Docker Compose.
* Docker instructions: https://docs.docker.com/engine/install
* Docker Compose instructions: https://docs.docker.com/compose/install

Provide Telegram API credentials to [configs/client_config.json](https://github.com/NyanNyanovich/nyan/blob/main/configs/client_config.json).

## Run

Run Mongo container
```
docker-compose up
```

Run crawler
```
bash crawl.sh
```

Run server
```
bash send.sh
```

You can provide OPENAI_API_KEY environment variable to use LLM-related features.
