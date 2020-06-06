# flick-backend
Backend for flick app that handles users, lists, and movies.

# Setup
If running for the first time, run where `manage.py` is:
```
virtualenv venv
. venv/bin/activate
pip3 install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```
The development database file, sqlite3.db, should appear with the migrated models.

Ask Alanna for environment variables! 

To access Django admin, you will have to create an "account" for yourself as 
an administrator, so use this command and follow the prompts:
```
python manage.py createsuperuser
```

To help us manage asynchronous tasks, we use a Celery, and as a result, use
Redis as our cache for saving those future tasks. 
Ensure you have Redis installed and that your server is running:
```
brew install redis
brew services start redis
redis-cli ping
```
You should get `PONG` back!
Open the Redis server:
```
redis_server
```
Start the celery worker:
```
celery -A cfehome worker -l info
```
Now you should be able to run the backend with asynchronous tasks!
Our current use case with this is to upload images while we send the AWS S3
urls to the client.


# Run
To run the Django backend, run where `manage.py` is:
```
python manage.py runserver
```

# Style
The `requirements.txt` already includes the pre-commit formatting, so making
commits in your virtual environment will ensure that your code is formatted 
by [black](https://github.com/psf/black) standards

# Basic Endpoints
# **/admin** • GET
* user-friendly view of all data

# **/api/auth** • POST
* followed by `/register`, `/login`, `/logout`, `/me` 
* all authorization related content

