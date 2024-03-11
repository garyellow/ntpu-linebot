# 第一階段：安裝 poetry 並建立套件清單
FROM python:3.12-slim AS builder

# 安裝 poetry
RUN pip install poetry

# 將 pyproject.toml 和 poetry.lock(如果有) 複製到容器中
COPY pyproject.toml poetry.lock* ./

# 若 poetry.lock 不存在，則執行 poetry lock 建立
RUN if [ ! -f poetry.lock ]; then poetry lock; fi

# 建立依賴清單
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# 第二階段：建立執行環境
FROM python:3.12-slim AS runner

# 設定 LABEL
LABEL org.opencontainers.image.title="ntpu-linebot"
LABEL org.opencontainers.image.description="Linebot for NTPU"
LABEL org.opencontainers.image.authors="garyellow"
LABEL org.opencontainers.image.source=https://github.com/garyellow/ntpu-linebot
LABEL org.opencontainers.image.version="3.0.0"
LABEL org.opencontainers.image.licenses=MIT

# 複製第一階段的 wheels 和 requirements.txt
COPY --from=builder /wheels /wheels
COPY --from=builder /requirements.txt /requirements.txt

# 安裝套件，並刪除 wheels 和 requirements.txt
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt &&\
    rm -rf /wheels /requirements.txt

# 將 app.py 和 ntpu_linebot 目錄複製到容器中
COPY app.py .
COPY ntpu_linebot ntpu_linebot/

# 使用 sanic 執行應用程式
ENTRYPOINT ["sanic", "app:app"]
CMD ["--host=0.0.0.0", "--port=10000", "--no-access-logs"]
