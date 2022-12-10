# TSOJ

Tonbridge School Online Judge

## Installation instructions
Download [docker](https://docs.docker.com/get-docker/).

Run the following:
- `pip install -r requirements.txt`.
- `docker run -p 6379:6379 --name tsoj-redis -d redis`

## Run server instructions

Open three terminals, each running the following:
- `python wsgi.py`
- `celery -A website.celery_tasks worker --loglevel=INFO`
- `celery -A website.celery_tasks flower`

Visit website at `localhost:5000`
Visit celery monitor at `localhost:5555`

In `.env`, add a line: `MONGO_URI=<connection-string>`
Remember to put database name (`dev` if for development, `prod` if for production) in the connection string, after the last `/`.

## Setting up email verification

See [.env configuration](#env-configuration) for a email address you can use without all the setup

1. Go to [Account Security](https://myaccount.google.com/u/0/security)
2. Enable 2FA
3. Go to [App Passwords](https://myaccount.google.com/u/0/apppasswords)
4. Select app `Other` and select device `Other` and click `Generate`
5. Copy the password and paste into `.env` as `GMAIL_APP_PWD`
6. Put the email address into `.env` as `GMAIL_EMAIL`

## .env configuration

	SECRET_KEY="dev"  # can be whatever
	MONGO_URI=<connection-string> # Remember to put database name (tsoj) in the connection string, after the last `/`.
	GMAIL_EMAIL=tsojauth@gmail.com
	GMAIL_APP_PWD=pxezvdeozcdfslbr
	BASE_URL = 'http://127.0.0.1:5000'
	CELERY_BROKER_URL = 'redis://127.0.0.1:6379' # the port is the one you set up in docker
	CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'

## Typings

(In visual studio code): Press F1, select `Python: Select Linter`, select `mypy`

## Project structure
This is strictly provisional and will be changed in the future.
```
/website
	/static
		script.js
		style.css
	/templates
		base.html  # base html template
		problem.html  # for problem
		404.html
	__init__.py  # app initialisation
	errors.py  # error handling
	problem.py  # blueprint for problem
config.py
wsgi.py
```
## Todo

 - [ ] Work out connection to backend
	 - [x] Hardcode `Problem 1` so can test
 - [ ] Ask JER what dashboard should look like
 - [ ] Build database for users and problems
 - [ ] Add more pages to website
	 - [ ] Home
	 - [ ] Problem listing
	 - [ ] Homework(?)
	 - [ ] Profile(?)
	 - [ ] Dashboard for teachers

## Updating submodules
Run `git submodule update --init --force --remote`.

## Activate venv in WSL
Run `source venv/bin/activate`.

