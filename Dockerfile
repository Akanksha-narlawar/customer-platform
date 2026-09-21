FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home appuser

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/app.py .

ENV APP_VERSION=5.0
ENV ENVIRONMENT=DEV

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')" || exit 1

CMD ["python", "app.py"]