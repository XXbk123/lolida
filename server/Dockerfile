# 萝莉dao FastAPI 后端 Docker 镜像（连接 Supabase PostgreSQL）
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static

ENV HOST=0.0.0.0
ENV PORT=8765

EXPOSE 8765

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765"]
