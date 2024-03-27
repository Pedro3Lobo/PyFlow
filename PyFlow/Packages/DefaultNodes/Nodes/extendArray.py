from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *


class extendArray(NodeBase):
    def __init__(self, name):
        super(extendArray, self).__init__(name)

        self.inExec = self.createInputPin(
            DEFAULT_IN_EXEC_NAME, "ExecPin", None, self.compute
        )
        self.lhs = self.createInputPin(
            "lhs", "AnyPin", structure=StructureType.Array, constraint="1"
        )
        self.lhs.enableOptions(PinOptions.AllowMultipleConnections)
        self.lhs.disableOptions(PinOptions.SupportsOnlyArrays)

        self.rhs = self.createInputPin(
            "rhs", "AnyPin", structure=StructureType.Array, constraint="1"
        )
        self.rhs.enableOptions(PinOptions.AllowMultipleConnections)
        self.rhs.disableOptions(PinOptions.SupportsOnlyArrays)

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
        self.number.setData(self.lhs.getData() + self.rhs.getData())
        self.outExec.call()