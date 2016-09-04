__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import logging
logging.getLogger().setLevel(logging.INFO)
from flask import Flask, render_template, Response, request
from flask.ext.api import status
import os
import json

#import att_event_engine.iotApplication as iotApp
import att_trusted_event_server.iotApplication as iotApp
from att_event_engine.att import Client
import credentials

app = Flask(__name__)
iot = iotApp.IotApplication(credentials.UserName, credentials.Pwd, credentials.Api, credentials.Broker, "statistition")

import rules

def registerEventsForDef(definition):
    """
    load the statistsc object for the definition, create the assets required for the statistics and register for
    topic events.
    :param definition:
    :return:
    """
    connection = Client()
    connection.connect(definition['username'], definition['pwd'])
    obj = rules.AssetStats(definition, connection)
    map(lambda x: x.createAssets(connection), obj.groups)  # make certain that all the assets have been created.
    obj.register()
    return obj

def loadAll():
    """
    loads al the known statistics defs from disc and registers them to monitor for incomming events
    :return:
    """
    files = [f for f in os.listdir('definitions') if os.path.isfile(os.path.join('definitions', f))]
    for file in files:
        registerEventsForDef(rules.loadDefinition(file))



def storeDef(name, value):
    """
    stores the definition on disk
    :param name: the name to use
    :param value: the value (string)
    :return:None
    """
    with open(os.path.join('definitions', name), 'w') as f:
        f.write(value)


@app.route('/definition', methods=['PUT'])
def addEvent():
    """
    called when a statistics definition needs to be added to the list
    :return: ok or error
    """
    try:
        data = json.loads(request.data)
        obj = registerEventsForDef(data)
        storeDef(obj.asset.id, request.data)
        return 'ok', status.HTTP_200_OK
    except  Exception as e:
        logging.exception("failed to store definition")
        return str(e), status.HTTP_405_METHOD_NOT_ALLOWED




try:
    loadAll()
    iot.run()
    if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=True, threaded=True, port=1000, use_reloader=False)  # blocking
except:
    logging.exception("failed to start statistician engine")