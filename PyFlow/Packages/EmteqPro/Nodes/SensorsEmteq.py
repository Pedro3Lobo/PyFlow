from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
import json

class SensorsEmteq(NodeBase):
    def __init__(self, name):
        super(SensorsEmteq, self).__init__(name)
        self.Sensor_Name = self.createInputPin('Name', 'StringPin')
        self.Data = self.createInputPin('InData', 'AnyPin', structure=StructureType.Multi)
        self.Data.enableOptions(
            PinOptions.AllowMultipleConnections | PinOptions.AllowAny | PinOptions.DictElementSupported)
        self.Data.disableOptions(PinOptions.SupportsOnlyArrays)

        self.Send = self.createOutputPin('DataOut', 'AnyPin', structure=StructureType.Multi)
        self.Send.enableOptions(PinOptions.AllowAny)

        #self.LastValue = self.createOutputPin('LastValue', 'FloatPin')

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

    def compute(self, *args, **kwargs):
        sensor_name = self.Sensor_Name.getData()
        data_r = self.Data.getData()
        if isinstance(data_r, dict):
            #print("is a dict")
            data = data_r

        if isinstance(data_r, str):
            #print("is a string ")
            data = json.loads(data_r)



        if sensor_name in data["Emteq"]:
            self.Send.setData(data["Emteq"][sensor_name])
            #self.LastValue.setData(data["Emteq"][sensor_name][-1])
