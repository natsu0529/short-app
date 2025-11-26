# デプロイ時間を短縮するため slim 版推奨ですが、今のままでも動きます
FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
# 本番用サーバーを追加インストール
RUN pip install gunicorn

COPY . /app/

# Cloud Run 用のポート設定
ENV PORT 8080

# 【重要】ここが本番用の起動コマンドになります
# ローカル(docker-compose)では無視され、Cloud Runでのみ実行されます
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 short_app.wsgi:application