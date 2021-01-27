FROM nginx:alpine

RUN apk update && apk add bash

ADD nginx.conf /etc/nginx/nginx.conf
COPY /static/ /var/www/app/static/
COPY ./wait-for ./wait-for
COPY ./nginx-entrypoint.sh ./nginx-entrypoint.sh

EXPOSE 80

RUN ["chmod", "+x", "nginx-entrypoint.sh"]

ENTRYPOINT ["sh", "nginx-entrypoint.sh"]

