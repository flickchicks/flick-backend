# FROM python:3.7-alpine

# # Install dependencies required for psycopg2 python package
# RUN apk update && apk add libpq && apk add bash
# RUN apk update && apk add --virtual .build-deps gcc build-base python3-dev musl-dev postgresql-dev 
# RUN apk update && apk add libxml2-dev libxslt-dev py-lxml
# RUN apk add --no-cache \
#         libressl-dev \
#         musl-dev \
#         libffi-dev && \
#     pip install --no-cache-dir cryptography==2.1.4 && \
#     apk del \
#         libressl-dev \
#         musl-dev \
#         libffi-dev

# FROM ubuntu:latest
# FROM python:3.7.6-slim-buster

FROM python:3.7-buster


# ENV DEBIAN_FRONTEND=noninteractive
# ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && pip3 install --upgrade pip
RUN apt-get -q update && apt-get -qy install netcat


RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
# RUN ["chmod", "+x", "wait-for-it.sh"]

COPY . .

# RUN chmod +x wait-for-it.sh
# RUN mv wait-for-it.sh /bin/wait-for-it.sh
# USER root 
# RUN chmod 755 /usr/src/app/wait-for-it.sh
# RUN chmod +x /usr/src/app/wait-for-it.sh
# COPY wait-for-it.sh /wait-for-it.sh
# RUN chmod +x /wait-for-it.sh
RUN ["chmod", "+x", "/usr/src/app/wait-for-it.sh"]

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "flick.wsgi", "0:8000"]
