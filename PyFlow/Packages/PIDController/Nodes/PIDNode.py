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
    def __init__(self, kp, ki, kd, integral_max=32767):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        self.integral_max = integral_max
        self.prev_error = 0
        self.integral = 0
        self.lastTimeStamp = 0.0

    def calculate(self, setpoint, current_value, TimeStamp):
        time_delta = TimeStamp-self.lastTimeStamp

        #print(time_delta)

        self.lastTimeStamp = TimeStamp

        error = setpoint - current_value
        self.integral += error * time_delta

        # Clamp the integral term to prevent windup
        self.integral += error * time_delta

        derivative = (error - self.prev_error) / time_delta

        print("KP=" + str((self.kp * error)))
        print("KI=" + str((self.ki * self.integral)))
        print("KD=" + str((self.kd * derivative)))



        # Calculate the control output using bitwise operations
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

        self.prev_error = error

        print()


        return output


def save_json(file_name, data, time):
    dt_string = time.strftime("%d-%m-%Y_%H-%M-%S")
    filename = dt_string + "-" + file_name
    with open("Data/" + filename + ".txt", "a") as outfile:
        json.dump(data, outfile)
        outfile.write('\n')


class PIDNode(NodeBase):
    def __init__(self, name):
        super(PIDNode, self).__init__(name)

        self.default = None
        self.beginPin = self.createInputPin("Begin", 'ExecPin', None, self.start)
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

        self.Setpoint = self.createInputPin('Target', 'FloatPin')

        self.Performance = self.createInputPin('In', 'FloatPin')
        self.TimeStamp= self.createInputPin('Timestamp', 'FloatPin')




        # Output
        # self.Result = self.createOutputPin("Result", "FloatPin")

        # self.Control = self.createOutputPin("Control", "FloatPin")

        self.Send = self.createOutputPin('Data', 'AnyPin', structure=StructureType.Multi)
        self.Send.enableOptions(PinOptions.AllowAny)

        self.now = datetime.now()

        self.Begin_Out = self.createOutputPin("Start", 'ExecPin')
        self.End_Out = self.createOutputPin("Stop", 'ExecPin')

        self._Max = 0
        self._Min = 0

        self.bWorking = None
        self.receivedNewValue = False
        self.sentFirstValue = False
        self.pid = None
        self.startTimer = time.time()
        self.start = time.time()
        self.timeDelta = 0
        self.interval = 0
        self.val = 0
        self.randomval = 0.001
        self.Difficulty = 0.0

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
        super(PIDNode, self).Tick(delta)
        if self.bWorking:

            if time.time() - self.start >= self.timeDelta:

                self.timeDelta = self.DelayCalculation(self, round(time.time() - self.start, 3))
                # self.timeDelta = ((time.time() - self.start)-self.Timer.getData())*2
                self.start = time.time()
                control = self.pid.calculate(self.Setpoint.getData(), self.Performance.getData(), self.TimeStamp.getData())
                self.default += control

                if not self.sentFirstValue:
                    self.Begin_Out.call()
                    self.sentFirstValue = True

                if self._Max >= self._Min:
                    if self._Max < self.default:
                        self.default = self._Max

                    elif self._Min > self.default:
                        self.default = self._Min
                else:
                    if self._Max > self.default:
                        self.default = self._Max

                    elif self._Min < self.default:
                        self.default = self._Min

                info = {"Time": time.time() - self.startTimer, "SetPoint": self.Setpoint.getData(),
                        "KP": self.KP.getData(),
                        "KI": self.KI.getData(), "KD": self.KD.getData(), "Timer": self.Timer.getData(),
                        "Performance": self.Performance.getData(),
                        "Difficulty": self.default}

                _dict = dict()
                _dict = {"" + self.Name.getData() + "": self.default}

                self.Send.setData(_dict)
                file_name = "ID" + self.ID.getData() + "_" + self.Name.getData()

                # self.Result.setData(self.default)

            self.val = self.Performance.getData()
        else:
            if self.randomval < 1:
                self.interval = self.Timer.getData()
                self.DelayCalculation(self, round(self.randomval, 3))
                #print("Delta time " + str( self.DelayCalculation(self, round(self.randomval, 3))) + "Time since last Update" + str(self.randomval))
                self.randomval += 0.001

    def stop(self, *args, **kwargs):
        self.bWorking = False
        self.End_Out.call()

    def start(self, *args, **kwargs):

        self.bWorking = True
        self.startTimer = time.time()
        self.default = self.Default.getData()
        kp = self.KP.getData()
        ki = self.KI.getData()
        kd = self.KD.getData()
        self.interval = self.Timer.getData()

        self.pid = PIDController(kp, ki, kd)
        self.val = self.Performance.getData()
        self._Max = self.Max.getData()
        self._Min = self.Min.getData()


    @Memoize
    def DelayCalculation(self, real_interval):
        interval = self.interval
        if real_interval > self.interval:
            interval += self.interval - real_interval-0.002
            #print("Interval = "+str(self.interval) + "real Interval = "+str(real_interval) + "Delay = "+str(interval))
        return interval

