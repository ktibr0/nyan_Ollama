FROM python:3.9-slim

# Установка системных зависимостей включая build-tools для компиляции
RUN apt-get update && apt-get install -y \
    git \
    wget \
    cron \
    build-essential \
    g++ \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование requirements.txt и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов проекта
COPY . .

# Скачивание моделей
#RUN bash download_models.sh

# Создание директории для данных
RUN mkdir -p data

# Копирование entrypoint скрипта
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Создание cron log файла
RUN touch /var/log/cron.log

# Запуск entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["cron", "-f"]