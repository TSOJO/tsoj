# TSOJ

Tonbridge School Online Judge

## Installation instructions

Add `SECRET_KEY` to the environment by creating a file called `.env` in the root folder and adding this:

    SECRET_KEY="dev"  # can be whatever
   
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

## MongoDB Server

In `.env`, add a line: `MONGO_URI=<connection-string>`
Remember to put database name (`tsoj`) in the connection string, after the last `/`.

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

