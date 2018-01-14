## CaveCmd.py
# This command is used to create the cave geometry

import sys
import maya.api.OpenMaya as om
import maya.cmds as mc

#----------------------------------------------------------
# Plugin
#----------------------------------------------------------

# The name of the command
kPluginCmdName = "createCave"

# Flag details
shortFlagNames = ["-n","-d","-rb"]
longFlagNames = ["-name","-depth","-rebuild"]

## This class creates the command used to set up a cave
class CaveCmdClass(om.MPxCommand):

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
		self.name = "CaveNode"
		self.depthValue = 1.0
		self.rebuild = False
		# Check if the arguments were parsed correctly
		if (self.parseArguments(args) == True):
			if self.rebuild == True:
				mc.rebuildCurve(self.curveName, kr=0, rt=4)
			self.redoIt()

	## redoIt function, all the computation occurs here
	def redoIt(self):
		# Create a dg and dag modifier
		dgModifier = om.MDGModifier()
		dagModifier = om.MDagModifier()
		# Create the cave node
		self.caveNode = dgModifier.createNode("CaveNode")
		dgModifier.renameNode(self.caveNode, self.name)
		# Get the name of the node
		dgModifier.doIt()
		nodeName = om.MFnDependencyNode(self.caveNode).name()
		# Set the depth of the cave
		mc.setAttr(nodeName + ".depth", self.depthValue)
		# Create the loft node
		self.loftNode = dgModifier.createNode("loft")
		dgModifier.renameNode(self.loftNode, nodeName + "Loft")
		# Create the nurbs tesselate node for the loft
		self.loftTessellateNode = dgModifier.createNode("nurbsTessellate")
		dgModifier.renameNode(self.loftTessellateNode, nodeName + "LoftTessellate")
		# Create the planar node
		self.planarNode = dgModifier.createNode("planarTrimSurface")
		dgModifier.renameNode(self.planarNode, nodeName + "PlanarTrimSurface")
		# Create the nurbs tesselate node for the planar
		self.planarTesselateNode = dgModifier.createNode("nurbsTessellate")
		dgModifier.renameNode(self.planarTesselateNode, nodeName + "PlanarTessellate")
		# Create a mesh for the loft tesselate
		self.loftMeshTransformNode = dagModifier.createNode("mesh")
		dagModifier.renameNode(self.loftMeshTransformNode, nodeName + "LoftMeshTransform")
		# Create a mesh for the planar surface
		self.planarMeshTransformNode = dagModifier.createNode("mesh")
		dagModifier.renameNode(self.planarMeshTransformNode, nodeName + "PlanarMeshTransform")
		# Create the boolean node
		self.booleanNode = dgModifier.createNode("polyCBoolOp")
		dgModifier.renameNode(self.booleanNode, nodeName + "Combine")
		# Execute the dg queue to create the nodes
		dgModifier.doIt()
		dagModifier.doIt()
		# Get the mesh shape nodes
		self.loftMeshShapeNode = om.MFnDagNode(self.loftMeshTransformNode).child(0)
		dagModifier.renameNode(self.loftMeshShapeNode, nodeName + "LoftMeshShape")
		self.planarMeshShapeNode = om.MFnDagNode(self.planarMeshTransformNode).child(0)
		dagModifier.renameNode(self.planarMeshShapeNode, nodeName + "PlanarMeshShape")
		dagModifier.doIt()
		# Connect the attributes
		mc.connectAttr(self.curveName + ".worldSpace[0]", nodeName + ".caveEntrance")
		mc.connectAttr(self.terrainName + ".worldMesh[0]", nodeName + ".terrain")
		mc.connectAttr(nodeName + ".caveEntrance", nodeName + "Loft.inputCurve[0]",f=True)
		mc.connectAttr(nodeName + ".outCurve", nodeName + "Loft.inputCurve[1]",f=True)
		mc.connectAttr(nodeName + "Loft.outputSurface", nodeName + "LoftTessellate.inputSurface",f=True)
		mc.connectAttr(nodeName + ".outCurve", nodeName + "PlanarTrimSurface.inputCurve[0]")
		mc.connectAttr(nodeName + "PlanarTrimSurface.outputSurface", nodeName + "PlanarTessellate.inputSurface")
		mc.connectAttr(nodeName + "LoftTessellate.outputPolygon", nodeName + "LoftMeshShape.inMesh")
		mc.connectAttr(nodeName + "PlanarTessellate.outputPolygon", nodeName + "PlanarMeshShape.inMesh")
		mc.connectAttr(nodeName + "LoftMeshShape.worldMatrix[0]", nodeName + "Combine.inputMat[0]")
		mc.connectAttr(nodeName + "PlanarMeshShape.worldMatrix[0]", nodeName + "Combine.inputMat[1]")
		mc.connectAttr(nodeName + "LoftMeshShape.outMesh", nodeName + "Combine.inputPoly[0]")
		mc.connectAttr(nodeName + "PlanarMeshShape.outMesh", nodeName + "Combine.inputPoly[1]")

		# Set the tesselate attributes
		mc.setAttr(nodeName + "LoftTessellate.polygonType", 1)
		mc.setAttr(nodeName + "LoftTessellate.matchNormalDir", 1)
		mc.setAttr(nodeName + "LoftTessellate.format", 0)
		mc.setAttr(nodeName + "PlanarTessellate.polygonType", 1)
		mc.setAttr(nodeName + "PlanarTessellate.matchNormalDir", 1)
		mc.setAttr(nodeName + "PlanarTessellate.format", 0)

		# Hide history meshes
		mc.hide(nodeName + "LoftMeshShape", nodeName + "PlanarMeshShape")

	## Delete all the created nodes
	def undoIt(self):
		dgModifier = om.MDGModifier()
		dagModifier = om.MDagModifier()
		dgModifier.deleteNode(self.caveNode)
		dgModifier.deleteNode(self.loftNode)
		dgModifier.deleteNode(self.loftTessellateNode)
		dgModifier.deleteNode(self.planarNode)
		dgModifier.deleteNode(self.planarTesselateNode)
		dagModifier.deleteNode(self.loftMeshTransformNode)
		dgModifier.doIt()
		dagModifier.doIt()

	## Parse arguments and flags
	# @param args The arguments from when the command is executed
	def parseArguments(self, args):
		argData = om.MArgParser(self.syntax(), args)
		# Parse arguments
		# If arguments exist, it will be the curve and the mesh names
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
		# Parse flags
		if argData.isFlagSet("-n"):
			self.name = argData.flagArgumentString("-n",0)
		if argData.isFlagSet("-name"):
			self.name = argData.flagArgumentString("-name",0)
		if argData.isFlagSet("-d"):
			self.depthValue = argData.flagArgumentFloat("-d",0)
		if argData.isFlagSet("-depth"):
			self.depthValue = argData.flagArgumentFloat("-depth",0)
		if argData.isFlagSet("-rb"):
			self.rebuild = argData.flagArgumentBool("-rb",0)
		if argData.isFlagSet("-rebuild"):
			self.rebuild = argData.flagArgumentBool("-rebuild",0)
		return True

	## Find the mesh and curve from the selection
	# @param _selectionList Selected items from the Maya scene
	def findFromSelection(self, _selectionList):
		iterator = om.MItSelectionList(_selectionList, om.MFn.kDagNode)
		# Check if nothing is selected
		if iterator.isDone():
			print "Error. Nothing selected."
			# Return failure as nothing was selected
			return False
		else:
			dagPath = om.MDagPath()
			dagFn = om.MFnDagNode()
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
					self.curveName = dagFn.name()
				elif (dagFn.typeName == "mesh"):
					self.terrainName = dagFn.name()
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
	return CaveCmdClass()

## Define the argument and syntax for the command
def syntaxCreator():
	syntax = om.MSyntax()
	syntax.addArg(om.MSyntax.kString)
	syntax.addArg(om.MSyntax.kString)
	syntax.addFlag(shortFlagNames[0], longFlagNames[0], om.MSyntax.kString)
	syntax.addFlag(shortFlagNames[1], longFlagNames[1], om.MSyntax.kDouble)
	syntax.addFlag(shortFlagNames[2], longFlagNames[2], om.MSyntax.kBoolean)
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
