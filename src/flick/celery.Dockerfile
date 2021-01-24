FROM python:3-alpine

# Install dependencies required for psycopg2 python package
RUN apk update && apk add libpq && apk add bash
RUN apk update && apk add --virtual .build-deps gcc build-base python3-dev musl-dev postgresql-dev 
RUN apk update && apk add libxml2-dev libxslt-dev py-lxml
RUN apk add --no-cache \
        libressl-dev \
        musl-dev \
        libffi-dev && \
    pip install --no-cache-dir cryptography==2.1.4 && \
    apk del \
        libressl-dev \
        musl-dev \
        libffi-dev

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .
RUN mv wait-for /bin/wait-for

RUN pip install --no-cache-dir -r requirements.txt

# Remove dependencies only required for psycopg2 build
RUN apk del .build-deps

EXPOSE 8000

RUN ["chmod", "+x", "celery-entrypoint.sh"]

ENTRYPOINT ["sh", "celery-entrypoint.sh"]