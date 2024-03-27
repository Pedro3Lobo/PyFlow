from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *


class CSVEmteq(NodeBase):
    def __init__(self, name):
        super(CSVEmteq, self).__init__(name)
        self.data = self.createInputPin('InData', 'AnyPin', structure=StructureType.Multi)
        self.data.enableOptions(PinOptions.AllowMultipleConnections | PinOptions.AllowAny | PinOptions.DictElementSupported)
        self.data.disableOptions(PinOptions.SupportsOnlyArrays)

        self.Send = self.createOutputPin('DataOut', 'AnyPin', structure=StructureType.Multi)
        self.Send.enableOptions(PinOptions.AllowAny)


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
        Sources=self.data.getData()
        Emteq_data=dict()
        for source in Sources:
            if source == "Emteq":
                Emteq_data=Sources[source]

        self.Send.setData(Emteq_data)

    def create_csv_with_specifications(self,data, specifications, filename):
        # Add the version information to the specifications
        specifications.insert(0, "#Format/Version,CSV1.0.0")

        # Open the CSV file in write mode
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write the specifications as comment lines
            for spec in specifications:
                writer.writerow([spec])

            # Write the CSV header row
            header_row = data[0].keys()
            writer.writerow(header_row)

            # Write the data rows
            for row in data:
                writer.writerow(row.values())


    def format_Data(self, data):
        data = [
            {'Frame#': 1, 'Time': 0.01052, 'Emg/RightFrontalis': 1.02, 'Emg/RightZygomaticus': 0.89,
             'Emg/LeftFrontalis': 0.85},
            {'Frame#': 2, 'Time': 0.01584, 'Emg/RightFrontalis': 1.03, 'Emg/RightZygomaticus': 0.88,
             'Emg/LeftFrontalis': 0.84},
            # Add more data rows as needed
        ]
        return data

    def format_Specifications(self, specifications):


        return specifications