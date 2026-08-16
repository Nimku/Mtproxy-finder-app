FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# data/ holds the generated list, language preferences and the Telethon session,
# so it must be a volume — see docker-compose.yml.
CMD ["python", "bot.py"]
