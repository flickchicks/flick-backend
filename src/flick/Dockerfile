FROM python:3.7-buster

RUN apt-get update && pip3 install --upgrade pip
RUN apt-get -q update && apt-get -qy install netcat

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .

RUN ["chmod", "+x", "/usr/src/app/wait-for-it.sh"]

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "flick.wsgi", "0:8000"]
