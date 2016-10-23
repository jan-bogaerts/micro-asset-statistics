__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"


import requests
import json
import credentials

with open("definitions/gsm_pressence.json") as file:
    code = file.read()
    r = requests.put("http://attrdproduction.westeurope.cloudapp.azure.com:2000/definition", data=code)
    print(r.status_code, r.reason, r.content)