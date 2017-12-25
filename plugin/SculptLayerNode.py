## SculptLayerNode.py
# This node creats a sculpt layer

import sys
import maya.api.OpenMaya as om

#----------------------------------------------------------
# Plugin
#----------------------------------------------------------

# Node info
kPluginNodeName = "SculptLayerNode"
kPluginNodeID = om.MTypeId(0x1005)

class SculptNodeClass(om.MPxNode):
	# Define the attributes
	m_terrain = om.MObject()
	m_curveMask = om.MObject()
	m_sculptedMesh = om.MObject()
	m_sculptStrength = om.MObject()
	m_outMesh = om.MObject()

	def __init__(self):
		om.MPxNode.__init__(self)

	def compute(self, _plug, _dataBlock):
		# Check if the plug is the output
		if (_plug == SculptNodeClass.m_outMesh):

			# Get data handles and typecast
			terrainDataHandle = _dataBlock.inputValue(SculptNodeClass.m_terrain)
			terrainValue = terrainDataHandle.asMesh()

			curveMaskDataHandle = _dataBlock.inputValue(SculptNodeClass.m_curveMask)
			curveMaskValue = curveMaskDataHandle.asNurbsCurve()

			sculptedMeshDataHandle = _dataBlock.inputValue(SculptNodeClass.m_sculptedMesh)
			sculptedMeshValue = sculptedMeshDataHandle.asMesh()

			sculptStrengthDataHandle = _dataBlock.inputValue(SculptNodeClass.m_sculptStrength)
			sculptStrengthValue = sculptStrengthDataHandle.asFloat()

			outMeshDataHandle = _dataBlock.outputValue(SculptNodeClass.m_outMesh)

			# Computation
			# Create a copy of the terrain
			meshDataFn = om.MFnMeshData()
			outTerrain = meshDataFn.create()
			inTerrainFn = om.MFnMesh(terrainValue)
			outTerrainFn = om.MFnMesh()
			outTerrainFn.copy(terrainValue, outTerrain)

			# Find the centre of the curve
			curveFn = om.MFnNurbsCurve(curveMaskValue)
			curveCentre = self.findCurveCentre(curveFn)

			# Get all the vertices from the terrain
			vertexPositions = inTerrainFn.getPoints()

			# Create a polygon iterator
			polygonIterator = om.MItMeshPolygon(terrainValue)

			# Find the closest face on the terrain and set the iterator to that face
			closestPointOnTerrain = inTerrainFn.getClosestPoint(curveCentre, om.MSpace.kWorld)[1]
			polygonIterator.setIndex(closestPointOnTerrain)
			# Get the vertices for this face
			polyVertices = polygonIterator.getVertices()

			# Find the connected faces and check if they lie in the circle
			connectedFaces = polygonIterator.getConnectedFaces()
			for faceId in connectedFaces:
				polygonIterator.setIndex(faceId)
				# Find the centre of the face and the closest point on the curve to check against
				faceCentre = polygonIterator.center(om.MSpace.kWorld)
				closestPointOnCurve = curveFn.closestPoint(faceCentre, space=om.MSpace.kWorld)[0]
				# Calculate two vectors from the centre of the curve to the face and closest point on curve
				centreToFace = faceCentre - curveCentre
				centreToCurve = closestPointOnCurve - curveCentre
				# Use the dot product to see if the point is inside
				if centreToFace * centreToCurve.normal() < centreToCurve.length():
					thisFaceVertices = polygonIterator.getVertices()
					polyVertices += thisFaceVertices

			# Remove duplicates to reduce computation
			polyVertices = self.removeDuplicates(polyVertices)

			# Iterate through poly vertices and offset to test which verts were affected
			numVertices = len(polyVertices)
			for i in xrange(numVertices):
				vertexPositions[polyVertices[i]][1] += sculptStrengthValue

			outTerrainFn.setPoints(vertexPositions)

			# Set the output value
			outMeshDataHandle.setMObject(outTerrain)

			# Mark the plug as clean
			outMeshDataHandle.setClean()

	## Find the centre of a curve
	# @param _curveFn The curve function set
	# @return The centre of the curve as a MPoint
	def findCurveCentre(self, _curveFn):
		curvePoints = om.MPointArray()
		numPoints = _curveFn.numCVs * 2
		curvePoints.setLength(numPoints)
		curveCentre = om.MVector(0.0,0.0,0.0)
		for i in range(numPoints):
			point = _curveFn.getPointAtParam(float(i) / numPoints, om.MSpace.kWorld)
			curvePoints[i] = point
			curveCentre += om.MVector(point)
		# Find the centre of the curve and then typecast to MPoint
		curveCentre /= float(numPoints)
		return om.MPoint(curveCentre)

	## Find all the vertices inside the curve
	# @param _polygonIterator The iterator for the mesh polygons
	# @param _startIndex The starting index for the iterator
	# @return A list of indices of vertices that lie within the curve
	def findVerticesInsideCurve(self, _polygonIterator, _startIndex):
		pass


	## Given a list, remove items
	# @param _list The list containing duplicates
	# @return A new list without any duplicates
	def removeDuplicates(self, _list):
		newList = []
		seenElements = set()
		for item in _list:
			if item not in seenElements:
				newList.append(item)
				seenElements.add(item)
		return newList

#----------------------------------------------------------
# Plugin Initialisation
#----------------------------------------------------------

## This function tells Maya to use the Python API 2.0
def maya_useNewAPI():
	pass

## Create an instance of the node
def nodeCreator():
	return SculptNodeClass()

## Initialise the node attributes
def nodeInitializer():
	# Create a numeric and typed attribute function set
	numericAttr = om.MFnNumericAttribute()
	typedAttr = om.MFnTypedAttribute()

	# Input node attributes
	SculptNodeClass.m_terrain = typedAttr.create("terrain", "t", om.MFnData.kMesh)
	typedAttr.readable = False
	typedAttr.writable = True
	typedAttr.storable = True
	SculptNodeClass.addAttribute(SculptNodeClass.m_terrain)

	SculptNodeClass.m_curveMask = typedAttr.create("curveMask", "cm", om.MFnData.kNurbsCurve)
	typedAttr.readable = False
	typedAttr.writable = True
	typedAttr.storable = True
	SculptNodeClass.addAttribute(SculptNodeClass.m_curveMask)

	SculptNodeClass.m_sculptedMesh = typedAttr.create("sculptedMesh", "sm", om.MFnData.kMesh)
	typedAttr.readable = False
	typedAttr.writable = True
	typedAttr.storable = True
	SculptNodeClass.addAttribute(SculptNodeClass.m_sculptedMesh)

	SculptNodeClass.m_sculptStrength = numericAttr.create("sculptStrength", "ss", om.MFnNumericData.kFloat, 1.0)
	numericAttr.readable = False
	numericAttr.writable = True
	numericAttr.storable = True
	SculptNodeClass.addAttribute(SculptNodeClass.m_sculptStrength)

	# Output node attribute
	SculptNodeClass.m_outMesh = typedAttr.create("outMesh", "m", om.MFnData.kMesh)
	typedAttr.readable = True
	typedAttr.writable = False
	typedAttr.storable = False
	SculptNodeClass.addAttribute(SculptNodeClass.m_outMesh)

	# Connect input/output dependencies
	SculptNodeClass.attributeAffects(SculptNodeClass.m_terrain, SculptNodeClass.m_outMesh)
	SculptNodeClass.attributeAffects(SculptNodeClass.m_curveMask, SculptNodeClass.m_outMesh)
	SculptNodeClass.attributeAffects(SculptNodeClass.m_sculptedMesh, SculptNodeClass.m_outMesh)
	SculptNodeClass.attributeAffects(SculptNodeClass.m_sculptStrength, SculptNodeClass.m_outMesh)

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
