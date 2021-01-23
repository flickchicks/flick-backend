# flick-backend

A Django, RabbitMQ, Celery, PostgreSQL backend for the iOS and Android Flick app that handles users, lists, and movies.

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

You will also need the private key files `apple_private.p8` (verify Apple Access Tokens during authentication) and `aps.pem` (connect with APNS to send push notifications to iOS devices) which we've pinned in the backend Slack channel. Put these in `flick-backend/src/flick` so that the settings can be properly configured.

## Run

Because this is a Django, RabbitMQ, Celery, PostgreSQL application, the backend is containerized and orchestrated with [Docker](https://www.docker.com/get-started) and Docker Swarm. Before we start, download [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/). Once you've installed Docker, check that it is running by seeing if there is a whale at the top menu toolbar with `Docker Desktop is running`.

Depending on if you are running in development mode or production mode, update `.env` with `DEBUG=1` for the former and `DEBUG=0` for the latter. Note that production mode will include things like checking against Facebook tokens, which will make it difficult to use in development.

You may encounter an error with a celery worker exiting out with 137 error code. This simply means that there is a memory cap on the Docker settings on your computer, and you can increase the allowed memory allocation to containers in `Docker > Preferences > Advanced > Memory`. You may also need to increase the Swap size.

You may also encounter migrations issues (likely once you make the transition from `db.sqlite3` to PostgreSQL), and you can run the following two commands to clear migrations in `flick-backend/src/flick`:

```
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
```

Before we go into the proper ways of running the backend, here's a quick way to run locally for development purposes:

1. Update `.env` with `SQLITE3=1`
2. Create a virtual environment

```
flick-backend/src/flick> $ python3 -m pip install virtualenv
flick-backend/src/flick> $ virtualenv venv
flick-backend/src/flick> $ . venv/bin/activate
flick-backend/src/flick> (venv) $ python3 -m pip install -r requirements.txt
```

3. Install RabbitMQ

```
brew update
brew install rabbitmq
```

4. Start RabbitMQ
   To run in the foreground,

```
rabbitmq-server
```

To run in the background,

```
brew services start rabbitmq
```

5. Start Celery worker

```
flick-backend/src/flick> (venv) $ celery -A flick worker -l info
```

6. Set up `db.sqlite3` database

```
flick-backend/src/flick> (venv) $ python3 manage.py makemigrations
flick-backend/src/flick> (venv) $ python3 manage.py migrate
```

6. Run Django development server

```
flick-backend/src/flick> (venv) $ python3 manage.py runserver
```

7. Visit `http://localhost:8000/admin/`
8. (Optional) Create superuser to log into `/admin/`

```
flick-backend/src/flick> (venv) $ python3 manage.py createsuperuser
```

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
In the case that you'd like to create a username and password to log into `/admin`, you can also access the Django shell of the running container with

```

docker exec -it app sh

```

where `app` is the name of the Django container, and you can then type the usual command in the shell

```

python3 manage.py createsuperuser

```

### Swarm

We can also use the same `docker-compose.yaml` files to run the services using Docker Swarm, which enables the creation of multi-container clusters running in a multi-host environment with inter-service communication across hosts via overlay networks.

```

docker swarm init --advertise-addr 127.0.0.1:2377
docker stack deploy -c docker-compose.yaml -c docker-compose.prod.yaml proj

```

It should be noted that the app will not be accessible via `localhost` in Chrome. Instead use `127.0.0.1` in Chrome.

To bring down the project or stack and remove the host from the swarm

```

docker stack rm proj
docker swarm leave --force

```

## Description

The setup here defines distinct development and production environments for the app. Running the app using Django's built in web server with `DEBUG=True` allows for quick and easy development; however, relying on Django's web server in a production environment is discouraged in the Django docs for security reasons. Additionally, serving large files in production should be handled by a proxy such as nginx to prevent the app from blocking.

## Style

The `requirements.txt` already includes the pre-commit formatting, so making commits in your virtual environment will ensure that your code is formatted by [black](https://github.com/psf/black) standards.

```

```
