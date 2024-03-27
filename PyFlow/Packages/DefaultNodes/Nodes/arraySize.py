from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *


class arraySize(NodeBase):
    def __init__(self, name):
        super(arraySize, self).__init__(name)

        self.inExec = self.createInputPin(
            DEFAULT_IN_EXEC_NAME, "ExecPin", None, self.compute
        )
        self.ls = self.createInputPin(
            "ls", "AnyPin", structure=StructureType.Array, constraint="1"
        )
        self.ls.enableOptions(PinOptions.AllowMultipleConnections)
        self.ls.disableOptions(PinOptions.SupportsOnlyArrays)



        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, "ExecPin")
        self.size = self.createOutputPin("size", "IntPin",structure=StructureType.Single)
        self.is_empty = self.createOutputPin("is_empty", "BoolPin",structure=StructureType.Single)
        self.not_empty = self.createOutputPin("not_empty", "BoolPin", structure=StructureType.Single)


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
        l = len(self.ls.getData())
        self.size.setData(l)
        self.is_empty.setData(True if l > 0 else False)
        self.not_empty.setData(True if l < 0 else False)

        self.outExec.call()