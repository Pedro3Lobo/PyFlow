import random

from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
from pylsl import StreamInlet, resolve_streams, pylsl, StreamInfo, StreamOutlet
from PyFlow.Packages.PyFlowBase.Nodes import FLOW_CONTROL_COLOR


# DemoNode
# LSL_Writer
class StreamGrapher(NodeBase):
    def __init__(self, name):
        super(StreamGrapher, self).__init__(name)
        self.beginPin = self.createInputPin("Begin", 'ExecPin', None, self.start)
        self.stopPin = self.createInputPin("Stop", 'ExecPin', None, self.stop)
        self.streamName = self.createInputPin("Name", 'StringPin')
        self.streamType = self.createInputPin("Type", 'StringPin')
        self.streamID = self.createInputPin("ID", 'StringPin')
        self.time = self.createInputPin("Time", 'FloatPin')
        self.Data = self.createInputPin('Data', 'AnyPin', structure=StructureType.Multi)
        self.Data.enableOptions(
            PinOptions.AllowMultipleConnections | PinOptions.AllowAny | PinOptions.DictElementSupported)
        self.Data.disableOptions(PinOptions.SupportsOnlyArrays)

        self.out = self.createOutputPin("OUT", 'ExecPin')
        # self.Info_Stream = self.createOutputPin('Info', 'AnyPin', structure=StructureType.Single)
        # self.Info_Stream.enableOptions(PinOptions.AllowAny)
        # self.Send = self.createOutputPin('DataOut', 'AnyPin', structure=StructureType.Multi)
        # self.Send.enableOptions(PinOptions.AllowAny)

        self.info = None
        self.bWorking = False
        self.outlet = None
        self.info = None
        self.headerColor = FLOW_CONTROL_COLOR
        self.On = False

        self.DataBase = dict()
        self.channels_dicts = dict()
        self.start = time.time()
        self.counter = 0

    def Tick(self, delta):
        super(StreamGrapher, self).Tick(delta)
        if self.bWorking:

            if time.time() - self.start >= self.time.getData():

                sample = list(self.Data.getData().values())
                # self.addDataToDict(self.streamName.getData(), sample)
                #self.Send.setData(self.DataBase)
                #print("Flag1")
                self.outlet.push_sample(sample)
                self.start = time.time()


    def addDataToDict(self, key, data):
        for i, row in enumerate(self.DataBase[key]):
            self.DataBase[key][row].append(data[i])

    def get_all_keys(self, array_of_dicts):
        keys = dict()
        channels_dicts = dict()
        i = 0
        for key in array_of_dicts.keys():
            keys.update({i: [key, ""]})
            self.channels_dicts[key] = []
            i += 1

        return keys

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def stop(self, *args, **kwargs):
        self.bWorking = False
        self.On = False

    def start(self, *args, **kwargs):
        global info
        #self.out.call()
        data = self.Data.getData()
        if data is not None:

            stream_name = self.streamName.getData()
            stream_type = self.streamType.getData()
            channel_count = len(data)
            stream_desc = {
                "Name": stream_name,
                "Type": stream_type,
                "Channels": channel_count,
                "Sampling Rate": self.time.getData(),
                "Channels Info": self.get_all_keys(data),
            }
            info = StreamInfo(
                name=stream_name,
                type=stream_type,
                channel_count=channel_count,
                nominal_srate=19,
                channel_format='float32',
                source_id=self.streamID.getData()
            )
            info_channels = info.desc().append_child("channels")

            for name in data.keys():
                info_channels.append_child("channel").append_child_value("label", name)
            self.DataBase[stream_name] = self.channels_dicts

            self.info = info
            self.outlet = StreamOutlet(self.info)
            self.bWorking = True

        # self.Info_Stream.setData(stream_information)

    @staticmethod
    def category():
        return 'Transmitters'
