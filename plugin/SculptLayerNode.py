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
	# Input objects
	m_terrain = om.MObject()
	m_curveMask = om.MObject()
	m_sculptedMesh = om.MObject()
	# Parameters
	m_sculptStrength = om.MObject()
	m_curveOffset = om.MObject()
	m_maxProjectionDistance = om.MObject()
	# Output
	m_outMesh = om.MObject()

	def __init__(self):
		om.MPxNode.__init__(self)
		self.m_curveOriginalPoints = None
		self.m_affectedVertices = []
		self.m_lastCurveOffset = 0.0
		self.m_lastNumVertices = 0
		self.m_lastVertex01 = []

	## The computation of the node
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

			curveOffsetDataHandle = _dataBlock.inputValue(SculptNodeClass.m_curveOffset)
			curveOffsetValue = curveOffsetDataHandle.asFloat()

			maxProjectionDistanceDataHandle = _dataBlock.inputValue(SculptNodeClass.m_maxProjectionDistance)
			maxProjectionDistanceValue = maxProjectionDistanceDataHandle.asFloat()

			outMeshDataHandle = _dataBlock.outputValue(SculptNodeClass.m_outMesh)

			# Computation
			# Create a copy of the terrain
			meshDataFn = om.MFnMeshData()
			outTerrain = meshDataFn.create()
			outTerrainFn = om.MFnMesh()
			outTerrainFn.copy(terrainValue, outTerrain)

			# Get all the vertices from the terrain
			inTerrainFn = om.MFnMesh(terrainValue)
			vertexPositions = inTerrainFn.getPoints()

			# Create a function set for the curve and find the centre
			curveFn = om.MFnNurbsCurve(curveMaskValue)
			curveCentre = self.findCurveCentre(curveFn)

			# If this is the first computation, store the curve positions as the original and compute the affectedVertices
			if self.m_curveOriginalPoints == None:
				self.m_curveOriginalPoints = curveFn.cvPositions(om.MSpace.kWorld)
				# Create a polygon iterator
				polygonIterator = om.MItMeshPolygon(terrainValue)
				# Find the closest face on the terrain
				centreFaceIndex = inTerrainFn.getClosestPoint(curveCentre, om.MSpace.kWorld)[1]
				# Calculate the affected vertices
				self.m_affectedVertices = self.findVerticesInsideCurve(polygonIterator, centreFaceIndex, curveFn, curveCentre, curveOffsetValue)
				# Store values
				self.m_lastCurveOffset = curveOffsetValue
				self.m_lastNumVertices = inTerrainFn.numVertices
				self.m_lastVertex01.append(inTerrainFn.getPoint(0, om.MSpace.kWorld))
				self.m_lastVertex01.append(inTerrainFn.getPoint(1, om.MSpace.kWorld))
			# Check if the input terrain, curve offset or the curve has changed
			else:
				recomputeAffectedVertices = False
				if self.m_lastNumVertices != inTerrainFn.numVertices:
					recomputeAffectedVertices = True
					self.m_lastNumVertices = inTerrainFn.numVertices
				elif curveOffsetValue != self.m_lastCurveOffset:
					recomputeAffectedVertices = True
					self.m_lastCurveOffset = curveOffsetValue
				elif self.m_lastVertex01[0] != inTerrainFn.getPoint(0, om.MSpace.kWorld) or self.m_lastVertex01[1] != inTerrainFn.getPoint(1, om.MSpace.kWorld):
					recomputeAffectedVertices = True
					self.m_lastVertex01[0] = inTerrainFn.getPoint(0, om.MSpace.kWorld)
					self.m_lastVertex01[1] = inTerrainFn.getPoint(1, om.MSpace.kWorld)
				elif len(self.m_curveOriginalPoints) != curveFn.numCVs:
					recomputeAffectedVertices = True
				else:
					curvePoints = curveFn.cvPositions(om.MSpace.kWorld)
					for originalPos, newPos in zip(self.m_curveOriginalPoints, curvePoints):
						if originalPos != newPos:
							recomputeAffectedVertices = True
							break
				if recomputeAffectedVertices == True:
					# Create a polygon iterator
					polygonIterator = om.MItMeshPolygon(terrainValue)
					# Find the closest face on the terrain
					centreFaceIndex = inTerrainFn.getClosestPoint(curveCentre, om.MSpace.kWorld)[1]
					self.findVerticesInsideCurve(polygonIterator, centreFaceIndex, curveFn, curveCentre, curveOffsetValue)
					self.m_curveOriginalPoints == curveFn.cvPositions(om.MSpace.kWorld)

			# Create a function set for the sculpted mesh
			sculptedMeshFn = om.MFnMesh(sculptedMeshValue)
			accelerationParams = sculptedMeshFn.autoUniformGridParams()

			# Iterate through affected vertices and project onto the sculpted mesh
			numVertices = len(self.m_affectedVertices)
			for i in xrange(numVertices):
				# Find a ray intersection from the original point in the direction of the normal to the scul mesh
				raySource = om.MFloatPoint(vertexPositions[self.m_affectedVertices[i]])
				normal = inTerrainFn.getVertexNormal(self.m_affectedVertices[i], True, om.MSpace.kWorld)
				intersection = sculptedMeshFn.closestIntersection(raySource, om.MFloatVector(normal), om.MSpace.kWorld, maxProjectionDistanceValue, False, accelParams=accelerationParams)
				# Calculate a vector from the original point to the new point
				difference = om.MPoint(intersection[0]) - vertexPositions[self.m_affectedVertices[i]]
				# Ensure the vertices are not sliding perpendicular to the normal
				if difference * normal != 0.0:
					closestPointOnCurve = curveFn.closestPoint(vertexPositions[self.m_affectedVertices[i]], space=om.MSpace.kWorld)[0]
					vertexPositions[self.m_affectedVertices[i]] += difference * sculptStrengthValue * self.calculateSoftSelectValue(curveCentre, vertexPositions[self.m_affectedVertices[i]], closestPointOnCurve)

			outTerrainFn.setPoints(vertexPositions)

			# Set the output value
			outMeshDataHandle.setMObject(outTerrain)

			# Mark the plug as clean
			outMeshDataHandle.setClean()

	## Calculate the soft selection value
	# @param _centre The centre of the curve
	# @param _vertex The vertex position to calculate for
	# @param _curvePoint The closest point on the curve to the vertex
	# @return A float value in the range [0,1]
	def calculateSoftSelectValue(self, _centre, _vertex, _curvePoint):
		centreVertexLenSquared = ((_centre.x - _vertex.x) * (_centre.x - _vertex.x)) + ((_centre.y - _vertex.y) * (_centre.y - _vertex.y)) + ((_centre.z - _vertex.z) * (_centre.z - _vertex.z))
		centreCurvePointLenSquared = ((_centre.x - _curvePoint.x) * (_centre.x - _curvePoint.x)) + ((_centre.y - _curvePoint.y) * (_centre.y - _curvePoint.y)) + ((_centre.z - _curvePoint.z) * (_centre.z - _curvePoint.z))
		ratio = centreVertexLenSquared / centreCurvePointLenSquared
		return 2 + 2.0/(ratio - 2)

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
	# @param _polygonIt The iterator for the mesh polygons
	# @param _startIndex The starting index for the iterator
	# @param _curveFn The curve function set
	# @param _curveCentre The centre of the curve
	# @param _curveOffset Offset the curve so it is still visible
	def findVerticesInsideCurve(self, _polygonIt, _startIndex, _curveFn, _curveCentre, _curveOffset):
		# Create a list and set containing face IDs
		uncheckedFaces = om.MIntArray() # This is a list of face IDs to check if they lie inside the curve
		checkedFaces = set() # This is a list of all the faces already checked, to avoid adding duplicates to uncheckedFaces
		# Add the starting index to this list and set
		uncheckedFaces.append(_startIndex)
		checkedFaces.add(_startIndex)

		# Create a list of vertex IDs that lie within the curve
		polyVertices = om.MIntArray()

		# Loop through and check the array of unchecked faces
		while (len(uncheckedFaces) > 0):
			# Set the iterator to the last item in the list of unchecked faces
			_polygonIt.setIndex(uncheckedFaces[-1])
			# Pop from the list of unchecked faces
			uncheckedFaces.remove(-1)
			# Find the centre of this face and the closest point on the curve
			faceCentre = _polygonIt.center(om.MSpace.kWorld)
			closestPointOnCurve = _curveFn.closestPoint(faceCentre, space=om.MSpace.kWorld)[0]
			# Calculate two vectors from the centre of the curve to the face and to the closest point on the curve
			centreToFace = (faceCentre - _curveCentre) * _curveOffset
			centreToCurve = closestPointOnCurve - _curveCentre
			# Use the dot product to see if the point is inside
			if centreToFace * centreToCurve.normal() < centreToCurve.length():
				# Add the vertices to the list of vertices that lie inside
				thisFaceVertices = _polygonIt.getVertices()
				polyVertices += thisFaceVertices
				# Find the connected faces and append to the list of unchecked faces
				connectedFaces = _polygonIt.getConnectedFaces()
				for faceId in connectedFaces:
					if faceId not in checkedFaces:
						uncheckedFaces.append(faceId)
						checkedFaces.add(faceId)
		self.m_affectedVertices = self.removeDuplicates(polyVertices)

	## Given a list, remove duplicate items
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

	SculptNodeClass.m_curveOffset = numericAttr.create("curveOffset", "co", om.MFnNumericData.kFloat, 1.1)
	numericAttr.readable = False
	numericAttr.writable = True
	numericAttr.storable = True
	SculptNodeClass.addAttribute(SculptNodeClass.m_curveOffset)

	SculptNodeClass.m_maxProjectionDistance = numericAttr.create("maxProjectionDistance", "mpd", om.MFnNumericData.kFloat, 1000)
	numericAttr.readable = False
	numericAttr.writable = True
	numericAttr.storable = True
	SculptNodeClass.addAttribute(SculptNodeClass.m_maxProjectionDistance)

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
	SculptNodeClass.attributeAffects(SculptNodeClass.m_curveOffset, SculptNodeClass.m_outMesh)
	SculptNodeClass.attributeAffects(SculptNodeClass.m_maxProjectionDistance, SculptNodeClass.m_outMesh)

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
