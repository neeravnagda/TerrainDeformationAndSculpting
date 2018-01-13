import maya.api.OpenMaya as om
import maya.cmds as mc

## This class creates the UI for the terrain tools
class UserInterface(object):

#---------------------------------------------------------------------------------------
# General functions for user to use
#---------------------------------------------------------------------------------------

	## Constructor
	def __init__(self):
		self.m_windowTitle = "Terrain Deformation and Sculpting Tools"
		self.m_window = mc.window()
		self.warpControlPoints = []

	## Show the window
	def start(self):
		self.close()
		self.reloadUI()
		mc.showWindow(self.m_window)

	## Close the window
	def close(self):
		if (mc.window(self.m_window, exists=True)):
			mc.deleteUI(self.m_window)

#---------------------------------------------------------------------------------------
# Functions for creating the nodes
#---------------------------------------------------------------------------------------

	def createCave(self, *args):
		nodeName = mc.textFieldGrp(self.m_caveNameTextField, query=True, tx=True)
		if nodeName == "":
			nodeName = "CaveNode"
		depthValue = mc.floatSliderGrp(self.m_caveDepthControl, query=True, value=True)
		rebuildStatus = mc.checkBox(self.m_caveRebuildCurveCheckBox, query=True, value=True)
		mc.createCave(n=nodeName, d=depthValue, rb=rebuildStatus)

	def createHeightField(self, *args):
		nodeName = mc.textFieldGrp(self.m_hfNameTextField, query=True, tx=True)
		if nodeName == "":
			nodeName = "HeightField"
		rbCollection = mc.radioCollection(self.m_hfSpaceTypeCollection, query=True, select=True)
		selectedRB = mc.radioButton(rbCollection, query=True, label=True)
		worldSpaceValue = False
		if selectedRB == "World Space":
			worldSpaceValue = True
		rbCollection = mc.radioCollection(self.m_hfNoiseTypeCollection, query=True, select=True)
		noiseTypeStr = mc.radioButton(rbCollection, query=True, label=True)
		amplitudeValue = mc.floatSliderGrp(self.m_hfAmplitudeControl, query=True, value=True)
		seedValue = mc.intSliderGrp(self.m_hfSeedControl, query=True, value=True)
		frequencyValue = mc.floatSliderGrp(self.m_hfFrequencyControl, query=True, value=True)
		fractalOctavesValue = mc.intSliderGrp(self.m_hfFractalOctavesControl, query=True, value=True)
		lacunarityValue = mc.floatSliderGrp(self.m_hfLacunarityControl, query=True, value=True)
		fractalGainValue = mc.floatSliderGrp(self.m_hfFractalGainControl, query=True, value=True)
		mc.createHeightField(n=nodeName, ws=worldSpaceValue, nt=noiseTypeStr, a=amplitudeValue, s=seedValue, f=frequencyValue, fo=fractalOctavesValue, l=lacunarityValue, fg=fractalGainValue)

	def createRiver(self, *args):
		nodeName = mc.textFieldGrp(self.m_riverNameTextField, query=True, tx=True)
		if nodeName == "":
			nodeName = "RiverNode"
		depthValue = mc.floatSliderGrp(self.m_riverDepthControl, query=True, value=True)
		widthValue = mc.floatSliderGrp(self.m_riverWidthControl, query=True, value=True)
		rebuildStatus = mc.checkBox(self.m_riverRebuildCurveCheckBox, query=True, value=True)
		mc.createRiver(n=nodeName, d=depthValue, w=widthValue, rb=rebuildStatus)

	def combineCmd(self, *args):
		nodeName = mc.textFieldGrp(self.m_combineNameTextField, query=True, tx=True)
		if nodeName == "":
			nodeName = "Combine"
		mc.combine(n=nodeName)

	def createSculptLayer(self, *args):
		terrain = mc.textFieldGrp(self.m_slTerrainText, query=True, tx=True)
		sculptedMesh = mc.textFieldGrp(self.m_slSculptedMeshText, query=True, tx=True)
		curveMask = mc.textFieldGrp(self.m_slCurveMaskText, query=True, tx=True)
		if (terrain == "") or (sculptedMesh == "") or (curveMask == ""):
			print "Error. Missing info for the input objects."
		else:
			nodeName = mc.textFieldGrp(self.m_slNameTextField, query=True, tx=True)
			if nodeName == "":
				nodeName = "SculptLayerNode"
			sculptStr = mc.floatSliderGrp(self.m_slSculptStrengthControl, query=True, value=True)
			curveOff = mc.floatSliderGrp(self.m_slCurveOffsetControl, query=True, value=True)
			maxProj = mc.floatSliderGrp(self.m_slMaxProjectionControl, query=True, value=True)
			rebuildStatus = mc.checkBox(self.m_slRebuildCurveCheckBox, query=True, value=True)
			mc.createSculptLayer(curveMask, sculptedMesh, terrain, n=nodeName, ss=sculptStr, co=curveOff, mpd=maxProj, rb=rebuildStatus)

	def createWarp(self, *args):
		terrain = mc.textFieldGrp(self.m_warpTerrainText, query=True, tx=True)
		if (terrain == "") or (self.warpControlPoints == []):
			print "Error. Missing info for the input objects"
		else:
			nodeName = mc.textFieldGrp(self.m_warpNameTextField, query=True, tx=True)
			if nodeName == "":
				nodeName = "WarpNode"
			maxCPRadius = mc.floatSliderGrp(self.m_warpMaxRadius, query=True, value=True)
			# Create the warp node
			dgModifier = om.MDGModifier()
			warpNode = dgModifier.createNode("WarpNode")
			# Get the name of the node
			dgModifier.doIt()
			nodeName = om.MFnDependencyNode(warpNode).name()
			# Connect the terrain
			mc.connectAttr(terrain + ".worldMesh[0]", nodeName + ".terrain")
			# Set the max radius
			mc.setAttr(nodeName + ".maxRadius", maxCPRadius)
			# Connect all of the control points
			numControlPoints = len(self.warpControlPoints)
			for i in range(numControlPoints):
				mc.connectAttr(self.warpControlPoints[i] + ".translate", nodeName + ".controlPoints[" + str(i) + "]")
				mc.connectAttr(self.warpControlPoints[i] + ".translate", nodeName + ".controlPointsOriginal[" + str(i) + "]")
				mc.disconnectAttr(self.warpControlPoints[i] + ".translate", nodeName + ".controlPointsOriginal[" + str(i) + "]")

#---------------------------------------------------------------------------------------
# Functions for picking UI elements
#---------------------------------------------------------------------------------------

	def findFromSelection(self):
		selectionList = om.MGlobal.getActiveSelectionList()
		iterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)
		if iterator.isDone():
			print "Error. Nothing selected."
			return ""
		else:
			dagPath = om.MDagPath()
			dagFn = om.MFnDagNode()
			dagPath = iterator.getDagPath()
			try:
				dagPath.extendToShape()
			except:
				pass
			node = dagPath.node()
			dagFn.setObject(node)
			return dagFn.name()

	def slPickTerrain(self, *args):
		name = self.findFromSelection()
		mc.textFieldGrp(self.m_slTerrainText, edit=True, tx=name)

	def slPickSculptedMesh(self, *args):
		name = self.findFromSelection()
		mc.textFieldGrp(self.m_slSculptedMeshText, edit=True, tx=name)

	def slPickCurveMask(self, *args):
		name = self.findFromSelection()
		mc.textFieldGrp(self.m_slCurveMaskText, edit=True, tx=name)

	def warpPickTerrain(self, *args):
		name = self.findFromSelection()
		mc.textFieldGrp(self.m_warpTerrainText, edit=True, tx=name)

	def warpPickControlPoints(self, *args):
		selectionList = om.MGlobal.getActiveSelectionList()
		iterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)
		if iterator.isDone():
			print "Error. Nothing selected."
			self.warpControlPoints = []
		else:
			selectedItems = set()
			dagPath = om.MDagPath()
			dagFn = om.MFnDagNode()
			while not iterator.isDone():
				dagPath = iterator.getDagPath()
				node = dagPath.node()
				dagFn.setObject(node)
				if dagPath.apiType() != 110:
					parentObj = dagFn.parent(0)
					dagFn.setObject(parentObj)
				selectedItems.add(dagFn.name())
				iterator.next()
			self.warpControlPoints = list(selectedItems)
		mc.intFieldGrp(self.m_warpNumControlPoints, edit=True, value1=len(self.warpControlPoints))


#---------------------------------------------------------------------------------------
# Functions for creating the UI
#---------------------------------------------------------------------------------------

	def reloadUI(self):
		# Create the window and the tab layout
		self.m_window = mc.window(title=self.m_windowTitle, rtf=True)
		self.m_tabs = mc.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
		# Create all the tabs
		self.createCaveTab()
		self.createHeightFieldTab()
		self.createRiverTab()
		self.createCombineTab()
		self.createSculptLayerTab()
		self.createWarpTab()
		self.createMiscTab()
		# Set the tab layout
		mc.tabLayout(self.m_tabs, edit=True, tabLabel=((self.m_caveTabLayout, "Cave"),(self.m_heightFieldTabLayout, "Height Field"),(self.m_riverTabLayout, "River"),(self.m_combineTabLayout, "Combine"),(self.m_sculptLayerTabLayout, "Sculpt Layer"),(self.m_warpTabLayout, "Warp"),(self.m_miscTabLayout, "Misc")))
		mc.setParent("..")

	## A tab to create the cave
	def createCaveTab(self):
		self.m_caveTabLayout = mc.columnLayout(adjustableColumn=True)
		mc.separator(st="in")
		self.m_caveNameTextField = mc.textFieldGrp(label="Node name:", pht="CaveNode")
		mc.separator(h=5)
		self.m_caveDepthControl = mc.floatSliderGrp(label="Depth:", field=True, minValue=0.1, value=1.0)
		mc.separator(h=5)
		self.m_caveRebuildCurveCheckBox = mc.checkBox(label="Rebuild Curve")
		mc.separator(h=5)
		mc.button(label="Create Cave", command=self.createCave)
		mc.separator(st="out")
		mc.setParent("..")

	## A tab to create the height field
	def createHeightFieldTab(self):
		self.m_heightFieldTabLayout = mc.columnLayout(adjustableColumn=True)
		mc.separator(st="in")
		self.m_hfNameTextField = mc.textFieldGrp(label="Node name:", pht="HeightFieldNode")
		mc.separator(h=5)
		mc.text(label="Space type:")
		self.m_hfSpaceTypeCollection = mc.radioCollection()
		objectSpaceRB = mc.radioButton(label="Object Space", cl=self.m_hfSpaceTypeCollection, p=self.m_heightFieldTabLayout)
		worldSpaceRB = mc.radioButton(label="World Space", cl=self.m_hfSpaceTypeCollection, p=self.m_heightFieldTabLayout)
		mc.radioCollection(self.m_hfSpaceTypeCollection, edit=True, select=worldSpaceRB)
		mc.separator(h=5)
		mc.text(label="Noise type:")
		self.m_hfNoiseTypeCollection = mc.radioCollection()
		simplexNoiseRB = mc.radioButton(label="Simplex", cl=self.m_hfNoiseTypeCollection, p=self.m_heightFieldTabLayout)
		perlinNoiseRB = mc.radioButton(label="Perlin", cl=self.m_hfNoiseTypeCollection, p=self.m_heightFieldTabLayout)
		cubicNoiseRB = mc.radioButton(label="Cubic", cl=self.m_hfNoiseTypeCollection, p=self.m_heightFieldTabLayout)
		mc.radioCollection(self.m_hfNoiseTypeCollection, edit=True, select=simplexNoiseRB)
		mc.separator(h=5)
		self.m_hfAmplitudeControl = mc.floatSliderGrp(label="Amplitude:", field=True, minValue=0.0, value=1.0)
		mc.separator(h=5)
		self.m_hfSeedControl = mc.intSliderGrp(label="Seed:", field=True, minValue=0, maxValue=10000, value=1337)
		mc.separator(h=5)
		self.m_hfFrequencyControl = mc.floatSliderGrp(label="Frequency:", field=True, minValue=0.0, value=0.01)
		mc.separator(h=5)
		self.m_hfFractalOctavesControl = mc.intSliderGrp(label="Fractal Octaves:", field=True, minValue=0, maxValue=15, value=8)
		mc.separator(h=5)
		self.m_hfLacunarityControl = mc.floatSliderGrp(label="Lacunarity:", field=True, minValue=0.0, value=2.0)
		mc.separator(h=5)
		self.m_hfFractalGainControl = mc.floatSliderGrp(label="Fractal Gain:", field=True, minValue=0.0, value=0.5)
		mc.separator(h=5)
		mc.button(label="Create Height Field", command=self.createHeightField)
		mc.separator(st="out")
		mc.setParent("..")

	## A tab to create the river
	def createRiverTab(self):
		self.m_riverTabLayout = mc.columnLayout(adjustableColumn=True)
		mc.separator(st="in")
		self.m_riverNameTextField = mc.textFieldGrp(label="Node name:", pht="RiverNode")
		mc.separator(h=5)
		self.m_riverDepthControl = mc.floatSliderGrp(label="Depth:", field=True, minValue=0.1, value=1.0)
		mc.separator(h=5)
		self.m_riverWidthControl = mc.floatSliderGrp(label="Width:", field=True, minValue=0.1, value=1.0)
		mc.separator(h=5)
		self.m_riverRebuildCurveCheckBox = mc.checkBox(label="Rebuild Curve")
		mc.separator(h=5)
		mc.button(label="Create River", command=self.createRiver)
		mc.separator(st="out")
		mc.setParent("..")

	## A tab to create the combine tab
	def createCombineTab(self):
		self.m_combineTabLayout = mc.columnLayout(adjustableColumn=True)
		mc.separator(st="in")
		self.m_combineNameTextField = mc.textFieldGrp(label="Node name:", pht="Combine")
		mc.separator(h=5)
		mc.button(label="Combine selected", command=self.combineCmd)
		mc.separator(st="out")
		mc.setParent("..")

	## A tab to create the sculpt layer
	def createSculptLayerTab(self):
		self.m_sculptLayerTabLayout = mc.columnLayout(adjustableColumn=True)
		mc.separator(st="in")
		self.m_slNameTextField = mc.textFieldGrp(label="Node name:", pht="SculptLayerNode")
		mc.separator(h=5)
		self.m_slSculptStrengthControl = mc.floatSliderGrp(label="Sculpt Strength:", field=True, minValue=0.0, value=1.0)
		mc.separator(h=5)
		self.m_slCurveOffsetControl = mc.floatSliderGrp(label="Curve offset:", field=True, minValue=1.0, value=1.1)
		mc.separator(h=5)
		self.m_slMaxProjectionControl = mc.floatSliderGrp(label="Max Projection Distance:", field=True, minValue=1, maxValue=100000, value=1000)
		mc.separator(h=5)
		self.m_slRebuildCurveCheckBox = mc.checkBox(label="Rebuild Curve")
		mc.separator(h=5)
		mc.text(label="Select the desired object and then use the buttons to store the selection")
		mc.separator(h=5)
		self.m_slTerrainText = mc.textFieldGrp(label="Terrain:", pht="Terrain", ed=False)
		mc.button(label="Pick Terrain", command=self.slPickTerrain)
		mc.separator(h=5)
		self.m_slSculptedMeshText = mc.textFieldGrp(label="Sculpted Mesh:", pht="Sculpted Mesh", ed=False)
		mc.button(label="Pick Sculpted Mesh", command=self.slPickSculptedMesh)
		mc.separator(h=5)
		self.m_slCurveMaskText = mc.textFieldGrp(label="Curve Mask:", pht="Curve Mask", ed=False)
		mc.button(label="Pick Curve Mask", command=self.slPickCurveMask)
		mc.separator(h=5)
		mc.button(label="Create Sculpt Layer", command=self.createSculptLayer)
		mc.separator(st="out")
		mc.setParent("..")

	## A tab to create the warp tool
	def createWarpTab(self):
		self.m_warpTabLayout = mc.columnLayout(adjustableColumn=True)
		mc.separator(st="in")
		self.m_warpNameTextField = mc.textFieldGrp(label="Node name:", pht="WarpNode")
		mc.separator(h=5)
		self.m_warpMaxRadius = mc.floatSliderGrp(label="Max Control Point Radius:", field=True, minValue=1.0, value=10.0)
		mc.separator(h=5)
		mc.text(label="Select the desired object(s) and then use the buttons to store the selection")
		mc.separator(h=5)
		self.m_warpTerrainText = mc.textFieldGrp(label="Terrain:", pht="Terrain", ed=False)
		mc.button(label="Pick terrain", command=self.warpPickTerrain)
		mc.separator(h=5)
		self.m_warpNumControlPoints = mc.intFieldGrp(label="Number of control points:", value1=0, en1=False)
		mc.button(label="Pick control points", command=self.warpPickControlPoints)
		mc.separator(h=5)
		mc.button(label="Create Warp Node", command=self.createWarp)
		mc.separator(st="out")
		mc.setParent("..")

	## A miscellaneous tab to load the plugins if not already loaded
	def createMiscTab(self):
		self.m_miscTabLayout = mc.columnLayout(adjustableColumn=True)
		mc.setParent("..")

# Run the code - test
x = UserInterface()
x.start()
