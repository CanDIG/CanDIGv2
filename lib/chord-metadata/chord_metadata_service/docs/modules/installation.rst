Installation
============

1. Clone the project from github (use :code:`-r` to fetch submodules content)

.. code-block::

    git clone https://github.com/bento-platform/katsu.git


2. Install the git submodule for DATS JSON schemas (if did not clone recursively):

.. code-block::

    git submodule update --init

3. Create and activate a virtual environment

4. Move to the main directory and install required packages:

.. code-block::

    pip install -r requirements.txt

5. The service uses PostgreSQL database for data storage. Install PostgreSQL following `this tutorial <https://www.postgresql.org/docs/12/tutorial-install.html>`_.

6. Configure database connection in settings.py

e.g. settings if running database on localhost, default port for PostgreSQL is 5432:

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'database_name',
            'USER': 'user',
            'PASSWORD': 'password',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

7. From the main directory run (where the manage.py file located):

.. code-block::

    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

8. Development server runs at :code:`localhost:8000`
