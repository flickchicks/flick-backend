# flick-backend
Backend for flick app that handles users, lists, and movies.

# Setup Virtual Environment
If running for the first time, run where `manage.py` is:
```
virtualenv venv
. venv/bin/activate
pip3 install -r requirements.txt
```

# Setup Environment Variables 
## With Slack
There is a `.env` file pinned in the backend channel of the Slack, and you
must put this file in the project.
There is also a `.aws.zip` file pinned, and you must unzip it and put it in your 
computer's home directory.

## Manually
For devs other than those on the Flick team, here is how you can set the
environment variables up.

Make sure to create your own `.env` file by running:
```
cp env.template .env
```
Make sure to create your own `.aws` credentials folder in your home directory 
(your computer's home directory, not in this project!), with two files 
`credentials` and `config` in them:

`~/.aws/credentials`:
```
[default]
aws_access_key_id=<YOUR_ACCESS_KEY_ID>
aws_secret_access_key=<YOUR_SECRET_ACCESS_KEY>
```
`~/.aws/config`:
```
[default]
region=us-east-1
```
The access key ID and secret access key can be found in the "Security 
Credentials" section of your AWS account.

# Setup Django
```
python manage.py makemigrations
python manage.py migrate
```
The development database file, sqlite3.db, should appear with the migrated models.

To access Django admin, you will have to create an "account" for yourself as 
an administrator, so use this command and follow the prompts:
```
python manage.py createsuperuser
```

# Setup Celery & Redis
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
by [black](https://github.com/psf/black) standards.

# API Spec
You can check out the work in progress [API spec here](https://stoplight.io/p/studio/gh/alanna-zhou/flick-backend)!
