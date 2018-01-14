## RiverCmd.py
# This command is used to create a river node and lofted surface

import sys
import maya.api.OpenMaya as om
import maya.cmds as mc

#----------------------------------------------------------
# Plugin
#----------------------------------------------------------

# The name of the command
kPluginCmdName = "createRiver"

# Flag details
shortFlagNames = ["-n","-d","-w","-rb"]
longFlagNames = ["-name","-depth","-width","-rebuild"]

## This class creates the command to create a river
class RiverCmdClass(om.MPxCommand):

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
		self.depthValue = 1.0
		self.widthValue = 1.0
		self.name = "RiverNode"
		self.curve = None
		self.rebuild = False
		if (self.parseArguments(args) == True):
			if self.rebuild == True:
				mc.rebuildCurve(self.curve, kr=0, rt=4)
			self.redoIt()

	## redoIt function, all the computation occurs here
	def redoIt(self):
		# Create a dg modifier
		dgModifier = om.MDGModifier()
		# Create the river node
		self.riverNode = dgModifier.createNode("RiverNode")
		dgModifier.renameNode(self.riverNode, self.name)
		# Get the name of the node
		dgModifier.doIt()
		nodeName = om.MFnDependencyNode(self.riverNode).name()
		# Create the loft node
		self.loftNode = dgModifier.createNode("loft")
		dgModifier.renameNode(self.loftNode, nodeName + "Loft")
		# Create the nurbs tesselate node
		self.nurbsTesselateNode = dgModifier.createNode("nurbsTessellate")
		dgModifier.renameNode(self.nurbsTesselateNode, nodeName + "NurbsTesselate")
		# Execute the dg modifier queues to create the nodes
		dgModifier.doIt()
		# Connect attributes
		mc.connectAttr(self.curve + ".worldSpace[0]", nodeName + ".inputCurve")
		mc.connectAttr(self.mesh + ".outMesh", nodeName + ".terrain")
		mc.connectAttr(nodeName + ".curveL", nodeName + "Loft.inputCurve[0]")
		mc.connectAttr(nodeName + ".curveB", nodeName + "Loft.inputCurve[1]")
		mc.connectAttr(nodeName + ".curveR", nodeName + "Loft.inputCurve[2]")
		mc.connectAttr(nodeName + "Loft.outputSurface", nodeName + "NurbsTesselate.inputSurface")
		# Set the nurbs tesselate to quads
		mc.setAttr(nodeName + "NurbsTesselate.polygonType", 1)

	## Delete all the created nodes
	def undoIt(self):
		# Create a dg and dag modifier
		dgModifier = om.MDGModifier()
		# Delete the nodes
		dgModifier.deleteNode(self.riverNode)
		dgModifier.deleteNode(self.loftNode)
		dgModifier.deleteNode(self.nurbsTesselateNode)
		# Execute the dag and dg modifier queues
		dgModifier.doIt()

	## Parse arguments and flags
	# @param args The arguments from when the command is executed
	def parseArguments(self, args):
		argData = om.MArgParser(self.syntax(), args)
		# If an argument exists, it will be the curve name and the mesh name
		try:
			name0 = argData.commandArgumentString(0)
			name1 = argData.commandArgumentString(1)
			selectionList = om.MGlobal.getSelectionListByName(name0)
			selectionList2 = om.MGlobal.getSelectionListByName(name1)
			selectionList.merge(selectionList2)
		except:
			selectionList = om.MGlobal.getActiveSelectionList()
		status = self.findFromSelection(selectionList)
		if status == False:
			return False
		# Parse the flags
		if argData.isFlagSet("-n"):
			self.name = argData.flagArgumentString("-n",0)
		if argData.isFlagSet("-name"):
			self.name = argData.flagArgumentString("-name",0)
		if argData.isFlagSet("-d"):
			self.depthValue = argData.flagArgumentFloat("-d",0)
		if argData.isFlagSet("-depth"):
			self.depthValue = argData.flagArgumentFloat("-depth",0)
		if argData.isFlagSet("-w"):
			self.widthValue = argData.flagArgumentFloat("-w",0)
		if argData.isFlagSet("-width"):
			self.widthValue = argData.flagArgumentFloat("-width",0)
		if argData.isFlagSet("-rb"):
			self.rebuild = argData.flagArgumentBool("-rb",0)
		if argData.isFlagSet("-rebuild"):
			self.rebuild = argData.flagArgumentBool("-rebuild",0)
		return True

	## Find the mesh and curve from the selection
	# @param selectionList Selected items from the Maya scene
	def findFromSelection(self, selectionList):
		iterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)
		# Check if nothing is selected
		if iterator.isDone():
			print "Error nothing selected"
			# Return failure as nothing was selected
			return False
		else:
			dagPath = om.MDagPath()
			dagFn = om.MFnDagNode()
			curveName = None
			meshName = None
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
				# Check the type of node
				if (dagFn.typeName == "nurbsCurve"):
					self.curve = dagFn.name()
				elif (dagFn.typeName == "mesh"):
					self.mesh = dagFn.name()
				else:
					print "Invalid selection, ignoring"
				iterator.next()
			# If the loop was successful, return True (i.e. success)
			return True

## Tell Maya to use Python API 2.0
def maya_useNewAPI():
	pass

## Create an instance of the command
def cmdCreator():
	return RiverCmdClass()

## Define the argument and syntax for the command
def syntaxCreator():
	syntax = om.MSyntax()
	syntax.addArg(om.MSyntax.kString)
	syntax.addArg(om.MSyntax.kString)
	syntax.addFlag(shortFlagNames[0], longFlagNames[0], om.MSyntax.kString)
	syntax.addFlag(shortFlagNames[1], longFlagNames[1], om.MSyntax.kDouble)
	syntax.addFlag(shortFlagNames[2], longFlagNames[2], om.MSyntax.kDouble)
	syntax.addFlag(shortFlagNames[3], longFlagNames[3], om.MSyntax.kBoolean)
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
