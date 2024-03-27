from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *


class insertToArray(NodeBase):
    def __init__(self, name):
        super(insertToArray, self).__init__(name)

        self.inExec = self.createInputPin(
            DEFAULT_IN_EXEC_NAME, "ExecPin", None, self.compute
        )
        self.ls = self.createInputPin(
            "ls", "AnyPin", structure=StructureType.Array, constraint="1"
        )
        self.ls.enableOptions(PinOptions.AllowMultipleConnections)
        self.ls.disableOptions(PinOptions.SupportsOnlyArrays)

        self.element = self.createInputPin("element","AnyPin",structure=StructureType.Single)
        self.index = self.createInputPin("index", "IntPin", structure=StructureType.Single)

        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, "ExecPin")
        self.number = self.createOutputPin('out', 'AnyPin', structure=StructureType.Array)
        self.number.enableOptions(PinOptions.AllowAny)


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
        return 'ArrayNode'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Number of specific element in array"

    def compute(self, *args, **kwargs):
        self.ls.getData().insert(self.index.getData(), self.element.getData())
        self.number.setData(self.ls.getData())

        self.outExec.call()
