#!/usr/bin/python3
import sys
import os

here = os.path.dirname(__file__)
print(here)
sys.path.insert(0, here)

from catalog import app as application
application.secret_key = 'my_secret_key_wsgi'
