import numpy as np

from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *


class CalculationEmteq(NodeBase):
    def __init__(self, name):
        super(CalculationEmteq, self).__init__(name)
        #Inputs
        self.Data = self.createInputPin('Data', 'AnyPin', structure=StructureType.Multi)
        self.Data.enableOptions(
            PinOptions.AllowMultipleConnections | PinOptions.AllowAny | PinOptions.DictElementSupported)
        self.Data.disableOptions(PinOptions.SupportsOnlyArrays)

        #Outputs
        self.Focus = self.createOutputPin('Focus', 'IntPin')

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
        return 'Calculation'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def compute(self, *args, **kwargs):
        data = self.Data.getData()

        ppg_features = data["Ppg"]
        # Assuming you have 'emg_features' and 'ppg_features' as numpy arrays
        valence_estimation, arousal_estimation, dfc_mod = self.estimate_valence_arousal(
            [L_Zygomaticus, R_Zygomaticus, L_Orbicularis, R_Orbicularis, L_Frontalis, R_Frontalis, Corrugator],
            ppg_features
        )


        print("Estimated Valence:", valence_estimation)

        print("Estimated Arousal:", arousal_estimation)

        self.Focus.setData(dfc_mod)

    def estimate_valence_arousal(self,emg_features, ppg_features):
        # Define thresholds for valence and arousal estimation
        valence_threshold = 0.5  # Adjust this value based on your data and requirements
        arousal_threshold = 0.5  # Adjust this value based on your data and requirements

        # Calculate the average of facial EMG features
        avg_emg = np.mean(emg_features)

        # Calculate the average of PPG sensor features
        avg_ppg = np.mean(ppg_features)

        # Translates the values of valence and arousal to numeric one
        dfc_mod = 0

        # Estimate valence based on facial EMG features
        if avg_emg >= valence_threshold:
            valence = 'Positive'
            dfc_mod = dfc_mod + 1
        else:
            valence = 'Negative'
            dfc_mod = dfc_mod - 1

        # Estimate arousal based on PPG sensor features
        if avg_ppg >= arousal_threshold:
            arousal = 'High'
            dfc_mod = dfc_mod + 2
        else:
            arousal = 'Low'
            dfc_mod = dfc_mod - 2

        return valence, arousal, dfc_mod
