FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=3000
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

WORKDIR /srv
COPY app ./app

# Run as a non-root user (least privilege)
RUN useradd --system --no-create-home appuser
USER appuser

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:3000/health', timeout=2).status==200 else 1)"

CMD ["python", "-m", "app.server"]
