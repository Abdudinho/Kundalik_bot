FROM python:3.14-alpine
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip pip install -r requirements.txt
COPY . .
CMD ["python3", "main.py"]