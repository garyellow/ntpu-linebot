# 第一階段：安裝 poetry 和依賴項
FROM python:3.11 AS builder

WORKDIR /app

# 安裝 poetry
RUN pip install poetry

# 複製 pyproject.toml 和 poetry.lock (如果存在的話)
COPY pyproject.toml poetry.lock* /app/

# 安裝依賴項
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# 第二階段：建立執行環境
FROM python:3.11-slim AS runner

WORKDIR /app

# 複製第一階段的輪子檔案
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# 安裝依賴項
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# 複製應用程式
COPY . .

# 使用 uvicorn 執行
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]