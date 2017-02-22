#!/bin/python
# -*- coding: utf8 -*-
# -*- coding: cp850 -*
from stem import CircStatus
from stem.control import Controller
import geoip2.database

reader = geoip2.database.Reader('/root/docs/GeoLite2-City.mmdb')

with Controller.from_port(port = 9051) as controller:
    controller.authenticate()
    controller.new_circuit()
