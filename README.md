# TSOJ

Tonbridge School Online Judge

## Build instructions

Add `SECRET_KEY` to the environment by creating a file called `.env` in the root folder and adding this:

    SECRET_KEY="dev"  # can be whatever
   
  Run `pip install -r requirements.txt`.

Start the server by running the `wsgi.py` file.

## MongoDB Server

In `.env`, add a line: `MONGO_URI=<connection-string>`
Remember to put database name (`dev` if for development, `prod` if for production) in the connection string, after the last `/`.

## Setting up email verification

1. Go to [Account Security](https://myaccount.google.com/u/0/security)
2. Enable 2FA
3. Go to [App Passwords](https://myaccount.google.com/u/0/apppasswords)
4. Select app `Other` and select device `Other` and click `Generate`
5. Copy the password and paste into `.env` as `GMAIL_APP_PWD`
6. Put the email address into `.env` as `GMAIL_EMAIL`

Or more convienienty, use this (cause you don't really need to create a new email address for testing)
Email: tsojauth@gmail.com
App pwd: pxezvdeozcdfslbr

## Defining base url

Add `BASE_URL` into `.env` (eg. http://127.0.0.1:5000)

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

