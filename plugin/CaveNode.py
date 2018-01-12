## CaveNode.py
# This node creats a secondary curve inward from the mesh

import sys
import maya.api.OpenMaya as om

#----------------------------------------------------------
# Plugin
#----------------------------------------------------------

# Node info
kPluginNodeName = "CaveNode"
kPluginNodeID = om.MTypeId(0x1004)

# Default attribute values
depthDefaultValue = 1.0

class CaveNodeClass(om.MPxNode):
	# Define the attributes
	inTerrain = om.MObject()
	inCurve = om.MObject()
	depth = om.MObject()
	outCurve = om.MObject()

	def __init__(self):
		om.MPxNode.__init__(self)

	def compute(self, _plug, _dataBlock):
		# Check if the plug is the output
		if (_plug == CaveNodeClass.outCurve):

			# Get data handles and typecast
			inCurveDataHandle = _dataBlock.inputValue(CaveNodeClass.inCurve)
			inCurveValue = inCurveDataHandle.asNurbsCurve()

			inTerrainDataHandle = _dataBlock.inputValue(CaveNodeClass.inTerrain)
			inTerrainValue = inTerrainDataHandle.asMesh()

			depthDataHandle = _dataBlock.inputValue(CaveNodeClass.depth)
			depthValue = depthDataHandle.asFloat()

			outCurveDataHandle = _dataBlock.outputValue(CaveNodeClass.outCurve)

			# Computation
			# Get the input curve data
			inCurveFn = om.MFnNurbsCurve(inCurveValue)
			curvePoints = inCurveFn.cvPositions(om.MSpace.kWorld)
			knots = inCurveFn.knots()

			# Find the curve centre
			numPoints = inCurveFn.numCVs * 2
			curveCentre = om.MVector(0.0,0.0,0.0)
			for i in range(numPoints):
				point = inCurveFn.getPointAtParam(float(i) / numPoints, om.MSpace.kWorld)
				curveCentre += om.MVector(point)
			curveCentre /= float(numPoints)
			curveCentre = om.MPoint(curveCentre)

			# Get the normal from the closest point to the centre
			meshFn = om.MFnMesh(inTerrainValue)
			normal = meshFn.getClosestNormal(curveCentre, om.MSpace.kWorld)[0]
			normal.normalize()
			# Scale the normal
			normalScaled = normal * depthValue

			# Move the curve points
			for curvePoint in curvePoints:
				# Calculate the vector from the centre to the curve point
				centreToCurvePoint = curvePoint - curveCentre
				offset = (centreToCurvePoint * normalScaled) / depthValue
				# Move the point
				curvePoint -= (offset + depthValue) * normal

			# Create a new curve data fn and object
			curveDataFn = om.MFnNurbsCurveData()
			outCurve = curveDataFn.create()
			outCurveFn = om.MFnNurbsCurve()

			outCurveFn.create(curvePoints, knots, 3, inCurveFn.form, False, False, outCurve)

			# Set the output value
			outCurveDataHandle.setMObject(outCurve)

			# Mark the plug as clean
			outCurveDataHandle.setClean()


#----------------------------------------------------------
# Plugin Initialisation
#----------------------------------------------------------

## This function tells Maya to use the Python API 2.0
def maya_useNewAPI():
	pass

## Create an instance of the node
def nodeCreator():
	return CaveNodeClass()

## Initialise the node attributes
def nodeInitializer():
	# Create a numeric and typed attribute function set
	numericAttr = om.MFnNumericAttribute()
	typedAttr = om.MFnTypedAttribute()

	# Input node attributes
	CaveNodeClass.inTerrain = typedAttr.create("terrain", "t", om.MFnData.kMesh)
	typedAttr.readable = False
	typedAttr.writable = True
	typedAttr.storable = True
	CaveNodeClass.addAttribute(CaveNodeClass.inTerrain)

	CaveNodeClass.inCurve = typedAttr.create("caveEntrance", "ce", om.MFnData.kNurbsCurve)
	typedAttr.readable = True
	typedAttr.writable = True
	typedAttr.storable = True
	CaveNodeClass.addAttribute(CaveNodeClass.inCurve)

	CaveNodeClass.depth = numericAttr.create("depth", "d", om.MFnNumericData.kFloat, depthDefaultValue)
	numericAttr.readable = False
	numericAttr.writable = True
	numericAttr.storable = True
	CaveNodeClass.addAttribute(CaveNodeClass.depth)

	# Output node attribute
	CaveNodeClass.outCurve = typedAttr.create("outCurve", "oc", om.MFnData.kNurbsCurve)
	typedAttr.readable = True
	typedAttr.writable = False
	typedAttr.storable = False
	CaveNodeClass.addAttribute(CaveNodeClass.outCurve)

	# Connect input/output dependencies
	CaveNodeClass.attributeAffects(CaveNodeClass.inTerrain, CaveNodeClass.outCurve)
	CaveNodeClass.attributeAffects(CaveNodeClass.inCurve, CaveNodeClass.outCurve)
	CaveNodeClass.attributeAffects(CaveNodeClass.depth, CaveNodeClass.outCurve)

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
