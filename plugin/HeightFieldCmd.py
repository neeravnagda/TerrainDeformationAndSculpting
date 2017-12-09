## HeightFieldCmd.py
# This command creates the heightfield

import sys
import maya.api.OpenMaya as om
import maya.cmds as mc

#----------------------------------------------------------
# Plugin
#----------------------------------------------------------

# The name of the command
kPluginCmdName = "createHeightField"

# Flag details
shortFlagNames = ["-n","-ws","-nt","-a","-s","-f","-fo","l","fg"]
longFlagNames = ["-name","-worldSpace","-noiseType","-amplitude","-seed","-frequency","-fractalOctaves","-lacunarity","-fractalGain"]

class HeightFieldCmdClass(om.MPxCommand):

	## Constructor
	def __init__(self):
		om.MPxCommand.__init__(self)

	## This function is used to indicate the command is undoable
	def isUndoable(self):
		return True

	## The doIt function
	def doIt(self, args):
		# Initialise values
		self.name = "HeightFieldNode"
		self.lacunarity = 2.0
		self.worldSpace = False
		self.fractalOctaves = 8
		self.fractalGain = 0.5
		self.amplitude = 1.0
		self.seed = 1337
		self.frequency = 0.01
		self.noiseType = 5

		self.parseArguments(args)

		self.redoIt()

	## The redoIt function
	def redoIt(self):
		dgModifier = om.MDGModifier()
		# Create the heightfield node
		self.heightFieldNode = dgModifier.createNode("HeightFieldNode")
		dgModifier.renameNode(self.heightFieldNode, self.name)
		# Execute the ds modifier queue
		dgModifier.doIt()
		# Find the heightfield node name
		heightFieldNodeName = om.MFnDependencyNode(self.heightFieldNode).name()
		# Connect the attributes
		mc.connectAttr(self.mesh + ".worldMesh[0]", heightFieldNodeName + ".inMesh")

	## The undoIt function
	def undoIt(self):
		dgModifier = om.MDGModifier()
		dgModifier.deleteNode(self.heightFieldNode)
		dgModifier.doIt()

	## Parse the argumets
	def parseArguments(self, args):
		argData = om.MArgParser(self.syntax(), args)
		# If an argument exists, it will be the curve name. So it gets selected
		try:
			mesh_name = argData.commandArgumentString(0)
			selectionList = om.MGlobal.getSelectionListByName(name)
		except:
			selectionList = om.MGlobal.getActiveSelectionList()
		self.mesh = self.findFromSelection(selectionList)
		# Parse the flags
		if argData.isFlagSet("-n"):
			self.depthValue = argData.flagArgumentString("-n",0)
		if argData.isFlagSet("-name"):
			self.depthValue = argData.flagArgumentString("-name",0)
		if argData.isFlagSet("-ws"):
			self.widthValue = argData.flagArgumentBool("-ws",0)
		if argData.isFlagSet("-worldSpace"):
			self.widthValue = argData.flagArgumentBool("-worldSpace",0)
		if argData.isFlagSet("-nt"):
			self.name = argData.flagArgumentInt("-nt",0)
		if argData.isFlagSet("-noiseType"):
			self.name = argData.flagArgumentInt("-noiseType",0)
		if argData.isFlagSet("-a"):
			self.rebuild = argData.flagArgumentFloat("-a",0)
		if argData.isFlagSet("-amplitude"):
			self.rebuild = argData.flagArgumentFloat("-amplitude",0)
		if argData.isFlagSet("-s"):
			self.depthValue = argData.flagArgumentInt("-s",0)
		if argData.isFlagSet("-seed"):
			self.depthValue = argData.flagArgumentInt("-seed",0)
		if argData.isFlagSet("-f"):
			self.widthValue = argData.flagArgumentFloat("-f",0)
		if argData.isFlagSet("-frequency"):
			self.widthValue = argData.flagArgumentFloat("-frequency",0)
		if argData.isFlagSet("-fo"):
			self.name = argData.flagArgumentInt("-fo",0)
		if argData.isFlagSet("-fractalOctaves"):
			self.name = argData.flagArgumentInt("-fractalOctaves",0)
		if argData.isFlagSet("-l"):
			self.rebuild = argData.flagArgumentFloat("-l",0)
		if argData.isFlagSet("-lacunarity"):
			self.rebuild = argData.flagArgumentFloat("-lacunarity",0)
		if argData.isFlagSet("-fg"):
			self.rebuild = argData.flagArgumentFloat("-fg",0)
		if argData.isFlagSet("-fractalGain"):
			self.rebuild = argData.flagArgumentFloat("-fractalGain",0)

	## Find the input mesh from the selectionList
	def findFromSelection(self, selectionList):
		iterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)
		# Check if nothing is selected
		if iterator.isDone():
			print "Error nothing selected"
			return None
		else:
			dagPath = om.MDagPath()
			dagFn = om.MFnDagNode()
			curveName = None
			meshName = None
			while (not iterator.isDone()):
				dagPath = iterator.getDagPath()
				try:
					dagPath.extendToShape()
				except:
					pass
				node = dagPath.node()
				dagFn.setObject(node)
				if (dagFn.typeName == "mesh"):
					meshName = dagFn.name()
				else:
					print "Invalid selection, ignoring"
				iterator.next()
		return meshName

## Tell Maya to use Python API 2.0
def maya_useNewAPI():
	pass

## Create an instance of the command
def cmdCreator():
	return HeightFieldCmdClass()

## Define the argument and syntax for the command
def syntaxCreator():
	syntax = om.MSyntax()
	# The input mesh
	syntax.addArg(om.MSyntax.kString)
	# Flag arguments
	syntax.addFlag(shortFlagNames[0], longFlagNames[0], om.MSyntax.kString)
	syntax.addFlag(shortFlagNames[1], longFlagNames[1], om.MSyntax.kBoolean)
	syntax.addFlag(shortFlagNames[2], longFlagNames[2], om.MSyntax.kLong)
	syntax.addFlag(shortFlagNames[3], longFlagNames[3], om.MSyntax.kDouble)
	syntax.addFlag(shortFlagNames[4], longFlagNames[4], om.MSyntax.kLong)
	syntax.addFlag(shortFlagNames[5], longFlagNames[5], om.MSyntax.kDouble)
	syntax.addFlag(shortFlagNames[6], longFlagNames[6], om.MSyntax.kLong)
	syntax.addFlag(shortFlagNames[7], longFlagNames[7], om.MSyntax.kDouble)
	syntax.addFlag(shortFlagNames[8], longFlagNames[8], om.MSyntax.kDouble)

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
