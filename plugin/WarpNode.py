## WarpNode.py
# This node enables puppet warp on a region of the mesh

import sys
import maya.api.OpenMaya as om

#----------------------------------------------------------
# Plugin
#----------------------------------------------------------

# Node info
kPluginNodeName = "WarpNode"
kPluginNodeID = om.MTypeId(0x1006)

## This class is used to create the warp node
class WarpNodeClass(om.MPxNode):
	# Define the attributes
	m_terrain = om.MObject()
	m_controlPoints = om.MObject()
	m_controlPointsOriginal = om.MObject()
	m_maxRadius = om.MObject()
	m_outMesh = om.MObject()

	## Constructor
	def __init__(self):
		om.MPxNode.__init__(self)
		self.m_firstCompute = True
		self.m_controlPointsOriginal = []
		self.m_controlPointsVertices = []

	## The function that is called when the node is dirty
	# @param _plug A plug for one of the i/o attributes
	# @param _dataBlock The data used for the computations
	def compute(self, _plug, _dataBlock):
		# Check if the plug is the output mesh
		if (_plug == WarpNodeClass.m_outMesh):
			# Get handles for the attributes
			terrainDataHandle = _dataBlock.inputValue(WarpNodeClass.m_terrain)
			terrainValue = terrainDataHandle.asMesh()
			maxRadiusDataHandle = _dataBlock.inputValue(WarpNodeClass.m_maxRadius)
			maxRadiusValue = maxRadiusDataHandle.asFloat()
			controlPointsDataHandle = _dataBlock.inputArrayValue(WarpNodeClass.m_controlPoints)
			outMeshDataHandle = _dataBlock.outputValue(WarpNodeClass.m_outMesh)

			# Get all the vertices from the terrain
			inTerrainFn = om.MFnMesh(terrainValue)
			vertexPositions = inTerrainFn.getPoints()

			if self.m_firstCompute == True:
				# Get a list of the original control points positions
				controlPointsOriginalDataHandle = _dataBlock.inputArrayValue(WarpNodeClass.m_controlPointsOriginal)
				self.m_controlPointsOriginal = []
				if (len(controlPointsOriginalDataHandle) > 0):
					controlPointsOriginalDataHandle.jumpToPhysicalElement(0)
					while not controlPointsOriginalDataHandle.isDone():
						inputDataHandle = controlPointsOriginalDataHandle.inputValue()
						point = inputDataHandle.asDouble3()
						self.m_controlPointsOriginal.append(point)
						controlPointsOriginalDataHandle.next()

				numControlPoints = len(self.m_controlPointsOriginal)

				# Calculate the max radius for each control point
				maxRadiusSquared = maxRadiusValue * maxRadiusValue
				controlPointsRadii = numControlPoints * [maxRadiusSquared]
				for i in range(numControlPoints):
					distances = []
					for j in range(numControlPoints):
						dX = self.m_controlPointsOriginal[i][0] - self.m_controlPointsOriginal[j][0]
						dZ = self.m_controlPointsOriginal[i][2] - self.m_controlPointsOriginal[j][2]
						distances.append(dX*dX + dZ*dZ)
					distances.sort()
					if distances[3] < maxRadiusSquared:
						controlPointsRadii[i] = distances[3]

				# Calculate which vertices are affected
				for i in range(numControlPoints):
					tempArray = []
					# Calculate the min and max X and Z coordinates
					minX = self.m_controlPointsOriginal[i][0] - controlPointsRadii[i]
					maxX = self.m_controlPointsOriginal[i][0] + controlPointsRadii[i]
					minZ = self.m_controlPointsOriginal[i][2] - controlPointsRadii[i]
					maxZ = self.m_controlPointsOriginal[i][2] + controlPointsRadii[i]
					vertexIterator = om.MItMeshVertex(terrainValue)
					position = om.MPoint()
					while not vertexIterator.isDone():
						position = vertexIterator.position(om.MSpace.kWorld)
						if minX < position.x < maxX:
							if minZ < position.z < maxZ:
								index = vertexIterator.index()
								dX = self.m_controlPointsOriginal[i][0] - position.x
								dZ = self.m_controlPointsOriginal[i][2] - position.z
								distanceSquared = dX * dX + dZ * dZ
								if distanceSquared < controlPointsRadii[i]:
									ratio = distanceSquared / controlPointsRadii[i]
									softSelectValue = 1.0 - ratio
									tempArray.append((index, softSelectValue))
						vertexIterator.next()
					self.m_controlPointsVertices.append(tempArray)
				# Set this variable as false so this block of code is never recomputed
				self.m_firstCompute = False

			# Get a list of the control points positions
			controlPoints = []
			if (len(controlPointsDataHandle) > 0):
				controlPointsDataHandle.jumpToPhysicalElement(0)
			while not controlPointsDataHandle.isDone():
				inputDataHandle = controlPointsDataHandle.inputValue()
				point = inputDataHandle.asDouble3()
				controlPoints.append(point)
				controlPointsDataHandle.next()

			# Compute the difference in positions
			controlPointsDifference = []
			for cp, cpOriginal in zip(controlPoints,self.m_controlPointsOriginal):
				dX = cp[0] - cpOriginal[0]
				dY = cp[1] - cpOriginal[1]
				dZ = cp[2] - cpOriginal[2]
				controlPointsDifference.append(om.MVector(dX,dY,dZ))

			# Move the affected vertices
			numControlPoints = len(self.m_controlPointsOriginal)
			for i in range(numControlPoints):
				for point in self.m_controlPointsVertices[i]:
					vertexPositions[point[0]] += controlPointsDifference[i] * point[1]

			# Create a copy of the mesh to output
			meshDataFn = om.MFnMeshData()
			outTerrain = meshDataFn.create()
			outTerrainFn = om.MFnMesh()
			outTerrainFn.copy(terrainValue, outTerrain)

			# Set the output vertices
			outTerrainFn.setPoints(vertexPositions)

			# Set the output value
			outMeshDataHandle.setMObject(outTerrain)

			# Mark the output data handle as clean
			outMeshDataHandle.setClean()

#----------------------------------------------------------
# Plugin Initialisation
#----------------------------------------------------------

## This function tells Maya to use the Python API 2.0
def maya_useNewAPI():
	pass

## Create an instance of the node
def nodeCreator():
	return WarpNodeClass()

## Initialise the node attributes
def nodeInitializer():
	# Create a numeric attribute function set
	mFnNumericAttribute = om.MFnNumericAttribute()
	# Create a non-numeric attribute function set
	mFnTypedAttribute = om.MFnTypedAttribute()

	# Input node attributes
	WarpNodeClass.m_terrain = mFnTypedAttribute.create("terrain", "t", om.MFnData.kMesh)
	mFnTypedAttribute.readable = False
	mFnTypedAttribute.writable = True
	mFnTypedAttribute.storable = True
	WarpNodeClass.addAttribute(WarpNodeClass.m_terrain)

	WarpNodeClass.m_controlPoints = mFnNumericAttribute.create("controlPoints", "cp", om.MFnNumericData.k3Double)
	mFnNumericAttribute.readable = False
	mFnNumericAttribute.writable = True
	mFnNumericAttribute.storable = True
	mFnNumericAttribute.array = True
	WarpNodeClass.addAttribute(WarpNodeClass.m_controlPoints)

	WarpNodeClass.m_controlPointsOriginal = mFnNumericAttribute.create("controlPointsOriginal", "cpo", om.MFnNumericData.k3Double)
	mFnNumericAttribute.readable = False
	mFnNumericAttribute.writable = True
	mFnNumericAttribute.storable = True
	mFnNumericAttribute.array = True
	WarpNodeClass.addAttribute(WarpNodeClass.m_controlPointsOriginal)

	WarpNodeClass.m_maxRadius = mFnNumericAttribute.create("maxRadius", "mr", om.MFnNumericData.kFloat, 10.0)
	mFnNumericAttribute.readable = False
	mFnNumericAttribute.writable = True
	mFnNumericAttribute.storable = True
	WarpNodeClass.addAttribute(WarpNodeClass.m_maxRadius)

	# Output node attributes
	WarpNodeClass.m_outMesh = mFnTypedAttribute.create("outMesh", "om", om.MFnData.kMesh)
	mFnTypedAttribute.readable = True
	mFnTypedAttribute.writable = False
	mFnTypedAttribute.storable = False
	WarpNodeClass.addAttribute(WarpNodeClass.m_outMesh)

	# Connect input/output dependencies
	WarpNodeClass.attributeAffects(WarpNodeClass.m_terrain, WarpNodeClass.m_outMesh)
	WarpNodeClass.attributeAffects(WarpNodeClass.m_controlPoints, WarpNodeClass.m_outMesh)
	WarpNodeClass.attributeAffects(WarpNodeClass.m_controlPointsOriginal, WarpNodeClass.m_outMesh)
	WarpNodeClass.attributeAffects(WarpNodeClass.m_maxRadius, WarpNodeClass.m_outMesh)

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
