from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *


class arraySum(NodeBase):
    def __init__(self, name):
        super(arraySum, self).__init__(name)

        self.inExec = self.createInputPin(
            DEFAULT_IN_EXEC_NAME, "ExecPin", None, self.compute
        )
        self.ls = self.createInputPin(
            "ls", "AnyPin", structure=StructureType.Array, constraint="1"
        )
        self.ls.enableOptions(PinOptions.AllowMultipleConnections)
        self.ls.disableOptions(PinOptions.SupportsOnlyArrays)

        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, "ExecPin")
        self.number = self.createOutputPin("out", "IntPin", structure=StructureType.Single)


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
        self.number.setData(sum(self.ls.getData()))
        self.outExec.call()