# pull official base image
FROM python:3.7.6-slim-buster

# set environment variables
ENV PYTHONUNBUFFERED 1

# create and set work directory
RUN mkdir /usr/src/app/
WORKDIR /usr/src/app

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# install dependencies
RUN pip install -r requirements.txt

