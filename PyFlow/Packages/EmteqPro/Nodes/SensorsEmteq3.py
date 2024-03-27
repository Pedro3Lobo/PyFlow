from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
import json

class SensorsEmteq3(NodeBase):
    def __init__(self, name):
        super(SensorsEmteq3, self).__init__(name)
        self.beginPin = self.createInputPin("Begin", 'ExecPin', None, self.start)
        self.stopPin = self.createInputPin("Stop", 'ExecPin', None, self.stop)

        self.Sensor_Name = self.createInputPin('Name', 'StringPin')
        self.Data = self.createInputPin('InData', 'AnyPin', structure=StructureType.Multi)
        self.Data.enableOptions(
            PinOptions.AllowMultipleConnections | PinOptions.AllowAny | PinOptions.DictElementSupported)
        self.Data.disableOptions(PinOptions.SupportsOnlyArrays)

        self.Send = self.createOutputPin('DataOut', 'AnyPin', structure=StructureType.Multi)
        self.Send.enableOptions(PinOptions.AllowAny)
        self.Begin_Out = self.createOutputPin("Start", 'ExecPin')
        self.End_Out = self.createOutputPin("Stop", 'ExecPin')

        self.LastValue = self.createOutputPin('LastValue', 'FloatPin')

        self.bWorking = False
    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('BoolPin')
        helper.addOutputDataType('BoolPin')
        helper.addInputStruct(StructureType.Single)
        helper.addOutputStruct(StructureType.Single)
        return helper

    @staticmethod
    def category():
        return 'Data Management'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def Tick(self, delta):
        super(SensorsEmteq3, self).Tick(delta)
        if self.bWorking:
            sensor_name = self.Sensor_Name.getData()
            data = self.Data.getData()

            if sensor_name in data["Emteq"]:
                self.Send.setData(data["Emteq"][sensor_name])
                if len(data["Emteq"][sensor_name]) != 0:
                    self.LastValue.setData(data["Emteq"][sensor_name][-1]*1.2)

    def start(self, *args, **kwargs):
        self.bWorking = True
        self.Begin_Out.call()

    def stop(self, *args, **kwargs):
        self.bWorking = False
        self.End_Out.call()
