lp_cli
======

CLI utils for Launchpad.

Now lp_cli.py can only comment bugs on Launchpad and change it's status.

Configuration
-------------

There are some environment variables can be exported for define parameters:

- ``BROWSER`` - define browser that will be executed for authorization. You can
  use, for example, ``links2`` or ``w3m`` as a browser on the machine w/o X;
- ``LAUNCHPAD_CACHE_DIR`` - path to Launchpad cache directory;
- ``LAUNCHPAD_CREDS_FILENAME`` - path to file to store Launchpad's credentials.


Command line paramaters
-----------------------

lp_cli.py <project> <command> [command parameters]

<project>  --- Launchpad project name. Uses for prevent errors at [command
parameters]. For example utility will stop changes on Launchpad if bug in
command parameters affects to other project.

Commenting
^^^^^^^^^^

lp_cli.py <project> comment <bug_id> <comment body>

For example:

lp_cli.py fuel comment 123456 "I want to
comment this
!!!!"

Change status
^^^^^^^^^^^^^

lp_cli.py <project> status <bug_id> "<new status name>"

For example:

lp_cli.py fuel comment 123456 "Fix Committed"
