FROM python:3.13.1-slim

RUN apt-get update \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /sources
RUN mkdir -p /resources

COPY ./sources /sources
COPY ./resources /resources

WORKDIR /sources

RUN pip install --no-cache-dir -r /resources/requirements.txt

VOLUME [ "/data" ]

RUN chmod +x /resources/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "-c", "/resources/entrypoint.sh && python manage.py \"$@\"", "--"]

CMD ["runserver", "0.0.0.0:8000"]