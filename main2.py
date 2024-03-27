import cProfile
import csv
import json
import os
import random
import sys
import time
import logging
from multiprocessing import Queue

import PyQt5.QtWidgets as QtWidgets
import PyQt5.uic as uic
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QSpinBox, QRadioButton, QLabel, QDoubleSpinBox, QWidget, \
    QFrame, QAction
from pyqtgraph.Qt import QtCore


class Memoize:
    def __init__(self, func):
        self.func = func
        self.memo = {}

    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.func(*args)
        return self.memo[args]


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, QU: Queue, *args, **kwargs, ):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.stream_info = None
        ui_file = os.path.abspath('PyMonitorUi15.ui')
        # self.setWindowIcon(QtGui.QIcon("Pymonitor_Logo.png"))
        # Load the UI Page
        uic.loadUi('PyMonitorUi16.ui', self)
        self.Add.clicked.connect(self.Add_Graph)
        self.Minus.clicked.connect(self.Minus_Graph)

        ## Set List ##
        self.listGraph = []
        self.listLineColor = []
        self.listLineSize = []
        self.listWindowSize = []
        self.listVisible = []
        self.ListSources = []
        self.ListKeys = []
        self.ListChannelName = []
        self.ListPos = []
        self.ListSamplingRate = []
        self.RealTimeSamplingRate = []
        self.RL_SamplingRate = []
        # print("init2")
        ## Queue
        self.str = QU

        ## Stream Info ##
        self.stream_name = []
        self.channels = []
        self.sampling_rate = []
        self.stream_type = []

        self.init_stream_info()
        self.init_action()

        ##  Benchmarking Var ##
        level = logging.DEBUG
        fmt = '[%(levelname)s] %(asctime)s - %(message)s'
        logging.basicConfig(level=level, format=fmt)

        self.intervalbegin = self.GetTime()

        ##  Lines  ##
        self.line1 = []
        self.counter = 0
        self.BufferStep = 1
        self.timer = self.GetTime()
        self.timerstamps = 0
        self.updatetime = self.GetTime()
        self.Lock = False
        self.Rest = 0.0

        # print("Flag1")
        ## Fps Counter
        self.fps = 0.
        self.lastupdate = self.GetTime()
        # print("Flag2")
        self.Init_plots()
        # print("Flag3")
        self.Data_Queue()
        self._update()

    def init_action(self):
        self.actionFile1.triggered.connect(lambda: self.save_json("File1"))
        self.actionFile2.triggered.connect(lambda: self.save_json("File2"))
        self.actionFile3.triggered.connect(lambda: self.save_json("File3"))
        self.actionFile4.triggered.connect(lambda: self.save_json("File4"))
        self.actionFile5.triggered.connect(lambda: self.save_json("File5"))
        self.actionFile6.triggered.connect(lambda: self.save_json("File6"))

        self.actionFile1_2.triggered.connect(lambda: self.load_json("File1"))
        self.actionFile2_2.triggered.connect(lambda: self.load_json("File2"))
        self.actionFile3_2.triggered.connect(lambda: self.load_json("File3"))
        self.actionFile4_2.triggered.connect(lambda: self.load_json("File4"))
        self.actionFile5_2.triggered.connect(lambda: self.load_json("File5"))
        self.actionFile6_2.triggered.connect(lambda: self.load_json("File6"))

    @Memoize
    def fill_any(self, i):
        fill_var = []
        while len(fill_var) < i:
            fill_var.append(0)
        return fill_var

    def waiting_room(self):
        while (self.str.empty()):
            pass
        return self.str.get()

    def waiting_room2(self):
        while self.str.get() == self.stream_info:
            pass
        self._update()

    def _update(self):
        start = self.GetTime()
        if not self.str.empty():
            self.Data_Queue()
            #print("My queue is not empty")


        if self.GetTime() - self.timer > 1:
            # self.data_test2(self.line1)
            self.timer = self.GetTime()
            self.timerstamps += 1000;
            self.fps = self.counter
            tx = "FPS: " + str(self.fps)
            self.FPS.setText(tx)
            self.counter = 0
            # self.randomvar = 0

        if self.GetTime() - self.updatetime > self.Seconds.value():
            # print("Var:" + str(self.randomvar))
            self.Rest = self.GetTime() - self.updatetime - self.Seconds.value()
            # logging.debug("Tempo suficiente passou:{} |Tempo passado: {}| Tempo atual: {} |Tempo original: {}
            # |Tempo cortado:{}".format( self.GetTime() - self.updatetime > self.Seconds.value(), self.GetTime() -
            # self.updatetime, self.GetTime(), self.updatetime,self.Rest))
            self.updatetime = self.GetTime()

            # logging.debug("RAMDSFDSFS:{} = {}".format(self.randomvar,int((1/self.Seconds.value()))))
            for i, plots in enumerate(self.listGraph):

                self.Update_Line(plots, str(self.listLineColor[i].currentText()), self.listLineSize[i].value(),
                                 self.listVisible[i].isChecked())

                if self.listVisible[i].isChecked() and len(self.ListSources) > i:

                    if self.check_array_value_existence(self.ListSources[i].currentIndex()):
                        if self.sum_last_values(self.RL_SamplingRate[self.ListSources[i].currentIndex()],
                                                self.listWindowSize[i].value()) is None:
                            value = self.ListSamplingRate[self.ListSources[i].currentIndex()] * self.listWindowSize[
                                i].value()
                            buffer = self.Buffer(self.ListSamplingRate[self.ListSources[i].currentIndex()],
                                                 self.Seconds.value(), self.BufferStep)
                        else:
                            value = self.sum_last_values(self.RL_SamplingRate[self.ListSources[i].currentIndex()],
                                                         self.listWindowSize[i].value())
                            buffer = self.Buffer(self.RL_SamplingRate[self.ListSources[i].currentIndex()][-1],
                                                 self.Seconds.value(), self.BufferStep)
                    else:
                        value = self.ListSamplingRate[self.ListSources[i].currentIndex()] * self.listWindowSize[
                            i].value()
                        buffer = self.Buffer(self, self.ListSamplingRate[self.ListSources[i].currentIndex()],
                                             self.Seconds.value(), self.BufferStep)

                    # print("value=" + str(value))
                    value = min(value, 40000)

                    start_time = (self.timerstamps / 1000) - (self.listWindowSize[i].value() - 1)
                    end_time = (self.timerstamps + 1000) / 1000

                    # buffer = self.Buffer(self.ListSamplingRate[self.ListSources[i].currentIndex()],
                    # self.Seconds.value(),
                    # self.randomvar)

                    # if i == 1 and len(y_values) > 0: print("value=" + str(value) + "|Buffer=" + str(buffer)+
                    # "|Show=" +str(value+buffer) + "|Number= "+str(self.randomvar))

                    x_values = self.generate_values(self, start_time, end_time, value)
                    if buffer == 0:
                        y_values = self.Window_Size_Update(self.line1[self.ListSources[i].currentIndex()], value)
                    else:
                        y_values = self.Window_Size_Update(self.line1[self.ListSources[i].currentIndex()][:buffer],value)
                    # y_values = self.resample_linear(self.line1[self.ListSources[i].currentIndex()][:buffer], 254,250)

                    # if i == 1 and len(y_values) > 0: logging.info( "\nX length: {}, Y length: {}\nBuffer: {},
                    # Number: {}, Interval: {}\n------------------------------".format( len(x_values), len(y_values),
                    # y_values[-1], self.Buffer(self.ListSamplingRate[self.ListSources[i].currentIndex()],
                    # self.Seconds.value(), self.randomvar), self.randomvar, self.Seconds.value() ))

                    #logging.debug("x->" + str(len(x_values)) + "y->" + str(len(y_values)) + "buffer->" + str(buffer))
                    if len(x_values) == len(y_values):
                        plots.setData(x_values, y_values)
                    #else:
                        #logging.debug("x->"+str(len(x_values)) + "y->"+str(len(y_values)) + "buffer->"+str(buffer))

            self.BufferStep += 1
        self.counter += 1

        stop = self.GetTime()
        # if stop - start > 0:
        # logging.info("Time Consumed in Updating Values: {} secs".format(stop - start))
        # intervalEnd = self.GetTime()
        # logging.info("Interval before Updating Values: {} secs".format(intervalEnd - self.intervalbegin))
        # self.intervalbegin = self.GetTime()

        # QtCore.QTimer.singleShot((1000/self.sampling_rate), self._update)
        QtCore.QTimer.singleShot(1, self._update)
        # time.sleep(0.01)

        # self._update()

    def RandomValues(self, y):
        liney = y
        liney.pop(0)
        liney.append(random.uniform(1, 6))
        return liney

    @Memoize
    def Buffer(self, frequencyRate, interval, number):
        if interval == 1:
            return -int(frequencyRate)

        if number >= 1 / interval:
            return 0
        # logging.debug("Frequency Rate: {}| Interval: {}| number:{}".format(frequencyRate,interval,number))
        buf = frequencyRate - ((frequencyRate * interval) * number)
        return -int(buf)

    def GetTime(self):
        return time.time()

    @Memoize
    def generate_values(self, min_val, max_val, num_values):
        if num_values <= 1:
            num_values = 2
        step = (max_val - min_val) / (num_values - 1)
        return [min_val + i * step for i in range(num_values)]

    def Save_Graph(self, graphname):
        Graph_Example = QHBoxLayout()

        frame = QFrame(self)
        frame.setFrameShape(QFrame.StyledPanel)
        Graph_Example.addWidget(frame)

        canvas = self.init_Graph()

        # title_item = pg.LabelItem(graphname)
        # canvas.addItem(title_item)
        otherplot = canvas.addPlot()

        otherplot.setDownsampling(mode='peak')

        self.listGraph.append(otherplot.plot(pen=pg.mkPen('g', width=0.5, antialias=True)))
        Graph_Example.addWidget(canvas)

        Graph_Example.addWidget(QLabel("Line Color:"))
        self.listLineColor.append(self.init_Line_Color(frame))
        Graph_Example.addWidget(self.listLineColor[-1])

        Graph_Example.addWidget(QLabel("Source:"))
        self.ListSources.append(self.init_Source(frame))
        Graph_Example.addWidget(self.ListSources[-1])

        Graph_Example.addWidget(QLabel("Line Size:"))
        self.listLineSize.append(self.init_Line_Size(frame))
        Graph_Example.addWidget(self.listLineSize[-1])

        Graph_Example.addWidget(QLabel("Window Size:"))
        self.listWindowSize.append(self.init_Window_Size(frame))
        Graph_Example.addWidget(self.listWindowSize[-1])

        self.listVisible.append(self.init_Visible_Radio(frame))
        Graph_Example.addWidget(self.listVisible[-1])

        return Graph_Example

    def init_Graph(self):
        Graph = pg.GraphicsLayoutWidget()
        return Graph

    def init_Line_Color(self, frame):
        lcolors = QComboBox(frame)
        lcolors.addItem("r")
        lcolors.addItem("g")
        lcolors.addItem("b")
        lcolors.addItem("w")
        lcolors.addItem("y")
        return lcolors

    def init_Line_Size(self, frame):
        lsize = QDoubleSpinBox(frame)
        lsize.setMinimum(0.5)
        lsize.setSingleStep(0.5)
        lsize.setValue(0.5)
        return lsize

    def init_Source(self, frame):
        source_graph = QComboBox(frame)
        i = 0
        while i != sum(self.channels):
            source_graph.addItem(self.ListChannelName[i])
            i = i + 1
        source_graph.setCurrentIndex(len(self.listLineColor) - 1)
        return source_graph

    def init_Window_Size(self, frame):
        wsize = QSpinBox()
        wsize.setMinimum(1)
        wsize.setMaximum(40)
        wsize.setSingleStep(1)
        wsize.setValue(5)
        return wsize

    def init_Visible_Radio(self, frame):
        vradio = QRadioButton("Visible", frame)
        vradio.setAutoExclusive(False)
        vradio.setChecked(True)
        return vradio

    def Add_Graph(self, graphname):
        i = self.verticalLayout_3.count()
        if i < 10:
            self.verticalLayout_3.insertLayout(i + 1, self.Save_Graph(graphname))

    def Minus_Graph(self):
        i = self.verticalLayout_3.count()
        if i > 1:
            QWidget().setLayout(self.verticalLayout_3.takeAt(i - 1))
            self.listGraph.pop(-1)
            self.listLineColor.pop(-1)
            self.listLineSize.pop(-1)
            self.listWindowSize.pop(-1)
            self.ListSources.pop(-1)
            self.listVisible.pop(-1)

    def Show_All_Graph(self):
        if self.verticalLayout_3.count() < sum(self.channels):
            while self.verticalLayout_3.count() != sum(self.channels):
                self.Add_Graph("")
        else:
            while self.verticalLayout_3.count() > sum(self.channels):
                self.Minus_Graph()
        i = 0
        while i < self.verticalLayout_3.count():
            self.ListSources[i].setCurrentIndex(i)
            i = i + 1

    def Show_Only_Graph(self, key):
        id = self.stream_name.index(key)
        if self.verticalLayout_3.count() < self.channels[id]:
            while self.verticalLayout_3.count() != self.channels[id]:
                self.Add_Graph("")
        else:
            while self.verticalLayout_3.count() > self.channels[id]:
                self.Minus_Graph()
        i = 0
        while i < self.verticalLayout_3.count():
            self.ListSources[i].setCurrentIndex(self.ListPos[id] + i)
            # self.update_window_size_spinner(0, self.sampling_rate[id], self.channels[id])
            i = i + 1

    def Update_Window(self, data):
        i = 0
        while i < sum(self.ListChannels):
            self.listWindowSize[i].value = 100
            i = i + 1

    def Update_Line(self, plot, color, size, visible):
        if not visible:
            plot.setPen("k", width=size);
            plot.clear()
            return
        plot.setPen(color, width=size);

    def Window_Size_Update(self, line, windowSize):
        # self.Frequency.setText("Frequency: " + str(self.sampling_rate) + "Hz")
        # self.Refresh.setText("Refresh: " + str(1000 / self.sampling_rate) + "ms")
        if len(line) == windowSize:
            return line
        else:
            return line[-int(windowSize):]

    def save_json(self, file_name):
        print(os.getcwd())
        with open(file_name + ".txt", "w") as outfile:
            json.dump(self.Get_layout(), outfile)

    # a code that loads data from a json file into a json file
    def load_json(self, file_name):
        with open(file_name + ".txt") as json_file:
            data = json.load(json_file)
        self.Set_layout(data)

    def Frames_Per_Second(self):
        now = self.GetTime()
        dt = now - self.lastupdate if self.lastupdate else 0
        # dt = dt - (self.Frequency.value()/1000)
        self.lastupdate = now
        if dt == 0:
            self.fps = 0
        else:
            self.fps = 1.0 / dt
        self.fps = self.fps * 0.9 + dt * 0.1
        tx = f"FPS: {self.fps:.1f}"
        self.FPS.setText(tx)

    ## Data streamed and organize functions ##
    def Data_Queue(self):
        if not self.str.empty():
            self.Lock = True
            data = self.str.get()
            print("Flag1->" + str(data))
            for key in data:
                if key in self.stream_name:
                    pos = self.ListPos[list(self.stream_name).index(key)]
                    if data[key]:
                        self.Data_Gatherer2(data[key], pos)
        else:
            # logging.debug("NOTHING")
            self.Lock = False

    def Data_Gatherer(self, data, Graph_number):
        i = 0

        for new_value in data:
            # self.line1[Graph_number]=data[new_value]

            if new_value != "Timestamps":

                # print("Flag2-> len(data[" + str(new_value) + "]) | Self.line1[" + str(Graph_number) + "]")
                samplerate = len(data[new_value]) - self.RealTimeSamplingRate[Graph_number]
                #if Graph_number == 0:
                  #  print("Sample Rate : " + str(samplerate) + "| New Value : " + str(
                       # len(data[new_value])) + "|Real time : " + str(self.RealTimeSamplingRate[Graph_number]))
                if (samplerate != 1) or (samplerate != -1):
                    if samplerate == 0:
                        samplerate = self.ListSamplingRate[Graph_number]

                    # print("Length->" + str(len(self.line1[Graph_number])))
                    # print("Line1 last Value->" + str(self.line1[Graph_number][-1]))
                    # print("Line1->" + str(self.line1[Graph_number]))
                    # print("New Data->" + str(data[new_value]))

                    if self.check_array_value_existence(Graph_number):

                        self.RL_SamplingRate[Graph_number].append(samplerate)
                        self.RL_SamplingRate[Graph_number].pop(0)
                    else:
                        self.RL_SamplingRate.append(self.generate_array(self.ListSamplingRate[Graph_number]))

                    if len(data[new_value]) != self.RealTimeSamplingRate[Graph_number]:
                        samplerate = len(data[new_value]) - self.RealTimeSamplingRate[Graph_number]
                        #print("sample:"+str(data[new_value])+"\n resample:"+str(self.resample_linear(data[
                        #new_value][:-samplerate],samplerate))) self.ListSamplingRate[Graph_number] = len(data[
                        #new_value]) - self.RealTimeSamplingRate[Graph_number] self.RealTimeSamplingRate[Graph_number] = len(data[new_value]) print("Data:", self.ListSamplingRate[Graph_number])

                    if len(data[new_value]) < 40000:
                        self.line1[Graph_number] = np.array(
                            self.fill_any(self, 40000 - len(data[new_value])) + data[new_value])
                        # self.line1[Graph_number].extend(data[new_value])
                        # self.line1[Graph_number] = self.line1[Graph_number][len(data[new_value]):]
                    elif len(data[new_value]) >= 40000:
                        self.line1[Graph_number] = np.array(data[new_value])

                    #print(self.BufferStep+"->"+1 / self.Seconds.value())
                    if self.BufferStep <= 1 / self.Seconds.value():
                        self.BufferStep = 0

                    if self.BufferStep > 1 / self.Seconds.value():
                        self.BufferStep = abs(1 / self.Seconds.value() - self.BufferStep)

                    self.RealTimeSamplingRate[Graph_number] = len(data[new_value])
                    Graph_number = Graph_number + 1

                    i += 1

    def Data_Gatherer2(self, data, Graph_number):
        i = 0
        for new_value in data:
            samplerate = len(data[new_value])
            # print("Data:"+str(self.line1[Graph_number][:-samplerate]))
            # print("Data:" + str(data[new_value]))
            # print("Sample Rate : " + str(samplerate) + "| New Value : " + str(
            # len(data[new_value])) + "|Real time : " + str(len(self.line1[Graph_number])))

            self.RealTimeSamplingRate[Graph_number] += samplerate
            if len(self.line1[Graph_number]) < 40000:
                self.line1[Graph_number] = self.line1[Graph_number] + data[new_value]
            else:
                # self.line1[Graph_number] = self.line1[Graph_number][len(data[new_value]):] + data[new_value] print(
                # "1 Length->{} | Last Value->{} | First Value->{}".format(len(self.line1[Graph_number]),self.line1[
                # Graph_number][-1],self.line1[Graph_number][0]))
                self.line1[Graph_number] = self.line1[Graph_number][samplerate:]
                # print("2 Length->{} | Last Value->{} | First Value->{}".format(len(self.line1[Graph_number]),
                # self.line1[Graph_number][-1], self.line1[Graph_number][0]))
                self.line1[Graph_number] = self.line1[Graph_number] + data[new_value]
                # print("3 Length->{} | Last Value->{} | First Value->{}".format(len(self.line1[Graph_number]),
                # self.line1[Graph_number][-1],
                # self.line1[Graph_number][0]))

            #            print("[-1]="+str(self.line1[Graph_number][-1])+"[58999]"+str(self.line1[Graph_number][-(samplerate+1)]))

            Graph_number = Graph_number + 1
            i += 1

        #if self.BufferStep <= 1 / self.Seconds.value():
        self.BufferStep = 0

        #if self.BufferStep > 1 / self.Seconds.value():
            #self.BufferStep = abs(1 / self.Seconds.value() - self.BufferStep)

    def sum_last_values(self, array, i):
        if len(array) >= i:
            # print("1-number->" + str(array[-1]))
            # print("2-number->" + str(array[-2]))
            # print("3-number->" + str(array[-3]))
            # print("4-number->" + str(array[-4]))
            # print("5-number->" + str(array[-5]))
            return sum(array[-i:])
        else:
            return None

    def check_array_value_existence(self, i):
        if i < len(self.RL_SamplingRate):
            return True
        else:
            return False

    def resize_array(self, values, new_size):
        if len(values) <= new_size:
            return values[:new_size]  # No need to resize
        else:
            interval = len(values) // new_size
            return [values[i] for i in range(0, len(values), interval)][:new_size]

    def resample_linear(self, data, new_length):
        old_length = len(data)

        if old_length == new_length:
            return data

        x_old = np.linspace(0, old_length - 1, old_length)
        x_new = np.linspace(0, old_length - 1, new_length)
        resampled_data = np.interp(x_new, x_old, data)
        return resampled_data

    def Test2(self):
        if not self.str.empty():
            data = self.str.get()
            i = 0
            for key in data:
                # print("key:" + key)
                # print("key Register" + str(self.stream_name))
                if (key in self.stream_name):
                    pos = self.ListPos[list(self.stream_name).index(key)]
                    if data[key] != []:
                        self.Data_Dist2(data[key], pos)

    def Data_Dist2(self, data, Graph_number):
        i = 0
        for new_value in data:
            self.line1[Graph_number].append(new_value)
            self.line1[Graph_number].pop(0)
            Graph_number = Graph_number + 1
            i += 1

    def count_zeros(self, lst):
        count = 0
        for item in lst:
            if item == 0:
                count += 1
        return count

    def update_window_size_spinner(self, pos, window_size, channels):
        i = pos - 1
        while i < pos + channels:
            self.listWindowSize[i].value = window_size
            i = i + 1

    def generate_array(self, num_values):
        return [num_values] * 40

    def init_stream_info(self):

        data = self.waiting_room()
        self.stream_info = data
        pos = 0
        g = 0
        i = 0
        for key in data:
            print(str(data))
            self.stream_name.append(key['Name'])
            self.channels.append(key["Channels"])
            self.sampling_rate.append(key["Sampling Rate"])
            if self.sampling_rate[g] == 0:
                self.sampling_rate[g] = 100

            self.stream_type.append("teste")  # [key]["Type"]
            self.ListPos.append(pos)
            self.ListChannelName = self.ListChannelName + self.Init_Channel_Names(key["Channels Info"])
            self.menuGraphs.addAction(self.New_Action(key['Name']))
            pos = pos + key["Channels"]
            g = g + 1
        self.str.put(1)

        while i != sum(self.channels):
            graphName = str(i) + "º " + self.ListChannelName[i]
            self.Add_Graph(graphName)
            i = i + 1
        i = 0
        p = 0
        while i != len(self.sampling_rate):
            # print("len(self.sampling_rate): " + str(len(self.sampling_rate)))
            p = 0
            while p != self.channels[i]:
                self.ListSamplingRate.append(self.sampling_rate[i])
                self.RealTimeSamplingRate.append(self.sampling_rate[i])
                # print("len(self.channels): " + str(len(self.channels)))
                p = p + 1
            i = i + 1
        # print("self.ListSamplingRate: " + str(self.ListSamplingRate))
        self.actionAll_2.triggered.connect(self.Show_All_Graph)

    def New_Action(self, key):
        NewAction = QAction(key, self)
        NewAction.triggered.connect(lambda: self.Show_Only_Graph(key))
        return NewAction

    def Init_Channel_Names(self, dictio):
        dict_keys = []
        # dict_keys.pop(0)
        for key in dictio:
            dict_keys.append(dictio[key][0])
        return dict_keys

    def Init_plots(self):
        i = 0
        while i - 1 != sum(self.channels):
            self.line1.append(self.fill_any(self, 40000))
            i = i + 1

    def Get_layout(self):
        i = 0
        Layout_info = []
        while i != self.verticalLayout_3.count():
            Layout_info1 = {"Source": self.ListSources[i].currentText(), "Color": self.listLineColor[i].currentText(),
                            "Line_Size": self.listLineSize[i].value(), "Window_Size": self.listWindowSize[i].value(),
                            "Channels": "1", "Sampling_Rate": self.ListSamplingRate[i], "Type": "EEG"}
            Layout_info.append(Layout_info1)
            i = i + 1
        return Layout_info

    def Set_layout(self, layout):
        if self.verticalLayout_3.count() < len(layout):
            while self.verticalLayout_3.count() != len(layout):
                self.Add_Graph("")
        else:
            while self.verticalLayout_3.count() > len(layout):
                self.Minus_Graph()
        for dis in layout:
            if self.ListSources[layout.index(dis)].findText(dis["Source"]) != -1:
                self.ListSources[layout.index(dis)].setCurrentText(dis["Source"])
            else:
                self.ListSources[layout.index(dis)].setCurrentIndex(-1)
            self.listLineColor[layout.index(dis)].setCurrentText(dis["Color"])
            self.listLineSize[layout.index(dis)].setValue(dis["Line_Size"])
            self.listWindowSize[layout.index(dis)].setValue(dis["Window_Size"])
            # self.ListSamplingRate[layout.index(dis)] = dis["Sampling_Rate"]

    def main(self, q):
        # print(1)
        app = QtWidgets.QApplication(sys.argv)
        # print(2)
        main = MainWindow(q)
        # print(3)
        main.show()
        # print(4)
        sys.exit(app.exec_())
        # print(5)


def Run(q):
    main = MainWindow
    # print("Run")
    main.main(main, q)
