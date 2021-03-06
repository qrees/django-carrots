======================
Introduction to Django
======================


What is Django?
===============

So far we have been learning about Python. Python is just a language (and a set of basic libraries)
that allows you to create programs. Creating an interactive website in Python requires a huge amount
of work, which is why we will use the Django framework instead. Django gives us a set of tools, features (like the functions we
learned about earlier, but more complex), and classes that facilitate the creation of websites.

In order to obtain a fully interactive website we need a few items:

* Application server - where we use Django
* HTML and CSS files - responsible for the appearance of the website
* Databases - to store survey questions and answers

We will start by creating an application server.

Creation of the new project
===========================

Installation
------------

Install Django by running it on the console ``pip install django==3.0.3``:

.. code-block:: sh

    (workshops) ~$ pip install django==3.0.3
    Collecting django
      Downloading Django-3.0.3-py3-none-any.whl (7.5 MB)
    ...
    Installing collected packages: ..., django
    Successfully installed ...

A suitable package will be downloaded from `PyPI <https://pypi.org>`_ - a package repository 
where you can find many useful libraries.


Beginning of project
--------------------

Django provides the administrative script ``django-admin.py``. It allows you to create the basic scheme of our
site.

To create a new project with the site, launch ``django-admin.py startproject carrots``:

.. code-block:: sh

    # Linux

    (workshops) ~$ django-admin.py startproject carrots
    (workshops) ~$ tree carrots
    carrots/
    ├── carrots
    │   ├── asgi.py
    |   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── manage.py

    1 directory, 5 files


.. code-block:: bat

    :: Windows

    (workshops) C:\Users\TeddyBear> python -m django-admin startproject carrots
    (workshops) C:\Users\TeddyBear> tree /f carrots
    Folder PATH listing
    Volume serial number is 00FA-07FF
    C:\USERS\TEDDYBEAR\DOCUMENTS\CARROTS
    │   manage.py
    │
    └───carrots
            asgi.py
            __init__.py
            settings.py
            urls.py
            wsgi.py


Structure of project
--------------------

The newly created project contains a "carrots" directory and some basic files.

The file ``carrots/settings.py`` includes the settings such as the language, a database, and installed
applications. We can edit the file ourselves. Inside, you will find the default settings and
explanatory comments.


The file ``manage.py`` allows us to administer the web site, create or clear the database, run a simple
application server, etc. We will learn how to use it later on.


The file ``carrots/urls.py`` contains information about the paths in the site.

Other files are less interesting. Usually we do not look inside them at all nor do we modify them. If you are curious,
you can find more information through Google.

Settings of application
-----------------------

In the ``carrots/settings.py`` file, find ``TIME_ZONE`` and set time zone as Warsaw. You should get the following:
::

    TIME_ZONE = 'Europe/Luxembourg'

    LANGUAGE_CODE = 'en-GB'


To make it simpler we also exclude the advanced support for time zones in the database - it will not be needed in our project.
In the file ``settings.py`` please find  ``USE_TZ``  and set it as False:
::

    USE_TZ = False

..
.. ``INSTALLED_APPS`` zawiera informację o zainstalowanych aplikacjach. Projekty ``Django``
.. składają się z wielu aplikacji, w tym wypadku są to na przykład aplikacje: ``auth`` do
.. uwierzytelniania użytkowników, ``sessions`` do zarządzania sesją użytkownika itd.

..
.. Jak widać, ``INSTALLED_APPS`` jest po prostu krotką zawierającą napisy. Odkomentowanie
.. dwóch ostatnich napisów włączy aplikację do administracji. Później będziemy jej używać.

Database
--------

Now it's time to use the previously described file ``manage.py`` to create the database. For this purpose we execute the option ``migrate``. In the project directory run ``python manage.py migrate``:

.. code-block:: sh

    (workshops) ~$ cd carrots
    (workshops) ~/carrots$ python manage.py migrate
    Operations to perform:
      Apply all migrations: admin, auth, contenttypes, sessions
    Running migrations:
      Applying contenttypes.0001_initial... OK
      Applying auth.0001_initial... OK
      Applying admin.0001_initial... OK
      Applying admin.0002_logentry_remove_auto_add... OK
      Applying admin.0003_logentry_add_action_flag_choices... OK
      Applying contenttypes.0002_remove_content_type_name... OK
      Applying auth.0002_alter_permission_name_max_length... OK
      Applying auth.0003_alter_user_email_max_length... OK
      Applying auth.0004_alter_user_username_opts... OK
      Applying auth.0005_alter_user_last_login_null... OK
      Applying auth.0006_require_contenttypes_0002... OK
      Applying auth.0007_alter_validators_add_error_messages... OK
      Applying auth.0008_alter_user_username_max_length... OK
      Applying auth.0009_alter_user_last_name_max_length... OK
      Applying auth.0010_alter_group_name_max_length... OK
      Applying auth.0011_update_proxy_permissions... OK
      Applying sessions.0001_initial... OK

You just installed Django's system base, which means you have empty tables in your database and have no administrators (administration accounts aka admins or superusers) defined. Let's create one by running ``python manage.py createsuperuser``:

.. code-block:: sh

    (workshops) ~/carrots$ python manage.py createsuperuser
    Username (leave blank to use 'teddybear'): beans
    Email address: admin@example.com
    Password: 
    Password (again):
    Superuser created successfully.

If all goes well, Django will ask you to provide data for the administrator account. You may leave the username 
as it is proposed, and you may give any e-mail address. Memorize the data you provided (i.e, username 
and password) so that you can log in to the control panel. In the above example, the user will be ``beans``.

If you want to learn more about ``manage.py``, run python ``manage.py help``:

.. code-block:: sh

    (workshops) ~/carrots$ python manage.py help

 You will get a list of all commands and options supported by ``manage.py``. 

To get help on a single command, run  ``manage.py help`` command:

.. code-block:: sh

    (workshops) ~/carrots$ python manage.py help migrate

Administration interface
------------------------

Now we can run our application. Run the server by typing ``python manage.py runserver``:

.. code-block:: sh

    (workshops) ~/carrots$ python manage.py runserver
    Watching for file changes with StatReloader
    Performing system checks...

    System check identified no issues (0 silenced).
    February 20, 2020 - 01:50:36
    Django version 3.0.3, using settings 'carrots.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

Our website will be available at ``http://127.0.0.1:8000/`` or ``http://localhost:8000/``

The administration panel is available in the ``admin/`` path, that’s why we will go to 
``http://localhost:8000/admin/`` to find it.


We create a new application for questionnaires
----------------------------------------------

For now, we have created the project ``carrots``. Projects in Django are divided into apps that provide
specific functions.

We want to publish questionnaires on our website, so we will add the application ``polls``.

Quit the server and from the command line, type ``python manage.py startapp polls``:

::

    (workshops) ~/carrots$ python manage.py startapp polls
    (workshops) ~/carrots$ tree .
    .
    ├── carrots
    │   ├── asgi.py
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── db.sqlite3
    ├── manage.py
    └── polls
        ├── admin.py
        ├── apps.py
        ├── __init__.py
        ├── migrations
        │   └── __init__.py
        ├── models.py
        ├── tests.py
        └── views.py

    4 directories, 16 files

After creating the application, it must be activated in our project. In the file ``carrots/settings.py``
we have to add the application ``polls`` to ``INSTALLED_APPS``. The result should look like this::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'polls',
    )

Applications in ``Django`` consists of several files:

* ``apps.py`` - definitions for the application configuration,
* ``admin.py`` - definitions for the administration panel,
* ``models.py`` - definitions of the models for the database,
* ``tests.py`` - testing applications,
* ``views.py`` - views of the application.

Summary
-------

Django installation:

.. code-block:: sh

    (workshops) ~$ pip install django==3.0.3

Project directory creation:

.. code-block:: sh

    # Linux

    (workshops) ~$ django-admin.py startproject carrots


.. code-block:: bat

    :: Windows

    (workshops) C:\Users\TeddyBear> python -m django-admin startproject carrots

Setup of time zone in ``carrots/settings.py`` file::

    TIME_ZONE = 'Europe/Luxembourg'

    LANGUAGE_CODE = 'en-GB'

    USE_TZ = False

Creation of database (you need to run that command after adding every new model):

.. code-block:: sh

    (workshops) ~/carrots$ python manage.py migrate

Server start-up:

.. code-block:: sh

    (workshops) ~/carrots$ python manage.py runserver

Creation of the new application named ``polls``:

.. code-block:: sh

    (workshops) ~/carrots$ python manage.py startapp polls

Just remember that after creating an application you should add it to ``INSTALLED_APPS``.
