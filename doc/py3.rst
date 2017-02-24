.. _py3:

py3
===

.. autoclass:: py3status.py3.Py3
   :members:

Constants
^^^^^^^^^

The ``py3`` object also contains some special constants.

**CACHE_FOREVER**

If this is returned as the value for ``cached_until`` then the module will not be
updated. This is useful for static modules and ones updating asynchronously.

**COLOR_<VALUE>**

Introduced in py3status version 3.1

This will have the value of the requested color as defined by the user config.
eg ``COLOR_GOOD`` will have the value ``color_good`` that the user had in their
config.  This may have been defined in the modules config, that of a container
or the general section.

Custom colors like ``COLOR_CHARGING`` can be used and are set-able by the user in
their ``i3status.conf`` just like any other color.  If the color is undefined
then it will be the default color value.
