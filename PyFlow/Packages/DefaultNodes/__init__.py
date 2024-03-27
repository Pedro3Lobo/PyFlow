PACKAGE_NAME = 'DefaultNodes'

from collections import OrderedDict
from PyFlow.UI.UIInterfaces import IPackage

# Class based nodes
from PyFlow.Packages.DefaultNodes.Nodes.arrayElementCount import arrayElementCount
from PyFlow.Packages.DefaultNodes.Nodes.arrayElementIndex import arrayElementIndex
from PyFlow.Packages.DefaultNodes.Nodes.arraySize import arraySize
from PyFlow.Packages.DefaultNodes.Nodes.arraySlice import arraySlice
from PyFlow.Packages.DefaultNodes.Nodes.arraySum import arraySum
from PyFlow.Packages.DefaultNodes.Nodes.clearArray import clearArray
from PyFlow.Packages.DefaultNodes.Nodes.extendArray import extendArray
from PyFlow.Packages.DefaultNodes.Nodes.insertToArray import insertToArray
from PyFlow.Packages.DefaultNodes.Nodes.popFromArray import popFromArray

# Factories

_FOO_LIBS = {}
_NODES = {}
_PINS = {}
_TOOLS = OrderedDict()
_PREFS_WIDGETS = OrderedDict()
_EXPORTERS = OrderedDict()

_NODES[arrayElementCount.__name__] = arrayElementCount

_NODES={
	arrayElementCount.__name__: arrayElementCount,
	arrayElementIndex.__name__: arrayElementIndex,
	arraySize.__name__: arraySize,
	arraySlice.__name__: arraySlice,
	arraySum.__name__: arraySum,
	clearArray.__name__: clearArray,
	extendArray.__name__: extendArray,
	insertToArray.__name__: insertToArray,
	popFromArray.__name__: popFromArray,
}

class DefaultNodes(IPackage):
	def __init__(self):
		super(DefaultNodes, self).__init__()

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

