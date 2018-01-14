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

## This class creates the command used to combine two or more meshes
class CombineCmdClass(om.MPxCommand):

	## Constructor
	def __init__(self):
		om.MPxCommand.__init__(self)

	## Let Maya know that the command is undoable
	def isUndoable(self):
		return True

	## doIt function, called once when the command is first executed
	# @param args The arguments when the command is executed
	def doIt(self, args):
		# Initialise values
		self.name = "Combine"
		# Check if arguments were parsed correctly
		if (self.parseArguments(args) == True):
			self.redoIt()

	## redoIt function, all the computation occurs here
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

	## Parse arguments and flags
	# @param args The arguments from when the command is executed
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
			# Return failure as nothing was selected
			return False
		else:
			dagPath = om.MDagPath()
			dagFn = om.MFnDagNode()
			# Create a set of items so items are not added twice
			shapeNamesSet = set()
			# Loop through the iterator
			while (not iterator.isDone()):
				dagPath = iterator.getDagPath()
				# Try to get the shape node, not the transform node
				try:
					dagPath.extendToShape()
				except:
					pass
				node = dagPath.node()
				dagFn.setObject(node)
				shapeNamesSet.add(dagFn.name())
				iterator.next()
			# Convert the set to a list as it is easier to use
			self.shapeNames = list(shapeNamesSet)
			# If the loop was successful, return True (i.e. success)
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
