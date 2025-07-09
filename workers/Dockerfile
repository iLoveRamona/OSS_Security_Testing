# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt
    # добавьте другие зависимости, которые использует ваш код

# Запускаем скрипт
CMD ["python", "worker.py"]