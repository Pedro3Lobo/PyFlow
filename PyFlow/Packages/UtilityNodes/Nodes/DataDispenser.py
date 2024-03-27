from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *


class DataDispenser(NodeBase):
    def __init__(self, name):
        super(DataDispenser, self).__init__(name)
        self.beginPin = self.createInputPin("Begin", 'ExecPin', None, self.start)
        self.stopPin = self.createInputPin("Stop", 'ExecPin', None, self.stop)

        self.Stream_Name = self.createInputPin('Stream', 'StringPin')
        self.Channel_Name = self.createInputPin('Channel', 'StringPin')
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
        return 'Generated from wizard'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def Tick(self, delta):
        super(DataDispenser, self).Tick(delta)
        if self.bWorking:
            Stream = self.Stream_Name.getData()
            Channel = self.Channel_Name.getData()

            #sensor_name = self.Sensor_Name.getData()
            data = self.Data.getData()
            if Channel in data[Stream]:
                self.Send.setData(data[Stream][Channel])
                if len(data[Stream][Channel]) != 0:
                    value = {Channel: data[Stream][Channel][-1]}
                    self.LastValue.setData(data[Stream][Channel][-1])

    def start(self, *args, **kwargs):
        self.bWorking = True
        self.Begin_Out.call()

    def stop(self, *args, **kwargs):
        self.bWorking = False
        self.End_Out.call()
