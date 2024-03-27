PACKAGE_NAME = 'UtilityNodes'

from collections import OrderedDict
from PyFlow.UI.UIInterfaces import IPackage

# Class based nodes
from PyFlow.Packages.UtilityNodes.Nodes.DataDispenser import DataDispenser
from PyFlow.Packages.UtilityNodes.Nodes.SaveJson import SaveJson
from PyFlow.Packages.UtilityNodes.Nodes.SaveJson2 import SaveJson2

# Factories

_FOO_LIBS = {}
_NODES = {}
_PINS = {}
_TOOLS = OrderedDict()
_PREFS_WIDGETS = OrderedDict()
_EXPORTERS = OrderedDict()

_NODES = {
	DataDispenser.__name__: DataDispenser,
	SaveJson2.__name__: SaveJson2,
	SaveJson.__name__: SaveJson,
}

class UtilityNodes(IPackage):
	def __init__(self):
		super(UtilityNodes, self).__init__()

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

