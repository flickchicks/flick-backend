FROM nginx:alpine

RUN apk update && apk add bash

COPY . .

RUN ["chmod", "+x", "nginx-entrypoint.sh"]

EXPOSE 80

ENTRYPOINT ["sh", "nginx-entrypoint.sh"]

