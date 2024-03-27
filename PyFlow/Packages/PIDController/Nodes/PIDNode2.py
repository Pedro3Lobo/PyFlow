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


class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error_sum = 0
        self.last_error = 0

    def calculate(self, setpoint, input1, time_delta):
        error = setpoint - input1

        self.error_sum += error

        error_diff = error - self.last_error

        output = (self.kp * error) + (self.ki * self.error_sum) + (self.kd * (error_diff / time_delta))

        self.last_error = error

        return output


def save_json(file_name, data, time):
    dt_string = time.strftime("%d-%m-%Y_%H-%M-%S")
    filename = dt_string + "-" + file_name
    with open("Data/" + filename + ".txt", "a") as outfile:
        json.dump(data, outfile)
        outfile.write('\n')


class PIDNode2(NodeBase):
    def __init__(self, name):
        super(PIDNode2, self).__init__(name)

        self.min_val = None
        self.max_val = None
        self.timeDelta = 0
        self.default = None
        self.beginPin = self.createInputPin("Begin", 'ExecPin', None, self.start)
        self.ActionPin = self.createInputPin("Action", 'ExecPin', None, self.Action)

        self.stopPin = self.createInputPin("Stop", 'ExecPin', None, self.stop)

        self.Name = self.createInputPin('Name', 'StringPin')
        self.ID = self.createInputPin('ID', 'StringPin')

        self.KP = self.createInputPin('KP', 'FloatPin')
        self.KI = self.createInputPin('KI', 'FloatPin')
        self.KD = self.createInputPin('KD', 'FloatPin')

        self.Timer = self.createInputPin('Timer', 'FloatPin')

        self.Default = self.createInputPin('Default', 'FloatPin')

        self.Max = self.createInputPin('Max', 'FloatPin')

        self.Min = self.createInputPin('Min', 'FloatPin')

        self.Setpoint = self.createInputPin('Set point', 'FloatPin')

        self.Performance = self.createInputPin('Performance', 'AnyPin', structure=StructureType.Multi)
        self.Performance.enableOptions(
            PinOptions.AllowMultipleConnections | PinOptions.AllowAny | PinOptions.DictElementSupported)
        self.Performance.disableOptions(PinOptions.SupportsOnlyArrays)


        # Output

        self.now = datetime.now()

        self.Send = self.createOutputPin('Data', 'AnyPin', structure=StructureType.Multi)
        self.Send.enableOptions(PinOptions.AllowAny)


        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, 'ExecPin')

        self.bWorking = None
        self.receivedNewValue = False
        self.pid = None
        self.sentFirstValue = False

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
        return 'DataControl'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def Tick(self, delta):
        super(PIDNode2, self).Tick(delta)
        if self.bWorking:

            if time.time() - self.start >= self.timeDelta:
                self.timeDelta = self.DelayCalculation(self, round(time.time() - self.start, 3))
                if self.val is None:
                    return
                if len(self.val) == 0:
                    return

                control = self.pid.calculate(self.Setpoint.getData(), self.val[self.position], self.Timer.getData())

                # Update the default value
                self.default += control

                # Ensure the default value is within the min-max range
                if self.max_val >= self.min_val:
                    self.default = max(self.min_val, min(self.max_val, self.default))
                else:
                    self.default = min(self.max_val, max(self.min_val, self.default))

                # Create an info dictionary
                info = {
                    "Time": time.time() - self.startTimer,
                    "SetPoint": self.Setpoint.getData(),
                    "KP": self.KP.getData(),
                    "KI": self.KI.getData(),
                    "KD": self.KD.getData(),
                    "Performance": self.val[self.position],
                    "Difficulty": self.default
                }
                self.dataGathering.append(info)
                # Save info to a JSON file

                self.count_loops += 1

                # Create a dictionary for sending data
                data_dict = {self.Name.getData(): self.default}
                #print("Data Info :{}".format(data_dict))
                self.Send.setData(data_dict)
                if not self.sentFirstValue:
                    self.outExec.call()
                    self.sentFirstValue= True

                self.start = time.time()
                self.position += 1

                if self.position > len(self.val) - 1:
                    self.position = len(self.val) - 1
        else:
            if self.randomval < 1:
                print("Loading "+str((self.randomval/1
                                      )*100)+"% ...")
                self.interval = self.Timer.getData()
                self.DelayCalculation(self, round(self.randomval, 3))
                # print("Delta time " + str( self.DelayCalculation(self, round(self.randomval, 3))) + "Time since last Update" + str(self.randomval))
                self.randomval += 0.001


    def Action(self, *args, **kwargs):
        self.receivedNewValue = True
        self.position = 0
        self.val = self.Performance.getData()

    def stop(self, *args, **kwargs):
        self.bWorking = False
        file_name = "ID"+self.ID.getData()+"_"+self.Name.getData()
        save_json(file_name, self.dataGathering, self.now)
        self.sentFirstValue = False
        #print("Number of Loops :" + str(self.count_loops))
        # self.End_Out.call()

    def start(self, *args, **kwargs):

        self.bWorking = True
        self.startTimer = time.time()
        self.default = self.Default.getData()
        kp = self.KP.getData()
        ki = self.KI.getData()
        kd = self.KD.getData()
        self.max_val = self.Max.getData()
        self.min_val = self.Min.getData()

        self.pid = PIDController(kp, ki, kd)
        self.val = self.Performance.getData()
        # self.Begin_Out.call()


    @Memoize
    def DelayCalculation(self, real_interval):
        interval = self.interval
        if real_interval > self.interval:
            interval += self.interval - real_interval - 0.005
            # print("Interval = " + str(self.interval) + "real Interval = " + str(real_interval) + "Delay = " + str(
            # interval))
        return interval
