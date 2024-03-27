from PyFlow.Packages.LSLController.Nodes.StreamTransmitter import StreamTransmitter
from PyFlow.Packages.LSLController.Nodes.StreamGrapher import StreamGrapher

PACKAGE_NAME = 'LSLController'

from collections import OrderedDict
from PyFlow.UI.UIInterfaces import IPackage

# Class based nodes
from PyFlow.Packages.LSLController.Nodes.SingleStreamReceiver import SingleStreamReceiver
from PyFlow.Packages.LSLController.Nodes.MultiStreamReceiver import MultiStreamReceiver
from PyFlow.Packages.LSLController.Nodes.SingleStreamGrapher import SingleStreamGrapher
from PyFlow.Packages.LSLController.Nodes.MultiStreamGrapher import MultiStreamGrapher
from PyFlow.Packages.LSLController.Nodes.SingleStreamSample import SingleStreamSample
# Factories

_FOO_LIBS = {}
_NODES = {}
_PINS = {}
_TOOLS = OrderedDict()
_PREFS_WIDGETS = OrderedDict()
_EXPORTERS = OrderedDict()


_NODES={
	SingleStreamReceiver.__name__: SingleStreamReceiver,
	SingleStreamSample.__name__: SingleStreamSample,
	MultiStreamReceiver.__name__: MultiStreamReceiver,
	SingleStreamGrapher.__name__: SingleStreamGrapher,
	MultiStreamGrapher.__name__: MultiStreamGrapher,
	StreamGrapher .__name__: StreamGrapher,
	StreamTransmitter.__name__: StreamTransmitter
}


class LSLController(IPackage):
	def __init__(self):
		super(LSLController, self).__init__()

	@staticmethod
	def GetExporters():
		return _EXPORTERS

	@staticmethod
	def GetFunctionLibraries():
		return _FOO_LIBS

	@staticmethod
	def GetNodeClasses():
		return _NODES

	@staticmethod
	def GetPinClasses():
		return _PINS

	@staticmethod
	def GetToolClasses():
		return _TOOLS

