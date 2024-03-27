from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *


class popFromArray(NodeBase):
    def __init__(self, name):
        super(popFromArray, self).__init__(name)

        self.inExec = self.createInputPin(
            DEFAULT_IN_EXEC_NAME, "ExecPin", None, self.compute
        )
        self.ls = self.createInputPin(
            "ls", "AnyPin", structure=StructureType.Array, constraint="1"
        )
        self.ls.enableOptions(PinOptions.AllowMultipleConnections)
        self.ls.disableOptions(PinOptions.SupportsOnlyArrays)

        self.index = self.createInputPin("index","IntPin",structure=StructureType.Single)

        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, "ExecPin")

        self.number = self.createOutputPin("out", "IntPin",structure=StructureType.Single)
        self.popped = self.createOutputPin("popped", "BoolPin",structure=StructureType.Single)
        self.outLs = self.createOutputPin("outLs", 'AnyPin', structure=StructureType.Array)
        self.outLs.enableOptions(PinOptions.AllowAny)


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
        poppedElem = None
        ls = self.ls.getData()

        try:
            poppedElem = ls.pop(self.index.getData())
            self.popped.setData(True)
            self.number.setData(poppedElem)
        except IndexError:
            self.popped.setData(False)
            self.number.setData(0)

        self.outLs.setData(ls)
        self.outExec.call()
