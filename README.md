# flask-admin-modal

Example, in response to this [StackOverflow](https://stackoverflow.com/q/47593195/2800058) question,
of using a Bootstrap modal popup to update multiple records selected in a Flask-Admin batch action.

![Popup Demo](flask-admin-modal.gif)

## Installation

```bash
git clone https://github.com/pjcunningham/flask-admin-modal.git
cd flask-admin-modal

# (optional, create a virtual environment)
virtualenv venv && source venv/bin/activate

# fetch dependencies; add '--user' if not using a virtualenv
pip install -r requirements.txt

# Set Flask environment variable e.g. Windows CMD
set FLASK_APP=run.py

# Create/Populate data
flask create-database

# launch app
flask run
```
