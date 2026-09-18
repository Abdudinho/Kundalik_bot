    FROM python:3.14-alpine
    WORKDIR /app

    COPY requirements.txt .
    RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip pip install -r requirements.txt
COPY . .

CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]