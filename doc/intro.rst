Introduction
============

Using py3status, you can take control of your i3bar easily by:

* using one of the available :ref:`modules` shipped with py3status
* grouping multiple modules and automatically or manually cycle their
  display
* writing your own modules and have their output displayed on your bar
* handling click events on your i3bar and play with them in no time
* seeing your clock tick every second whatever your i3status interval

No extra configuration file needed, just install & enjoy!

About
-----

You will love py3status if you're using `i3wm
<http://i3wm.org>`_ and are frustrated by the i3status
limitations on your i3bar such as:

* you cannot hack into it easily
* you want more than the built-in modules and their limited configuration
* you cannot pipe the result of one of more scripts or commands in
  your bar easily

Philosophy
----------

* no added configuration file, use the standard i3status.conf
* rely on i3status' strengths and its existing configuration
  as much as possible
* be extensible, it must be easy for users to add their own
  stuff/output by writing a simple python class which will be loaded
  and executed dynamically
* easily allow interactivity with the i3bar
* add some built-in enhancement/transformation of basic i3status
  modules output
* support python 2.7 and python 3.x

Installation
------------

+-------------------+-----------------------------+-----------------------------------------+
|Distro             |Helpful Command              |Useful Note                              |
+===================+=============================+=========================================+
|**Arch Linux**     |``$ pacaur -S py3status``    |Stable updates. Official releases.       |
+                   +-----------------------------+-----------------------------------------+
|                   |``$ pacaur -S py3status-git``|Hot updates. Directly from master branch.|
+-------------------+-----------------------------+-----------------------------------------+
|**Debian & Ubuntu**|``$ pypi-install py3status`` |Usually in `python-stdeb` package.       |
+-------------------+-----------------------------+-----------------------------------------+
|**Fedora**         |``$ dnf install py3status``  |                                         |
+-------------------+-----------------------------+-----------------------------------------+
|**Gentoo Linux**   |``$ emerge -a py3status``    |                                         |
+-------------------+-----------------------------+-----------------------------------------+
|**Pypi**           |``$ pip install py3status``  |                                         |
+-------------------+-----------------------------+-----------------------------------------+

Installation Note: This list is incomplete. Please help us fill in the gaps.

Support
-------

Get help, share ideas or feedbacks, join community, report bugs, or others, see:

Github
^^^^^^

`Issues <https://github.com/ultrabug/py3status/issues>`_ /
`Pull requests <https://github.com/ultrabug/py3status/pulls>`_

Live IRC Chat
^^^^^^^^^^^^^


Visit `#py3status <https://webchat.freenode.net/?channels=%23py3status&uio=d4>`_
at `frenode.net <https://freenode.net>`_
