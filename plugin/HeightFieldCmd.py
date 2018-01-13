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
		self.worldSpaceBool = False
		self.worldSpace = 0
		self.fractalOctaves = 8
		self.fractalGain = 0.5
		self.amplitude = 1.0
		self.seed = 1337
		self.frequency = 0.01
		self.noiseTypeStr = "Simplex"
		self.parseArguments(args)
		if self.noiseTypeStr == "Perlin":
			self.noiseType = 3
		elif self.noiseTypeStr == "Cubic":
			self.noiseType = 9
		else:
			self.noiseType = 5
		if self.worldSpaceBool == True:
			self.worldSpace = 1
		else:
			self.worldSpace = 0
		self.redoIt()

	## The redoIt function
	def redoIt(self):
		dgModifier = om.MDGModifier()
		# Create the heightfield node
		self.heightFieldNode = dgModifier.createNode("HeightFieldNode")
		dgModifier.renameNode(self.heightFieldNode, self.name)
		# Execute the ds modifier queue
		dgModifier.doIt()
		nodeName = om.MFnDependencyNode(self.heightFieldNode).name()
		# Connect the attributes
		mc.connectAttr(self.meshName + ".worldMesh[0]", heightFieldNodeName + ".inMesh")
		# Set the attributes
		mc.setAttr(nodeName + ".noiseType", self.noiseType)
		mc.setAttr(nodeName + ".spaceType", self.worldSpace)
		mc.setAttr(nodeName + ".amplitude", self.amplitude)
		mc.setAttr(nodeName + ".seed", self.seed)
		mc.setAttr(nodeName + ".frequency", self.frequency)
		mc.setAttr(nodeName + ".fractalOctaves", self.fractalOctaves)
		mc.setAttr(nodeName + ".lacunarity", self.lacunarity)
		mc.setAttr(nodeName + ".fractalGain", self.fractalGain)

	## The undoIt function
	def undoIt(self):
		dgModifier = om.MDGModifier()
		dgModifier.deleteNode(self.heightFieldNode)
		dgModifier.doIt()

	## Parse the argumets
	def parseArguments(self, args):
		argData = om.MArgParser(self.syntax(), args)
		# If an argument exists, it will be the mesh name. So it gets selected
		try:
			meshName = argData.commandArgumentString(0)
			selectionList = om.MGlobal.getSelectionListByName(meshName)
		except:
			selectionList = om.MGlobal.getActiveSelectionList()
		self.findFromSelection(selectionList)
		# Parse the flags
		if argData.isFlagSet("-n"):
			self.name = argData.flagArgumentString("-n",0)
		if argData.isFlagSet("-name"):
			self.name = argData.flagArgumentString("-name",0)
		if argData.isFlagSet("-ws"):
			self.worldSpaceBool = argData.flagArgumentBool("-ws",0)
		if argData.isFlagSet("-worldSpace"):
			self.worldSpaceBool = argData.flagArgumentBool("-worldSpace",0)
		if argData.isFlagSet("-nt"):
			self.noiseTypeStr = argData.flagArgumentString("-nt",0)
		if argData.isFlagSet("-noiseType"):
			self.noiseTypeStr = argData.flagArgumentString("-noiseType",0)
		if argData.isFlagSet("-a"):
			self.amplitude = argData.flagArgumentFloat("-a",0)
		if argData.isFlagSet("-amplitude"):
			self.amplitude = argData.flagArgumentFloat("-amplitude",0)
		if argData.isFlagSet("-s"):
			self.seed = argData.flagArgumentInt("-s",0)
		if argData.isFlagSet("-seed"):
			self.seed = argData.flagArgumentInt("-seed",0)
		if argData.isFlagSet("-f"):
			self.frequency = argData.flagArgumentFloat("-f",0)
		if argData.isFlagSet("-frequency"):
			self.frequency = argData.flagArgumentFloat("-frequency",0)
		if argData.isFlagSet("-fo"):
			self.fractalOctaves = argData.flagArgumentInt("-fo",0)
		if argData.isFlagSet("-fractalOctaves"):
			self.fractalOctaves = argData.flagArgumentInt("-fractalOctaves",0)
		if argData.isFlagSet("-l"):
			self.lacunarity = argData.flagArgumentFloat("-l",0)
		if argData.isFlagSet("-lacunarity"):
			self.lacunarity = argData.flagArgumentFloat("-lacunarity",0)
		if argData.isFlagSet("-fg"):
			self.fractalGain = argData.flagArgumentFloat("-fg",0)
		if argData.isFlagSet("-fractalGain"):
			self.fractalGain = argData.flagArgumentFloat("-fractalGain",0)

	## Find the input mesh from the selectionList
	def findFromSelection(self, selectionList):
		iterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)
		# Check if nothing is selected
		if iterator.isDone():
			print "Error. Nothing selected."
			return None
		else:
			dagPath = om.MDagPath()
			dagFn = om.MFnDagNode()
			meshName = None
			while not iterator.isDone():
				dagPath = iterator.getDagPath()
				try:
					dagPath.extendToShape()
				except:
					pass
				node = dagPath.node()
				dagFn.setObject(node)
				if (dagFn.typeName == "mesh"):
					self.meshName = dagFn.name()
				else:
					print "Invalid selection, ignoring."
				iterator.next()

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
	syntax.addFlag(shortFlagNames[2], longFlagNames[2], om.MSyntax.kString)
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
