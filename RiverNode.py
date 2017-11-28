## RiverNode.py
# This node creates river geometry from an input curve and surface

import sys
import maya.api.OpenMaya as om

#----------------------------------------------------------
# Plugin
#----------------------------------------------------------

# Node info
kPluginNodeName = "RiverNode"
kPluginNodeID = om.MTypeId(0x1002)

# Default attribute values
depthDefaultValue = 1.0
widthDefaultValue = 1.0

## This class is used to create the river node
class RiverNodeClass(om.MPxNode):
	# Define the attributes
	inInputCurve = om.MObject()
	inTerrain = om.MObject()
	inDepth = om.MObject()
	inWidth = om.MObject()
	outCurveL = om.MObject()
	outCurveB = om.MObject()
	outCurveR = om.MObject()

	def __init__(self):
		om.MPxNode.__init__(self)

	## The function that is called when the node is dirty
	# @param _plug A plug for one of the i/o attributes
	# @param _dataBlock The data used for the computations
	def compute(self, _plug, _dataBlock):
		# Check if the plug is the curveL attribute
		if (_plug == RiverNodeClass.outCurveL):
			# Get handles for the attributes
			inputCurveDataHandle = _dataBlock.inputValue(RiverNodeClass.inInputCurve)
			terrainDataHandle = _dataBlock.inputValue(RiverNodeClass.inTerrain)
			widthDataHandle = _dataBlock.inputValue(RiverNodeClass.inWidth)
			curveDataHandle = _dataBlock.outputValue(RiverNodeClass.outCurveL)

			# Get values for the attributes
			inputCurveValue = inputCurveDataHandle.asNurbsCurve()
			terrainValue = terrainDataHandle.asMesh()
			widthValue = widthDataHandle.asFloat() / 2.0

			# Computation
			# Create a copy of the curve
			curveData = om.MFnNurbsCurveData()
			newCurveObj = curveData.create()
			inCurveFn = om.MFnNurbsCurve(inputCurveValue)
			newCurveFn = om.MFnNurbsCurve()
			newCurve = newCurveFn.copy(inputCurveValue, newCurveObj)

			# Get the CV positions
			curveCVs = inCurveFn.cvPositions()

			for cv in curveCVs:
				cv.x -= widthValue

			newCurveFn.setCVPositions(curveCVs)

			# Set the output value
			curveDataHandle.setMObject(newCurveObj)

			# Mark the output data handle as clean
			curveDataHandle.setClean()

		# Check if the plug is the curveR attribute
		if (_plug == RiverNodeClass.outCurveR):
			# Get handles for the attributes
			inputCurveDataHandle = _dataBlock.inputValue(RiverNodeClass.inInputCurve)
			terrainDataHandle = _dataBlock.inputValue(RiverNodeClass.inTerrain)
			widthDataHandle = _dataBlock.inputValue(RiverNodeClass.inWidth)
			curveDataHandle = _dataBlock.outputValue(RiverNodeClass.outCurveR)

			# Get values for the attributes
			inputCurveValue = inputCurveDataHandle.asNurbsCurve()
			terrainValue = terrainDataHandle.asMesh()
			widthValue = widthDataHandle.asFloat() / 2.0

			# Computation
			# Create a copy of the curve
			curveData = om.MFnNurbsCurveData()
			newCurveObj = curveData.create()
			inCurveFn = om.MFnNurbsCurve(inputCurveValue)
			newCurveFn = om.MFnNurbsCurve()
			newCurve = newCurveFn.copy(inputCurveValue, newCurveObj)

			# Get the CV positions
			curveCVs = inCurveFn.cvPositions()

			for cv in curveCVs:
				cv.x += widthValue

			newCurveFn.setCVPositions(curveCVs)

			# Set the output value
			curveDataHandle.setMObject(newCurveObj)

			# Mark the output data handle as clean
			curveDataHandle.setClean()

		# Check if the plug is the curveB attribute
		if (_plug == RiverNodeClass.outCurveB):
			# Get handles for the attributes
			inputCurveDataHandle = _dataBlock.inputValue(RiverNodeClass.inInputCurve)
			terrainDataHandle = _dataBlock.inputValue(RiverNodeClass.inTerrain)
			depthDataHandle = _dataBlock.inputValue(RiverNodeClass.inDepth)
			curveDataHandle = _dataBlock.outputValue(RiverNodeClass.outCurveB)

			# Get values for the attributes
			inputCurveValue = inputCurveDataHandle.asNurbsCurve()
			terrainValue = terrainDataHandle.asMesh()
			depthValue = depthDataHandle.asFloat()

			# Computation
			# Create a copy of the curve
			curveData = om.MFnNurbsCurveData()
			newCurveObj = curveData.create()
			inCurveFn = om.MFnNurbsCurve(inputCurveValue)
			newCurveFn = om.MFnNurbsCurve()
			newCurve = newCurveFn.copy(inputCurveValue, newCurveObj)

			# Get the CV positions
			curveCVs = inCurveFn.cvPositions()

			for cv in curveCVs:
				cv.y -= depthValue

			newCurveFn.setCVPositions(curveCVs)

			# Set the output value
			curveDataHandle.setMObject(newCurveObj)

			# Mark the output data handle as clean
			curveDataHandle.setClean()

#----------------------------------------------------------
# Plugin Initialisation
#----------------------------------------------------------

## This function tells Maya to use the Python API 2.0
def maya_useNewAPI():
	pass

## Create an instance of the node
def nodeCreator():
	return RiverNodeClass()

## Initialise the node attributes
def nodeInitializer():
	# Create a numeric attribute function set
	mFnNumericAttribute = om.MFnNumericAttribute()
	# Create a non-numeric attribute function set
	mFnTypedAttribute = om.MFnTypedAttribute()

	# Input node attributes
	RiverNodeClass.inInputCurve = mFnTypedAttribute.create("inputCurve", "c", om.MFnData.kNurbsCurve)
	mFnTypedAttribute.readable = False
	mFnTypedAttribute.writable = True
	mFnTypedAttribute.storable = True
	mFnTypedAttribute.keyable = True
	mFnTypedAttribute.hidden = False

	RiverNodeClass.inTerrain = mFnTypedAttribute.create("terrain", "t", om.MFnData.kMesh)
	mFnTypedAttribute.readable = False
	mFnTypedAttribute.writable = True
	mFnTypedAttribute.storable = True
	mFnTypedAttribute.keyable = True
	mFnTypedAttribute.hidden = False

	RiverNodeClass.inDepth = mFnNumericAttribute.create("depth", "d", om.MFnNumericData.kFloat, depthDefaultValue)
	mFnNumericAttribute.readable = False
	mFnNumericAttribute.writable = True
	mFnNumericAttribute.storable = True
	mFnNumericAttribute.keyable = True
	mFnNumericAttribute.hidden = False
	#mFnNumericAttribute.minValue = 0.1

	RiverNodeClass.inWidth = mFnNumericAttribute.create("width", "w", om.MFnNumericData.kFloat, widthDefaultValue)
	mFnNumericAttribute.readable = False
	mFnNumericAttribute.writable = True
	mFnNumericAttribute.storable = True
	mFnNumericAttribute.keyable = True
	mFnNumericAttribute.hidden = False
	#mFnNumericAttribute.minValue = 0.1

	# Output node attributes
	RiverNodeClass.outCurveL = mFnTypedAttribute.create("curveL", "cl", om.MFnData.kNurbsCurve)
	mFnTypedAttribute.readable = True
	mFnTypedAttribute.writable = False
	mFnTypedAttribute.storable = False

	RiverNodeClass.outCurveB = mFnTypedAttribute.create("curveB", "cb", om.MFnData.kNurbsCurve)
	mFnTypedAttribute.readable = True
	mFnTypedAttribute.writable = False
	mFnTypedAttribute.storable = False

	RiverNodeClass.outCurveR = mFnTypedAttribute.create("curveR", "cr", om.MFnData.kNurbsCurve)
	mFnTypedAttribute.readable = True
	mFnTypedAttribute.writable = False
	mFnTypedAttribute.storable = False

	# Add the attributes to the class
	RiverNodeClass.addAttribute(RiverNodeClass.inInputCurve)
	RiverNodeClass.addAttribute(RiverNodeClass.inTerrain)
	RiverNodeClass.addAttribute(RiverNodeClass.inDepth)
	RiverNodeClass.addAttribute(RiverNodeClass.inWidth)
	RiverNodeClass.addAttribute(RiverNodeClass.outCurveL)
	RiverNodeClass.addAttribute(RiverNodeClass.outCurveB)
	RiverNodeClass.addAttribute(RiverNodeClass.outCurveR)

	# Connect input/output dependencies
	RiverNodeClass.attributeAffects(RiverNodeClass.inInputCurve, RiverNodeClass.outCurveL)
	RiverNodeClass.attributeAffects(RiverNodeClass.inTerrain, RiverNodeClass.outCurveL)
	RiverNodeClass.attributeAffects(RiverNodeClass.inWidth, RiverNodeClass.outCurveL)

	RiverNodeClass.attributeAffects(RiverNodeClass.inInputCurve, RiverNodeClass.outCurveB)
	RiverNodeClass.attributeAffects(RiverNodeClass.inTerrain, RiverNodeClass.outCurveB)
	RiverNodeClass.attributeAffects(RiverNodeClass.inDepth, RiverNodeClass.outCurveB)

	RiverNodeClass.attributeAffects(RiverNodeClass.inInputCurve, RiverNodeClass.outCurveR)
	RiverNodeClass.attributeAffects(RiverNodeClass.inTerrain, RiverNodeClass.outCurveR)
	RiverNodeClass.attributeAffects(RiverNodeClass.inWidth, RiverNodeClass.outCurveR)


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
