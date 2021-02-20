FROM openbridge/nginx:latest
RUN addgroup -g 1000 -S nginx \
 && adduser -u 1000 -D -S -G nginx nginx

ADD nginx.conf /etc/nginx/nginx.conf
COPY /src/static/ /var/www/app/static/
COPY ./wait-for-it.sh ./wait-for-it.sh
COPY ./nginx-entrypoint.sh ./nginx-entrypoint.sh

EXPOSE 80

RUN ["chmod", "+x", "nginx-entrypoint.sh"]

ENTRYPOINT ["sh", "nginx-entrypoint.sh"]

