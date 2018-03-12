#!/usr/bin/python
import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/ClooneyWebServer/')

from server import app as application
application.secret_key = 'SuperSecretKey116236236ShhhhDontTellAnyone!'
