#!/bin/bash
set -e

# Получение расписания из переменных окружения
CRAWL_SCHEDULE=${CRAWL_SCHEDULE:-"0 */6 * * *"}
SEND_SCHEDULE=${SEND_SCHEDULE:-"30 */6 * * *"}

echo "Настройка cron расписания..."
echo "Crawl schedule: $CRAWL_SCHEDULE"
echo "Send schedule: $SEND_SCHEDULE"

# Получаем полный путь к Python
PYTHON_PATH=$(which python3)

# Создание cron задач с полными путями и переменными окружения
cat > /etc/cron.d/nyan-cron << EOF
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PYTHONPATH=/app

# Запуск парсинга каналов
$CRAWL_SCHEDULE root cd /app && $PYTHON_PATH -m scrapy crawl telegram -a channels_file=channels.json -a fetch_times=crawler/fetch_times.json -a hours=24 >> /var/log/cron.log 2>&1

# Запуск обработки и отправки
$SEND_SCHEDULE root cd /app && $PYTHON_PATH -m nyan.send --channels-info-path channels.json --client-config-path configs/client_config.json --mongo-config-path configs/mongo_config.json --annotator-config-path configs/annotator_config.json --renderer-config-path configs/renderer_config.json --daemon-config-path configs/daemon_config.json >> /var/log/cron.log 2>&1

# Пустая строка в конце файла (required by cron)
EOF

# Применение прав на cron файл
chmod 0644 /etc/cron.d/nyan-cron

# Применение cron задач
crontab /etc/cron.d/nyan-cron

echo "Cron задачи настроены:"
crontab -l

# Логирование
echo "Запуск cron демона..."
echo "Логи будут доступны в /var/log/cron.log"

# Опционально: запуск первого crawl сразу при старте
if [ "${RUN_CRAWL_ON_START}" = "true" ]; then
    echo "Запуск первоначального парсинга..."
    cd /app && $PYTHON_PATH -m scrapy crawl telegram -a channels_file=channels.json -a fetch_times=crawler/fetch_times.json -a hours=24 >> /var/log/cron.log 2>&1 &
fi

# Запуск команды из CMD
exec "$@"