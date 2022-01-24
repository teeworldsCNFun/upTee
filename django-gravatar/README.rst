===============
django-gravatar
===============

.. image:: http://stillmaintained.com/nvie/django-gravatar.png

`django-gravatar` makes it easy to add Gravatar support to your Django
application through the addition of a template tag.


*******
History
*******

This code was taken from http://django-gravatar.googlecode.com, but it
was superseded by the https://github.com/ericflo/django-avatar package,
which provides a way more general approach to avatars in Django (not
Gravatar-specific, with local Django caching).

If, however, you want to stick to a Gravatar-only solution, this package
may a bit more "lightweight" and easier to start using.


************
Installation
************

To install it, use pip::

    pip install django-gravatar


*****
Usage
*****

To use it with a Django installation, first place 'gravatar' in the
``INSTALLED_APPS`` tuple of your settings.py file like so::

    INSTALLED_APPS = (
        # ...
        'gravatar',
    )

Here is sample usage in a template::

    {% load gravatar %}
    {% gravatar_for_user request.user 40 g %}

In the previous example, a gravatar will be displayed for the specified
user at a size of 40 pixels square with a rating of 'g'.  The second and
third arguments are optional and if not supplied the gravatar image will 
be 80 pixels square, the default gravatar image size, and will carry a
rating of 'g', the default gravatar rating.

In addition to supplying a user object, you can also provide a username as
a string.  For instance::

    {% gravatar_for_user 'jtauber' %}

Or by email::

    {% gravatar_for_email 'someone@example.com' %}

It is possible to get the url wrapped in an html img tag::

    {% gravatar_img_for_email 'someone@example.com' %}
    {% gravatar_img_for_user request.user %}
    {% gravatar_img_for_user 'jtauber' %}

If you only want the URL and not the full blown ``img`-tag, you can use the
following functions::

    {% gravatar_for_email 'someone@example.com' %}
    {% gravatar_for_user request.user %}
    {% gravatar_for_user 'jtauber' %}

If you want the gravatar profile in json decoded format,  you can use the 
following functions::

    {% gravatar_profile_for_email 'someone@example.com' %}
    {% gravatar_profile_for_user request.user %}
    {% gravatar_profile_for_user 'jtauber' %}

There are a few configuration variables available that you can use in your
Django's ``settings.py``:

- **GRAVATAR_URL_PREFIX**: The gravatar URL to use. Default:
  ``'http://www.gravatar.com/'``
- **GRAVATAR_DEFAULT_IMAGE**: The default image to use. Default: ``''``. See
  http://en.gravatar.com/site/implement/images/#default-image
- **GRAVATAR_DEFAULT_RATING**: The default rating to use. Default: ``'g'``. See
  http://en.gravatar.com/site/implement/images/#rating
- **GRAVATAR_DEFAULT_SIZE**: The default size to use. Default: ``80``. See
  http://en.gravatar.com/site/implement/images/#size
- **GRAVATAR_IMG_CLASS**: The default CSS class name to add to generated
  ``<img>``-tags. Default: ``'gravatar'``.

