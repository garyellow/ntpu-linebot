# 第一階段：安裝 poetry 並建立依賴清單
FROM python:3.11 AS builder

WORKDIR /app

# 安裝 poetry
RUN pip install poetry

# 將 pyproject.toml 和 poetry.lock(如果有) 複製到容器中
COPY pyproject.toml poetry.lock* /app/

# 若 poetry.lock 不存在，則執行 poetry lock 建立
RUN if [ ! -f poetry.lock ]; then poetry lock; fi

# 建立依賴清單
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# 第二階段：建立執行環境
FROM python:3.11-slim AS runner

# 設定 LABEL
LABEL org.opencontainers.image.source=https://github.com/garyellow/ntpu-id-linebot
LABEL org.opencontainers.image.description="NTPU ID Linebot"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /app

# 複製第一階段的 wheels 和 requirements.txt
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# 安裝依賴項
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# 複製應用程式
COPY app.py .
COPY src/* src/

# 使用 uvicorn 執行
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]