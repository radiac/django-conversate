=======================================
Conversate - Persistent chat for Django
=======================================

A simple lightweight persistent chat app for Django sites, where users may not
always be around at the same time.

Requiring nothing other than a working Django installation, messages can be
left for users to pick up later, users can opt in to receive e-mail alerts of
activity when they are away, and real-time conversations are supported through
simple polling so it will work through the most restrictive of firewalls.


Features
========

* Admins create rooms and add users to them
* Messages are stored in the database
* Full history is available to all users of that room
* File upload support
* Simple jquery-based polling for real-time updates
* Users can opt in to receive e-mail alerts of activity when away
* Support for users without javascript

Supports Django 2.2+, on Python 3.6+.

* See `CHANGES <CHANGES>`_ for full changelog and roadmap
* See `UPGRADE <UPGRADE.rst>`_ for how to upgrade from earlier releases

Please note: this is designed for small groups to have infrequent conversations
which are often asynchronous; because each poll event will create a new HTTP
connection, installations where a large number of concurrent users are expected
should look for a different solution involving long-polling and websockets.

There is an example site in the ``example`` directory.


Installation
============

1. Install ``django-conversate`` (currently only on github)::

    pip install -e git+https://github.com/radiac/django-conversate.git#egg=django-conversate

   Note: The master branch may sometimes contain minor changes made since the
   version was incremented. These changes will be listed in
   `CHANGES <CHANGES>`_. It will always be safe to use, but versions will be
   tagged if you only want to follow releases.

2. Add Conversate to ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'conversate',
    )

   You may also want to change some settings here (see `Settings`_ below)

3. Include the URLconf in your project's urls.py::

    url(r'^conversate/', include('conversate.urls', namespace='conversate')),

4. Make sure your ``base.html`` template has the necessary blocks, or override
   Conversate's base, ``conversate/base.html`` (see `Templates`_ below). You
   will also want to create a link somewhere to ``conversate-index`` (or
   ``conversate.views.index``) so users can access it.

5. Add the models to the database::

    python manage.py migrate conversate


Settings
--------

Add these settings to your ``settings.py`` file to override the defaults.

``CONVERSATE_PAGE_SIZE``
    Number of lines to show on a page

    Default: ``100``

``CONVERSATE_IDLE_AT``:
    The time until the UI decides that the user is idle (in ms)

    Default: ``60*1000``

``CONVERSATE_POLL_MIN``:
    Minimum poll interval (in ms)

    Default: ``5 * 1000``

``CONVERSATE_POLL_MAX``:
    Maximum poll interval (in ms)

    Default: ``60 * 1000``

``CONVERSATE_POLL_STEP``:
    Amount to increase poll interval by when there is no activity (in ms)

    Default: ``5 * 1000``

``CONVERSATE_CONTROL_LAYOUT``:
    If True, Conversate's JavaScript will control the layout:
    * changes the container element to position:relative and padding:0
    * maximises container element's height into available space in the window
    * makes the conversation scroll in place
    * moves the input field to the bottom of the container

    Default: ``True``

``CONVERSATE_DISCONNECT_AT``:
    How long before marking the user as disconnected (in secs)

    Defaults to POLL_MAX plus 30 seconds, `os.path.join(BASE_DIR, "..", "private")`60 + 30````

``CONVERSATE_EMAIL_FROM``:
    From address for alert e-mails

    Default: ``DEFAULT_FROM_EMAIL`` (from main Django settings)

``CONVERSATE_STORE_ROOT``:
    Path to dir where uploaded files are stored.

    This should not be publicly accessible otherwise files could be downloaded without
    permission. The default value is the media root so that it works out of the box, but
    this is insecure as permission checks can be bypassed.

    Example: ``os.path.join(BASE_DIR, "..", "private")``

    Default: ``MEDIA_ROOT``


Templates and styles
--------------------

The Conversate templates extend ``conversate/base.html``, which in turn extends
``base.html``. The templates use HTML5 elements.

They will expect the following blocks:

* ``js`` for inserting JavaScript
* ``css`` for inserting CSS
* ``title`` for inserting the title (plain text) - or ``{{ title }}`` instead
* ``content`` for the body content

You will need to add these to your ``base.html`` template. Alternatively, if
you already have the blocks but with different names, create
``conversate/base.html`` in your own templates folder and map them; for
example::

    {% block script %}
        {{ block.super }}
        {% block js %}{% endblock %}
    {% endblock %}

Once you have mapped these blocks, the default settings and templates should
work out of the box with most designs. However, the conversate container
element in your site's base template should be given a fixed height and width
to contain the chat interface.

There is a single global JavaScript variable used, ``CONVERSATE``, which the
template uses to pass settings and variables to the JavaScript.


Usage
=====

Set up one or more rooms in the Django admin site, and the rooms will be listed
for your users on the conversate index page.

Users can double-click the poll timer to force a faster poll.


Credits
=======

Thanks to all contributors, who are listed in CHANGES.

This project includes bundled JavaScript dependencies.
