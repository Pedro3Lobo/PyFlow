from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

import numpy as np
from scipy.signal import find_peaks


class HeartRate(NodeBase):
    def __init__(self, name):
        super(HeartRate, self).__init__(name)
        self.HeartRate = self.createInputPin("HeartRate", 'FloatPin')
        self.Baseline = self.createInputPin("Baseline", 'FloatPin')

        self.Max = self.createInputPin('Max', 'IntPin')
        self.Min = self.createInputPin('Min', 'IntPin')

        self.Result = self.createOutputPin("Result", 'FloatPin')



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
            hr = self.HeartRate.getData()
            base = self.Baseline.getData()

            max = self.Max.getData()
            min = self.Min.getData()

            result = 0

            if hr > base + max:
                result = 0.5

            elif hr < base + min:
                result = 0.9

            else:
                result = 0.7

            self.Result.setData(result)



