__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import math

from att_event_engine.resources import Sensor, Actuator, Virtual, Gateway, Parameter

class Statistician:
    """
    performs all the statistical calculations for a single asset.
    """

    def __init__(self, name, functions, resetEvery, asset):
        """
        create object
        :param functions: a list of 'function' objects that this statistician has to calculate when a value is changed
        :param asset: an Asset object or id string that this statistician should calculate values for.
        """
        if isinstance(asset, basestring):
            self._asset = Sensor(asset)                                 # we treat it as a sensor, could also be an actuator.
        else:
            self._asset = asset
        self._name = name                                               # the name of the statistical group.
        self._functions = {}
        self.resetEvery = resetEvery                                    # so we can restart the timer.
        for function in functions:
            name = function['function']
            self._functions[function['function']] = function
            if name == "std":                                           # for std, we need avg
                if "avg" not in self._functions:
                    name = 'avg'                                        # change the name to avg so the next if works: for avg, we also need count.
                    self._functions[name] = None
            # this is correct: for std, we need avg and count
            if name == "avg" and "count" not in self._functions:        # if we need avg, then we need count to get the avg right.
                self._functions['count'] = None


    def createAssets(self, context):
        """
        creates the assets that represent the values of the statistical functions.
        :param device: the device object or id to attach the assets too.
        :return: None
        """
        if 'count' in self._functions:
            Virtual.create(context, self.getAssetName('count'), self._asset.device, "generated by the statistician", "integer")
        if 'min' in self._functions:
            Virtual.create(context, self.getAssetName('min'), self._asset.device, "generated by the statistician", self._asset.profile)
        if 'max' in self._functions:
            Virtual.create(context, self.getAssetName('max'), self._asset.device, "generated by the statistician", self._asset.profile)
        if 'avg' in self._functions:
            Virtual.create(context, self.getAssetName('avg'), self._asset.device, "generated by the statistician", "number")
        if "std" in self._functions:
            Virtual.create(context, self.getAssetName('devSum'), self._asset.device, "generated by the statistician","number")
            Virtual.create(context, self.getAssetName('std'), self._asset.device, "generated by the statistician", "number")

    def getAssetName(self, functionName):
        """
        builds the asset name for the asset that should be used for the specified function.
        :param functionName: a string, the name of the function
        :return: unique name for asset, function and group
        """
        return "{}_{}_{}".format(self._asset.name, self._name, functionName)

    def calculate(self, value):
        """
        updates  all the assets that contain the results of the functions that this statistician has to calculate.
        :param value: the new value that arrived.
        :return:
        """
        if 'count' in self._functions:
            cnt = Actuator(device=self._asset.device, name=self.getAssetName('count'), connection=self._asset.connection)
            prevVal = cnt.value
            if not prevVal:
                cnt.value = 1
            else:
                cnt.value =  prevVal + 1
        if 'min' in self._functions:
            minAct = Actuator(device=self._asset.device, name=self.getAssetName('min'), connection=self._asset.connection)
            prevVal = minAct.value
            if prevVal == None or value < prevVal:
                minAct.value = value
        if 'max' in self._functions:
            maxAct = Actuator(device=self._asset.device, name=self.getAssetName('max'), connection=self._asset.connection)
            prevVal = maxAct.value
            if prevVal == None or value > prevVal:
                maxAct.value = value
        if 'avg' in self._functions:
            avg = Actuator(device=self._asset.device, name=self.getAssetName('avg'), connection=self._asset.connection)
            avgVal = avg.value
            if avgVal == None:
                avg.value = value
            else:
                cntVal = cnt.value
                avg.value = avgVal - (avgVal / cntVal) + (float(value) / cntVal)
        if "std" in self._functions:
            devSum = Actuator(device=self._asset.device, name=self.getAssetName('devSum'), connection=self._asset.connection)       # we use a helper actuator for this to store a midstage value
            if devSum.value == None:
                devSum.value = 0
            else:
                devSum.value += (value - avg.value)
                std = Actuator(device=self._asset.device, name=self.getAssetName('std'), connection=self._asset.connection)
                std.value = math.sqrt((devSum.value * devSum.value) / cntVal)


    def resetValues(self):
        """
        resets all the values of the assets that this statistician feeds. This is called when
        a time period has passed.
        :return:
        """
        if 'count' in self._functions:
            cnt = Actuator(device=self._asset.device, name=self.getAssetName('count'))
            cnt.value = 0
        if 'min' in self._functions:
            minAct = Actuator(device=self._asset.device, name=self.getAssetName('min'))
            minAct.value = self._asset.value
        if 'max' in self._functions:
            maxAct = Actuator(device=self._asset.device, name=self.getAssetName('max'))
            maxAct.value = self._asset.value
        if 'avg' in self._functions:
            avg = Actuator(device=self._asset.device, name=self.getAssetName('avg'))
            avg.value = 0
        if "std" in self._functions:
            devSum = Actuator(device=self._asset.device, name=self.getAssetName('devSum'))  # we use a helper actuator for this to store a midstage value
            devSum.value = 0
            std = Actuator(device=self._asset.device, name=self.getAssetName('std'))
            std.value = 0