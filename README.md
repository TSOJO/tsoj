
# TSOJ

Tonbridge School Online Judge

## Build instructions

Add `SECRET_KEY` to the environment by creating a file called `.env` in the root folder and adding this:

    SECRET_KEY="dev"  # can be whatever
   
  Run `pip install -r requirements.txt`.

Start the server by running the `wsgi.py` file.

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
