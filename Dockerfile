FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir . && \
    useradd --create-home --shell /usr/sbin/nologin jarvis

USER jarvis
EXPOSE 8010
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8010/health', timeout=3)" || exit 1

CMD ["uvicorn", "jarvis_noc.main:app", "--host", "0.0.0.0", "--port", "8010"]
