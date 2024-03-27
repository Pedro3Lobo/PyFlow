import json

from datetime import date, datetime
from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

from PyFlow.Packages.PyFlowBase.Nodes import FLOW_CONTROL_COLOR


class Memoize:
    def __init__(self, func):
        self.func = func
        self.memo = {}

    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.func(*args)
        return self.memo[args]


def save_json(file_name, data, time):
    dt_string = time.strftime("%d-%m-%Y_%H-%M-%S")
    filename = dt_string + "-" + file_name
    with open("Data/" + filename + ".txt", "a") as outfile:
        json.dump(data, outfile)
        outfile.write('\n')


class SaveJson2(NodeBase):
    def __init__(self, name):
        super(SaveJson2, self).__init__(name)
        self.beginPin = self.createInputPin("Begin", 'ExecPin', None, self.start)
        self.ActionPin = self.createInputPin("Action", 'ExecPin', None, self.Action)
        self.stopPin = self.createInputPin("Stop", 'ExecPin', None, self.stop)

        self.Name = self.createInputPin('Name', 'StringPin')
        self.Timer = self.createInputPin('Timer', 'FloatPin')

        self.Performance = self.createInputPin('Performance', 'AnyPin', structure=StructureType.Multi)
        self.Performance.enableOptions(
            PinOptions.AllowMultipleConnections | PinOptions.AllowAny | PinOptions.DictElementSupported)
        self.Performance.disableOptions(PinOptions.SupportsOnlyArrays)

        # Output
        self.now = datetime.now()

        self.timeDelta = 0
        self.bWorking = None
        self.receivedNewValue = False
        self.pid = None
        self.startTimer = time.time()
        self.start = time.time()
        self.val = 0
        self.dataGathering = []
        self.Difficulty = 0.0
        self.position = 0
        self.randomval = 0.001
        self.count_loops = 0

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
        return 'Generated from wizard'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def Tick(self, delta):
        super(SaveJson2, self).Tick(delta)
        if self.bWorking:

            if time.time() - self.start >= self.timeDelta:
                self.timeDelta = self.DelayCalculation(self, round(time.time() - self.start, 3))
                if len(self.val) == 0:
                    return

                # Create an info dictionary
                info = {
                    "Time": time.time() - self.startTimer,
                    "Performance": self.val[self.position]
                }
                self.dataGathering.append(info)
                # Save info to a JSON file
                self.count_loops += 1

                self.start = time.time()
                self.position += 1

                if self.position > len(self.val) - 1:
                    self.position = len(self.val) - 1
        else:
            if self.randomval < 1:
                print("Loading " + str((self.randomval / 1) * 100) + "% ...")
                self.interval = self.Timer.getData()
                self.DelayCalculation(self, round(self.randomval, 3))
                # print("Delta time " + str( self.DelayCalculation(self, round(self.randomval, 3))) + "Time since last Update" + str(self.randomval))
                self.randomval += 0.001

    def stop(self, *args, **kwargs):
        self.bWorking = False
        save_json(self.Name.getData(), self.dataGathering, self.now)
        print("Number of Loops :" + str(self.count_loops))


    def start(self, *args, **kwargs):
        self.bWorking = True
        self.startTimer = time.time()
        self.randomval += 0.001

    def Action(self, *args, **kwargs):
        #print("action")
        self.receivedNewValue = True
        self.position = 0
        self.val = self.Performance.getData()

    @Memoize
    def DelayCalculation(self, real_interval):
        interval = self.interval
        if real_interval > self.interval:
            interval += self.interval - real_interval - 0.010
            print("Interval = " + str(self.interval) + "real Interval = " + str(real_interval) + "Delay = " + str(
                interval))
        return interval