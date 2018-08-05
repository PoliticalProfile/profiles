Political Profile - BR
========================

This project aims to fetch, digest, clean and organize all the information related to the congressman in the Brazilian Chamber of deputies.

Requirements
------------
* Python 3.7
* Django 2.0.7

Instructions
------------  
Go into the project directory:

    cd <project_name>

Copy the sample.env file to the project root:

    cp contrib/sample.env .env
    
Install all the dependencies:

    pip install -r requirements/dev.txt
    
Run celery:

    python -m celery -A political_profile worker -B -Q fetch -l info
    
Run Django server:

    python manage.py runserver
    
Known Issues
------------
None so far :)
