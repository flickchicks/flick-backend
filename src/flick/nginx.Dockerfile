FROM nginx

ADD nginx.conf /etc/nginx/nginx.conf
COPY /static/ /var/www/app/static/
COPY ./wait-for-it.sh ./wait-for-it.sh
COPY ./nginx-entrypoint.sh ./nginx-entrypoint.sh

EXPOSE 80

RUN ["chmod", "+x", "nginx-entrypoint.sh"]

ENTRYPOINT ["sh", "nginx-entrypoint.sh"]

