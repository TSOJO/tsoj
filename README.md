


# TSOJ

Tonbridge School Online Judge

## Build instructions

Add `SECRET_KEY` to the environment by creating a file called `.env` in the root folder and adding this:

    SECRET_KEY="dev"  # can be whatever
   
  Run `pip install -r requirements.txt`.

Start the server by running the `wsgi.py` file.

## MySQL server

[Install](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-database#install-mysql) MySQL server in Linux (WSL).

If there's an error when running `sudo mysql_secure_installation` see https://stackoverflow.com/a/72115499/6085039.

Create `tsoj` database by running `CREATE DATABASE tsoj;`.

Add `DB_URI` to environment by adding the following to a `.env` file:
`DB_URI  =  'mysql://<user>:<password>@localhost/tsoj'`.

Run `sudo python3 wsgi.py`. A table `problem` should be created in the database `tsoj`.

Note to self:

 - Start/stop server: `sudo /etc/init.d/mysql start`
 - Login to monitor: `sudo mysql -u <username> -p`

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

