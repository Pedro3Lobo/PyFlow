from datetime import datetime

from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
from pylsl import StreamInlet, resolve_streams, pylsl
from PyFlow.Packages.PyFlowBase.Nodes import FLOW_CONTROL_COLOR
#LSL_Writer
class MultiStreamReceiver(NodeBase):
        def __init__(self, name):
            super(MultiStreamReceiver, self).__init__(name)
            self.beginPin = self.createInputPin("Begin", 'ExecPin', None, self.start)
            self.stopPin = self.createInputPin("Stop", 'ExecPin', None, self.stop)

            self.out = self.createOutputPin("OUT", 'ExecPin')
            self.Send = self.createOutputPin('Data', 'AnyPin', structure=StructureType.Multi)
            self.Send.enableOptions(PinOptions.AllowAny)
            self.Info = self.createOutputPin('Info', 'AnyPin', structure=StructureType.Single)
            self.Info.enableOptions(PinOptions.AllowAny)
            self.inlets = []
            self.bWorking = False
            self.headerColor = FLOW_CONTROL_COLOR

            self.DataBase = dict()
            self.start = time.time()
            self.counter = 0

        def Tick(self, delta):
            super(MultiStreamReceiver, self).Tick(delta)
            if self.bWorking:
                if int(time.time()) - self.start >= 1:
                    self.start = time.time()
                    print("LSL Receiver2->Number of values in one second:" + str(self.counter))
                    self.counter = 0
                    self.out.call()
                for inlet in self.inlets:
                    now = datetime.now()
                    samples, timestamps = inlet.pull_chunk(max_samples=int(inlet.info().nominal_srate()))

                    if samples:
                        # Process the received samples
                        for sample, timestamp in zip(samples, timestamps):
                            # Do something with the sample data and timestamp
                            print("Sample = {}".format(sample))
                            print(inlet.info().name()+"Received sample:", sample, "at timestamp:", timestamp)
                            self.addDataToDict(inlet.info().name(), sample)
                self.Send.setData(self.DataBase)
                self.counter += 1
        @staticmethod
        def keywords():
            return []

        @staticmethod
        def description():
            return "Description in rst format."

        def stop(self, *args, **kwargs):
            self.bWorking = False

        def start(self, *args, **kwargs):
            streams = resolve_streams()
            if not streams:
                print("No streams found")
            else:
                self.bWorking = True
                stream_information = []
                for stream in streams:

                    inlet = StreamInlet(stream)
                    stream_channels = dict()
                    channels = inlet.info().desc().child("channels").child("channel")

                    channels_dicts = dict()
                    for i in range(inlet.info().channel_count()):
                        # Get the channel number (e.g. 1)
                        channel = i + 1

                        # Get the channel type (e.g. ECG)
                        sensor = channels.child_value("label")

                        # Get the channel unit (e.g. mV)
                        unit = channels.child_value("unit")

                        # Store the information in the stream_channels dictionary
                        stream_channels.update({channel: [sensor, unit]})
                        channels = channels.next_sibling()
                        channels_dicts[sensor] = []

                    self.DataBase[inlet.info().name()] = channels_dicts

                    inlet_info = {
                        "Name": inlet.info().name(),
                        "Type": inlet.info().type(),
                        "Channels": int(inlet.info().channel_count()),
                        "Sampling Rate": int(inlet.info().nominal_srate()),
                        "Channels Info": stream_channels,
                    }
                    stream_information.append(inlet_info)
                    #print(inlet_info)
                    self.Info.setData(stream_information)
                    #print(str(stream_information))
                    self.inlets.append(inlet)

        def addDataToDict(self, key, data):
            for i, row in enumerate(self.DataBase[key]):
                self.DataBase[key][row].append(data[i])

        @staticmethod
        def category():
            return 'Receivers'