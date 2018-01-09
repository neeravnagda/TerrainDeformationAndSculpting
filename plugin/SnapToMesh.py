## SnapToMesh.py
# This node keeps the control points snapped to the mesh, whilst forwarding their previous positions

import sys
import maya.api.OpenMaya as om

#----------------------------------------------------------
# Plugin
#----------------------------------------------------------

# Node info
kPluginNodeName = "SnapToMesh"
kPluginNodeID = om.MTypeId(0x1007)

## This class is used to create the warp node
class SnapToMeshClass(om.MPxNode):
	# Input attributes
	m_terrain = om.MObject()
	m_inControlPoints = om.MObject()
	# Output attributes
	m_outControlPoints = om.MObject() # This one is passed to the warp node
	m_outControlPointsFeedback = om.MObject() # This is passed back to the locators

	def __init__(self):
		om.MPxNode.__init__(self)
		#self.lastControlPoints = []

	## The function that is called when the node is dirty
	# @param _plug A plug for one of the i/o attributes
	# @param _dataBlock The data used for the computations
	def compute(self, _plug, _dataBlock):
		# Check if the plug is the output control points
		if (_plug == SnapToMeshClass.m_outControlPoints):
			# Get handles for the attributes
			terrainDataHandle = _dataBlock.inputValue(SnapToMeshClass.m_terrain)
			terrainValue = terrainDataHandle.asMesh()
			inControlPointsDataHandle = _dataBlock.inputArrayValue(SnapToMeshClass.m_inControlPoints)
			outControlPointsDataHandle = _dataBlock.outputArrayValue(SnapToMeshClass.m_outControlPoints)

			# Get a list of the control points positions
			controlPoints = []
			if (len(inControlPointsDataHandle) > 0):
				inControlPointsDataHandle.jumpToPhysicalElement(0)
			while not inControlPointsDataHandle.isDone():
				inputDataHandle = inControlPointsDataHandle.inputValue()
				point = inputDataHandle.asDouble3()
				controlPoints.append(point)
				inControlPointsDataHandle.next()

			# Set the values of the output array
			builder = outControlPointsDataHandle.builder()
			numControlPoints = len(controlPoints)
			for i in range(numControlPoints):
				dataHandle = builder.addElement(i)
				dataHandle.set3Double(controlPoints[i][0],controlPoints[i][1],controlPoints[i][2])
			outControlPointsDataHandle.set(builder)

			# Mark the output data handle as clean
			outControlPointsDataHandle.setAllClean()

		# Check if the plug is the output control points feedback
		if (_plug == SnapToMeshClass.m_outControlPointsFeedback):
			# Get handles for the attributes
			terrainDataHandle = _dataBlock.inputValue(SnapToMeshClass.m_terrain)
			terrainValue = terrainDataHandle.asMesh()
			inControlPointsDataHandle = _dataBlock.inputArrayValue(SnapToMeshClass.m_inControlPoints)
			outControlPointsDataHandle = _dataBlock.outputArrayValue(SnapToMeshClass.m_outControlPointsFeedback)

			# Get a list of the control points positions
			controlPoints = []
			if (len(inControlPointsDataHandle) > 0):
				inControlPointsDataHandle.jumpToPhysicalElement(0)
			while not inControlPointsDataHandle.isDone():
				inputDataHandle = inControlPointsDataHandle.inputValue()
				point = inputDataHandle.asDouble3()
				controlPoints.append(point)
				inControlPointsDataHandle.next()

			# Set the values of the output array
			# Set the values of the output array
			builder = outControlPointsDataHandle.builder()
			numControlPoints = len(controlPoints)
			for i in range(numControlPoints):
				dataHandle = builder.addElement(i)
				dataHandle.set3Double(controlPoints[i][0],controlPoints[i][1],controlPoints[i][2])
			outControlPointsDataHandle.set(builder)

			# Mark the output data handle as clean
			outControlPointsDataHandle.setAllClean()

#----------------------------------------------------------
# Plugin Initialisation
#----------------------------------------------------------

## This function tells Maya to use the Python API 2.0
def maya_useNewAPI():
	pass

## Create an instance of the node
def nodeCreator():
	return SnapToMeshClass()

## Initialise the node attributes
def nodeInitializer():
	# Create a numeric attribute function set
	mFnNumericAttribute = om.MFnNumericAttribute()
	# Create a non-numeric attribute function set
	mFnTypedAttribute = om.MFnTypedAttribute()

	# Input node attributes
	SnapToMeshClass.m_terrain = mFnTypedAttribute.create("terrain", "t", om.MFnData.kMesh)
	mFnTypedAttribute.readable = False
	mFnTypedAttribute.writable = True
	mFnTypedAttribute.storable = True
	SnapToMeshClass.addAttribute(SnapToMeshClass.m_terrain)

	SnapToMeshClass.m_inControlPoints = mFnNumericAttribute.create("controlPoints", "cp", om.MFnNumericData.k3Double)
	mFnNumericAttribute.readable = False
	mFnNumericAttribute.writable = True
	mFnNumericAttribute.storable = True
	mFnNumericAttribute.array = True
	SnapToMeshClass.addAttribute(SnapToMeshClass.m_inControlPoints)

	# Output node attributes
	SnapToMeshClass.m_outControlPoints = mFnNumericAttribute.create("controlPointsOut", "cpo", om.MFnNumericData.k3Double)
	mFnNumericAttribute.readable = True
	mFnNumericAttribute.writable = False
	mFnNumericAttribute.storable = False
	mFnNumericAttribute.array = True
	mFnNumericAttribute.usesArrayDataBuilder = True
	SnapToMeshClass.addAttribute(SnapToMeshClass.m_outControlPoints)

	SnapToMeshClass.m_outControlPointsFeedback = mFnNumericAttribute.create("controlPointsFeedback", "cpf", om.MFnNumericData.k3Double)
	mFnNumericAttribute.readable = True
	mFnNumericAttribute.writable = False
	mFnNumericAttribute.storable = False
	mFnNumericAttribute.array = True
	mFnNumericAttribute.usesArrayDataBuilder = True
	SnapToMeshClass.addAttribute(SnapToMeshClass.m_outControlPointsFeedback)

	# Connect input/output dependencies
	SnapToMeshClass.attributeAffects(SnapToMeshClass.m_terrain, SnapToMeshClass.m_outControlPoints)
	SnapToMeshClass.attributeAffects(SnapToMeshClass.m_inControlPoints, SnapToMeshClass.m_outControlPoints)
	SnapToMeshClass.attributeAffects(SnapToMeshClass.m_terrain, SnapToMeshClass.m_outControlPointsFeedback)
	SnapToMeshClass.attributeAffects(SnapToMeshClass.m_inControlPoints, SnapToMeshClass.m_outControlPointsFeedback)

## Initialise the plugin when Maya loads it
def initializePlugin(mobject):
	mplugin = om.MFnPlugin(mobject)
	try:
		mplugin.registerNode(kPluginNodeName, kPluginNodeID, nodeCreator, nodeInitializer)
	except:
		sys.stderr.write("Failed to register node: " + kPluginNodeName)
		raise

## Uninitialise the plugin when Maya unloads it
def uninitializePlugin(mobject):
	mplugin = om.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode(kPluginNodeID)
	except:
		sys.stderr.write("Failed to unregister node: " + kPluginNodeName)
		raise
