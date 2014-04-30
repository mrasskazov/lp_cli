lp_cli
======

CLI utils for Launchpad.

Now lp_cli.py can only commenting bugs on Launchpad.

Environment variables
---------------------

There are some environment variables can be exported for define parameters:

- ``BROWSER`` - define browser that will be executed for authorization. You can
  use, for example, ``links2`` or ``w3m`` as a browser on the machine w/o X;
- ``LAUNCHPAD_CACHE_DIR`` - path to Launchpad cache directory;
- ``LAUNCHPAD_CREDS_FILENAME`` - path to file to store Launchpad's credentials.
