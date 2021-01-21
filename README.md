# flick-backend

Backend for flick app that handles users, lists, and movies.

## Install

```
git clone https://github.com/flickchicks/flick-backend.git
cd flick-backend
```

## Environment Variables

If you are a developer on on the team, there is a `.env` file pinned in the backend channel of the Slack, and you can put this file where `manage.py` is. Any other average Joe can create an `.env` file by copying the template:

```
cp env.template .env
```

Another file that you will need is an `apple_private.p8` RSA private key file, which we've pinned in the backend Slack channel. Put this in `flick-backend/src/flick` so that Apple Access Tokens can be verified.

## Run

Because this is a Django, RabbitMQ, Celery, PostgreSQL application, the backend is containerized and orchestrated with [Docker](https://www.docker.com/get-started) and Docker Swarm. Before we start, download [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

Depending on if you are running in development mode or production mode, update `.env` with `DEBUG=1` for the former and `DEBUG=0` for the latter. Note that production mode will include things like checking against Facebook tokens, which will make it difficult to use in development.

You may encounter an error with a celery worker exiting out with 137 error code. This simply means that there is a memory cap on the Docker settings on your computer, and you can update increase this in Docker > Preferences > Advanced > Memory. You may also need to increase the Swap size.

### Compose

The app can be run in development mode using Django's built in web server with (not cached)

```
docker-compose up --build
```

and if you want to be speedy and use the last built containers (cached), you can use

```
docker-compose up
```

To remove all containers in the cluster use

```
docker-compose down
```

To run the app in production mode, using gunicorn as a web server and nginx as a proxy, use

```
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml down
```

You can check running containers with

```
docker ps
```

And you can completely clear cached Docker images with

```
docker system prune -a
```

It's recommended to run the `prune` command every so often because Docker likes to cache things, and you may not be getting the container you are expecting.

### Swarm

We can also use the same `docker-compose.yaml` files to run the services using Docker Swarm, which enables the creation of multi-container clusters running in a multi-host environment with inter-service communication across hosts via overlay networks.

```
docker swarm init --advertise-addr 127.0.0.1:2377
docker stack deploy -c docker-compose.yaml -c docker-compose.prod.yaml proj
```

It should be noted that the app will not be accessible via `localhost` in Chrome/Chromium.
Instead use `127.0.0.1` in Chrome/Chromium.

To bring down the project or stack and remove the host from the swarm

```
docker stack rm proj
docker swarm leave --force
```

## Description

The setup here defines distinct development and production environments for the app. Running the app using Django's built in web server with `DEBUG=True` allows for quick and easy development; however, relying on Django's web server in a production environment is discouraged in the Django docs for security reasons. Additionally, serving large files in production should be handled by a proxy such as nginx to prevent the app from blocking.

## Style

The `requirements.txt` already includes the pre-commit formatting, so making commits in your virtual environment will ensure that your code is formatted by [black](https://github.com/psf/black) standards.
