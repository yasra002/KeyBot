KeyBot: a utility to manage users and key access to boxes
=========================================================

This utility aims to solve creating and maintaining multiple linux boxes by consolidating user definitions to one place where they can be defined and updated. 
KeyBot is broken into the reusable classes that can be used for other projects or easily expanded for changing demands and the main utility that runs and does the management.
The pieces were built to be modular enough to be able to fit into most server environments: anything from Docker deploys to cloud servers or physical boxes.
Minimal impact on system requirements were aimed for to keep things as slim as possible.

Requirements to run

* Must run as root/sudo
* Needs ```python-libuser```, ```python-enum34```, and ```python-requests```
* Needs a gitlab token to access user data on gitlab. If it's not an admin token, it will not be able to fetch keys, but it can still set up the rest.

The environment variable ```KEYBOT_RUN_TESTS``` can be set in order to run some quick tests to make sure the basics are running. 
Not suggested to run on actual box, but in Docker or disposable environment.

The included Dockerfile can be used for testing as well as a template for basic server setup. 

Run ```main.py``` with ```-h``` in order to see any configuration options.
