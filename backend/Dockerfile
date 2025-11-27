FROM python:3.14-slim

WORKDIR /app

COPY ../pyproject.toml .

RUN pip install --no-cache-dir -e .
RUN apt-get update && apt-get install -y tk

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
