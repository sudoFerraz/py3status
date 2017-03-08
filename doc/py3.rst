.. _py3:

py3 module helper
=================

Py3 is a special helper object that gets injected into
py3status modules, providing extra functionality.
A module can access it via the ``self.py3`` instance attribute
of its py3status class.


Constants
---------

.. include:: py3-constants-info.inc


.. _COLOR_\<VALUE\>:

.. py:attribute:: COLOR_\<VALUE\>

This will have the value of the requested color as defined by the user config.
eg ``COLOR_GOOD`` will have the value ``color_good`` that the user had in their
config.  This may have been defined in the modules config, that of a container
or the general section.

Custom colors like ``COLOR_CHARGING`` can be used and are setable by the user in
their ``i3status.conf`` just like any other color.  If the color is undefined
then it will be the default color value.


Exceptions
----------

.. include:: py3-exceptions-info.inc

Methods
-------

.. include:: py3-methods-info.inc
