FROM python:3.14-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
