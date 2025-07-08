# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем зависимости системы
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt
    # добавьте другие зависимости, которые использует ваш код

# Запускаем скрипт
CMD ["python", "./your_script_name.py"]