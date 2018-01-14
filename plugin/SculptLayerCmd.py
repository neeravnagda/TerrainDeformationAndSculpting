## SculptLayerCmd.py
# This command is used to create a sculpt layer and connect the attributes

import sys
import maya.api.OpenMaya as om
import maya.cmds as mc

#----------------------------------------------------------
# Plugin
#----------------------------------------------------------

# Flag names
shortFlagNames = ["-n", "-ss", "-co", "-mpd", "-rb"]
longFlagNames = ["-name", "-sculptStrength", "-curveOffset", "-maxProjection", "-rebuildCurve"]

# The name of the command
kPluginCmdName = "createSculptLayer"

## This class creates the command used to create a sculpt layer
class SculptLayerCmdClass(om.MPxCommand):

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
		self.name = "SculptLayerNode"
		self.sculptStrength = 1.0
		self.curveOffset = 1.1
		self.maxProjection = 1000
		self.rebuild = False
		self.parseArguments(args)
		# Check if the arguments were parsed correctly
		if self.rebuild == True:
			mc.rebuildCurve(self.curveMask, kr=0, rt=4)
		self.redoIt()

	## redoIt function, all the computation occurs here
	def redoIt(self):
		# Create a dg and dag modifier
		dgModifier = om.MDGModifier()
		dagModifier = om.MDagModifier()
		# Create the sculpt layer node
		self.sculptLayerNode = dgModifier.createNode("SculptLayerNode")
		dgModifier.renameNode(self.sculptLayerNode, self.name)
		# Get the name of the node
		dgModifier.doIt()
		nodeName = om.MFnDependencyNode(self.sculptLayerNode).name()
		# Set the parameters
		mc.setAttr(nodeName + ".sculptStrength", self.sculptStrength)
		mc.setAttr(nodeName + ".curveOffset", self.curveOffset)
		mc.setAttr(nodeName + ".maxProjectionDistance", self.maxProjection)
		# Connect the attributes
		mc.connectAttr(self.curveMask + ".worldSpace[0]", nodeName + ".curveMask")
		mc.connectAttr(self.sculptedMesh + ".worldMesh[0]", nodeName + ".sculptedMesh")
		mc.connectAttr(self.terrain + ".worldMesh[0]", nodeName + ".terrain")

	## Delete all the created nodes
	def undoIt(self):
		dgModifier = om.MDGModifier()
		dgModifier.deleteNode(self.sculptLayerNode)
		dgModifier.doIt()

	## Parse arguments and flags
	# @param args The arguments from when the command is executed
	def parseArguments(self, args):
		argData = om.MArgParser(self.syntax(), args)
		# Parse arguments
		self.curveMask = argData.commandArgumentString(0)
		self.sculptedMesh = argData.commandArgumentString(1)
		self.terrain = argData.commandArgumentString(2)
		# Parse flags
		if argData.isFlagSet("-n"):
			self.name = argData.flagArgumentString("-n", 0)
		if argData.isFlagSet("-name"):
			self.name = argData.flagArgumentString("-name", 0)
		if argData.isFlagSet("-ss"):
			self.sculptStrength = argData.flagArgumentFloat("-ss", 0)
		if argData.isFlagSet("-sculptStrength"):
			self.sculptStrength = argData.flagArgumentFloat("-sculptStrength", 0)
		if argData.isFlagSet("-co"):
			self.curveOffset = argData.flagArgumentFloat("-co", 0)
		if argData.isFlagSet("-curveOffset"):
			self.curveOffset = argData.flagArgumentFloat("-curveOffset", 0)
		if argData.isFlagSet("-mpd"):
			self.maxProjection = argData.flagArgumentFloat("-mpd", 0)
		if argData.isFlagSet("-maxProjectionDistance"):
			self.maxProjection = argData.flagArgumentFloat("-maxProjectionDistance", 0)
		if argData.isFlagSet("-rb"):
			self.rebuild = argData.flagArgumentBool("-rb", 0)
		if argData.isFlagSet("-rebuildCurve"):
			self.rebuild = argData.flagArgumentBool("-rebuildCurve", 0)

## Tell Maya to use Python API 2.0
def maya_useNewAPI():
	pass

## Create an instance of the command
def cmdCreator():
	return SculptLayerCmdClass()

## Define the argument and syntax for the command
def syntaxCreator():
	syntax = om.MSyntax()
	syntax.addArg(om.MSyntax.kString) #Curve mask
	syntax.addArg(om.MSyntax.kString) #Sculpted mesh
	syntax.addArg(om.MSyntax.kString) #Terrain
	syntax.addFlag(shortFlagNames[0], longFlagNames[0], om.MSyntax.kString)
	syntax.addFlag(shortFlagNames[1], longFlagNames[1], om.MSyntax.kDouble)
	syntax.addFlag(shortFlagNames[2], longFlagNames[2], om.MSyntax.kDouble)
	syntax.addFlag(shortFlagNames[3], longFlagNames[3], om.MSyntax.kDouble)
	syntax.addFlag(shortFlagNames[4], longFlagNames[4], om.MSyntax.kBoolean)
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
