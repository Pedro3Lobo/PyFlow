from datetime import datetime

from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
from pylsl import StreamInlet, resolve_streams, pylsl
from PyFlow.Packages.PyFlowBase.Nodes import FLOW_CONTROL_COLOR

import copy

import sys
import multiprocessing


# LSL_Writer
class SingleStreamSample(NodeBase):
    def __init__(self, name):
        super(SingleStreamSample, self).__init__(name)
        # Input pins
        self.beginPin = self.createInputPin("Begin", 'ExecPin', None, self.start)
        self.stopPin = self.createInputPin("Stop", 'ExecPin', None, self.stop)

        self.StreamName = self.createInputPin("Name", 'StringPin')

        # Output pins

        self.Send = self.createOutputPin("Value", "FloatPin")
        self.Stamp = self.createOutputPin("TimeStamp", "FloatPin")

        self.Info = self.createOutputPin('Info', 'AnyPin', structure=StructureType.Single)
        self.Info.enableOptions(PinOptions.AllowAny)

        self.Begin_Out = self.createOutputPin("Start", 'ExecPin')
        self.End_Out = self.createOutputPin("Stop", 'ExecPin')

        self.inlets = []
        self.bWorking = False
        self.headerColor = FLOW_CONTROL_COLOR

        self.DataBase = dict()
        self.StructDataBase = dict()
        self.DataBaseZero = dict()

        self.Graph_queue = multiprocessing.Queue()
        self.online = False


        self.start = time.time()
        self.empty = False
        self.i=0
        self.counter = 0
        self.LastValue = 0
        self.hasReceived = False

    def Tick(self, delta):
        super(SingleStreamSample, self).Tick(delta)
        timer1 = time.time()
        if self.bWorking:
            if time.time() - self.start >= 1:
                self.start = time.time()
                self.counter = 0

            if len(self.inlets) != 0:

                # Pull a chunk of samples from the inlet
                samples, timestamps = self.inlets[0].pull_chunk(max_samples=1)



                if len(samples) > 0:
                    if not self.hasReceived:
                        self.Begin_Out.call()
                        self.hasReceived = True
                    self.empty = True
                    self.Send.setData(samples[0][0])
                    self.Stamp.setData(timestamps[0])
                    self.i = self.i + 1
                    #print(samples)
                    # Process the received samples
                    # for sample, timestamp in zip(samples, timestamps):
                    #     self.i= self.i+1;
                    #     if self.LastValue != samples[0][0]:
                    #         self.Send.setData(samples[0][0])
                    #         self.Stamp.setData(timestamps[0])
                    #         self.LastValue = samples[0][0]

                print("i="+str(self.i))


            else:
                self.bWorking = False

        if timer1 - time.time() != 0:
            self.counter += 1
            # print("it took |"+str(timer1-time.time())+"| to get the values")

    def fill_any(self, i):
        fill_var = []
        while len(fill_var) < i:
            fill_var.append(0)
        return fill_var

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def stop(self, *args, **kwargs):
        self.hasReceived = False
        self.bWorking = False


    def start(self, *args, **kwargs):
        self.bWorking = True
        streams = resolve_streams()
        stream_information = []
        stream_information2 = dict()

        for stream in streams:

            inlet = StreamInlet(stream)
            if inlet.info().name() != self.StreamName.getData():
                continue
            stream_channels = dict()
            channels = inlet.info().desc().child("channels").child("channel")

            channels_dicts = dict()
            channels_dicts_zero = dict()
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
                channels_dicts_zero[sensor] = self.fill_any(int(inlet.info().nominal_srate()))

            self.DataBase[inlet.info().name()] = channels_dicts
            self.StructDataBase = copy.deepcopy(self.DataBase)
            self.DataBaseZero[inlet.info().name()] = channels_dicts_zero

            inlet_info = {
                "Name": inlet.info().name(),
                "Type": inlet.info().type(),
                "Channels": int(inlet.info().channel_count()),
                "Sampling Rate": int(inlet.info().nominal_srate()),
                "Channels Info": stream_channels,
            }
            stream_information.append(inlet_info)
            stream_information2 = {inlet.info().name(): inlet_info}
            self.Info.setData(stream_information)

            self.inlets.append(inlet)

            self.online = True


    def addDataToDict(self, key, data):
        for i, row in enumerate(self.DataBase[key]):
            self.DataBase[key][row].append(data[i])
            # if i == 0:
            # print("Lenght"+str(len(self.DataBase[key][row])))

            if self.inlets[-1].info().nominal_srate()==0:
                if len(self.DataBase[key][row]==2):
                    self.DataBase[key][row].pop(0)
                    # self.Graph_queue.put(self.DataBase)
                    self.DataBase = None
                    self.DataBase = copy.deepcopy(self.StructDataBase)

            elif len(self.DataBase[key][row]) > 1:
                # print("Length" + str(len(self.DataBase[key][row])))
                self.DataBase[key][row].pop(0)
                self.DataBase = None
                self.DataBase = copy.deepcopy(self.StructDataBase)

    @staticmethod
    def category():
        return 'Receivers'
