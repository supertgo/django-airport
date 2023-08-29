# amo-promo-dev-challenge

I've chose to use python language with Django framework

- `airport/`: This directory contains modules related to airports.
    - `airport/`: This directory contains modules related to airports.
    
    - `airport/`: This directory represents the main application.
      - `__pycache__/`: Cache directory for compiled Python files (automatically generated).
        - `__init__.py`: Initialization file for the main application.
        - `asgi.py`: ASGI configuration for the application.
        - `settings.py`: Application-specific settings.
        - `urls.py`: URL routing for the application's endpoints.
        - `wsgi.py`: WSGI configuration for the application.

    - `app_api/`: Contains modules related to API functionality.
      - `__init__.py`: Initialization file for the `app_api` package.
      - `admin.py`: Admin configuration for API models.
      - `apps.py`: Configuration for the API app.
      - `consts.py`: Constants specific to the API.
      - `serializer.py`: Serializers for API data.
      - `tests.py`: Test cases for API functionality.
      - `urls.py`: URL routing for API endpoints.
      - `utils.py`: Utility functions for the API.
      - `views.py`: View functions for API views.
      - `viewsets.py`: Viewsets for API resources.
    - `app_core/`: Contains modules related to core functionality.
      - `__pycache__/`: Cache directory for compiled Python files (automatically generated).
      - `management/`: Management commands for the app (if applicable).
      - `migrations/`: Database migration files (if using a database).
      - `utils/`: Contains utility modules for the core functionality.
        - `__init__.py`: Initialization file for the `utils` package.
        - `admin.py`: Admin configuration for core models.
        - `apps.py`: Configuration for the core app.
        - `models.py`: Models for the core functionality.
        - `tests.py`: Test cases for the core functionality.
        - `views.py`: View functions for core views.
        - `works.py`: Additional modules related to core functionality.

- `__init__.py`, `asgi.py`, `settings.py`, `urls.py`, `wsgi.py`: Django project configuration files.


## Challenge 1
To solve the first challenge, i've just followed the instructions on Django documentation https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/ and created a file called `import_airports`, you can run:

`python manage.py import_airports`

So we can create a routine with a job scheduler and call it daily as the challenge suggests.


![image](https://github.com/supertgo/amo-promo-dev-challenge/assets/47607913/49a8f229-8f4f-4800-9c9b-faada8bf088c)

The output of the django-admin command is like the one above, if completed successfully

![image](https://github.com/supertgo/amo-promo-dev-challenge/assets/47607913/35c0cd8d-da9a-4ee6-b53d-8f0d0ba7bb37)


If there is an error, the output is red.


## Technologies

Django - https://www.djangoproject.com/ with  https://www.sqlite.org/index.html as DBMS
