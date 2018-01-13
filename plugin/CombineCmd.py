## CombineCmd.py
# This command is used to combime geometry

import sys
import maya.api.OpenMaya as om
import maya.cmds as mc

#----------------------------------------------------------
# Plugin
#----------------------------------------------------------

# Flag names
shortFlagNames = ["-n"]
longFlagNames = ["-name"]

# The name of the command
kPluginCmdName = "combine"

class CombineCmdClass(om.MPxCommand):

	## Constructor
	def __init__(self):
		om.MPxCommand.__init__(self)

	def isUndoable(self):
		return True

	def doIt(self, args):
		# Initialise values
		self.name = "Combine"
		if (self.parseArguments(args) == True):
			self.redoIt()

	def redoIt(self):
		# Create a dg and dag modifier
		dgModifier = om.MDGModifier()
		dagModifier = om.MDagModifier()
		# Create the boolean node
		self.booleanNode = dgModifier.createNode("polyCBoolOp")
		dgModifier.renameNode(self.booleanNode, self.name)
		# Get the name of the node
		dgModifier.doIt()
		nodeName = om.MFnDependencyNode(self.booleanNode).name()
		# Connect the attributes
		numShapes = len(self.shapeNames)
		for i in range(numShapes):
			mc.connectAttr(self.shapeNames[i] + ".outMesh", nodeName + ".inputPoly[" + str(i) + "]", f=True)
			mc.connectAttr(self.shapeNames[i] + ".worldMatrix[0]", nodeName + ".inputMat[" + str(i) + "]", f=True)

	## Delete all the created nodes
	def undoIt(self):
		dgModifier = om.MDGModifier()
		dgModifier.deleteNode(self.booleanNode)
		dgModifier.doIt()

	def parseArguments(self, args):
		argData = om.MArgParser(self.syntax(), args)
		# Parse flag
		if argData.isFlagSet("-n"):
			self.name = argData.flagArgumentString("-n", 0)
		elif argData.isFlagSet("-name"):
			self.name = argData.flagArgumentString("-name", 0)
		# Parse selection
		selectionList = om.MGlobal.getActiveSelectionList()
		iterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)
		# Check if nothing is selected
		if iterator.isDone():
			print "Error. Nothing selected."
			return False
		else:
			dagPath = om.MDagPath()
			dagFn = om.MFnDagNode()
			shapeNamesSet = set()
			while (not iterator.isDone()):
				dagPath = iterator.getDagPath()
				try:
					dagPath.extendToShape()
				except:
					pass
				node = dagPath.node()
				dagFn.setObject(node)
				shapeNamesSet.add(dagFn.name())
				iterator.next()
			self.shapeNames = list(shapeNamesSet)
			return True

## Tell Maya to use Python API 2.0
def maya_useNewAPI():
	pass

## Create an instance of the command
def cmdCreator():
	return CombineCmdClass()

## Define the argument and syntax for the command
def syntaxCreator():
	syntax = om.MSyntax()
	syntax.addFlag(shortFlagNames[0], longFlagNames[0], om.MSyntax.kString)
	return syntax

## Initialise the plugin when Maya loads it
def initializePlugin(mobject):
	mplugin = om.MFnPlugin(mobject)
	try:
		mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator)
	except:
		sys.stderr.write("Failed to register command: " + kPluginCmdName)

## Uninitialise the plugin when Maya unloads it
def uninitializePlugin(mobject):
	mplugin = om.MFnPlugin(mobject)
	try:
		mplugin.deregisterCommand(kPluginCmdName)
	except:
		sys.stderr.write("Failed to unregister command: " + kPluginCmdName)
