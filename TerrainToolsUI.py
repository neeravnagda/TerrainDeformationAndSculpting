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

	## Get the values from the UI and call the createCave command
	def createCave(self, *args):
		nodeName = mc.textFieldGrp(self.m_caveNameTextField, query=True, tx=True)
		if nodeName == "":
			nodeName = "CaveNode"
		depthValue = mc.floatSliderGrp(self.m_caveDepthControl, query=True, value=True)
		rebuildStatus = mc.checkBox(self.m_caveRebuildCurveCheckBox, query=True, value=True)
		mc.createCave(n=nodeName, d=depthValue, rb=rebuildStatus)

	## Get the values from the UI and call the createHeightField command
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

	## Get the values from the UI and call the createRiver command
	def createRiver(self, *args):
		nodeName = mc.textFieldGrp(self.m_riverNameTextField, query=True, tx=True)
		if nodeName == "":
			nodeName = "RiverNode"
		depthValue = mc.floatSliderGrp(self.m_riverDepthControl, query=True, value=True)
		widthValue = mc.floatSliderGrp(self.m_riverWidthControl, query=True, value=True)
		rebuildStatus = mc.checkBox(self.m_riverRebuildCurveCheckBox, query=True, value=True)
		mc.createRiver(n=nodeName, d=depthValue, w=widthValue, rb=rebuildStatus)

	## Get the values from the UI and call the combine command
	def combineCmd(self, *args):
		nodeName = mc.textFieldGrp(self.m_combineNameTextField, query=True, tx=True)
		if nodeName == "":
			nodeName = "Combine"
		mc.combine(n=nodeName)

	## Get the values from the UI and call the createSculptLayer command
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

	## Get the values from the UI and create the warp node and connect nodes
	# Note this is not written as a command as it becomes tedious to validate the input objects
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

	## Find the first selected object
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

	## Pick the terrain mesh for the sculpt layer and update the UI
	def slPickTerrain(self, *args):
		name = self.findFromSelection()
		mc.textFieldGrp(self.m_slTerrainText, edit=True, tx=name)

	## Pick the sculpted mesh  for the sculpt layer and update the UI
	def slPickSculptedMesh(self, *args):
		name = self.findFromSelection()
		mc.textFieldGrp(self.m_slSculptedMeshText, edit=True, tx=name)

	## Pick the curve mask for the sculpt layer and update the UI
	def slPickCurveMask(self, *args):
		name = self.findFromSelection()
		mc.textFieldGrp(self.m_slCurveMaskText, edit=True, tx=name)

	## Pick the terrain mesh for the warp tool and update the UI
	def warpPickTerrain(self, *args):
		name = self.findFromSelection()
		mc.textFieldGrp(self.m_warpTerrainText, edit=True, tx=name)

	## ## Pick the control points for the warp tool and update the UI
	def warpPickControlPoints(self, *args):
		selectionList = om.MGlobal.getActiveSelectionList()
		iterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)
		# Check if nothing is selected
		if iterator.isDone():
			print "Error. Nothing selected."
			self.warpControlPoints = []
		else:
			# Create a set of items so duplicates are not added
			selectedItems = set()
			dagPath = om.MDagPath()
			dagFn = om.MFnDagNode()
			# Loop through the selection
			while not iterator.isDone():
				dagPath = iterator.getDagPath()
				node = dagPath.node()
				dagFn.setObject(node)
				# 110 is a transform node. This checks if the node type is not a transform node
				if dagPath.apiType() != 110:
					# Get the parent node, which should be a transform node
					parentObj = dagFn.parent(0)
					dagFn.setObject(parentObj)
				selectedItems.add(dagFn.name())
				iterator.next()
			# Convert the set to a list as it is easier to use
			self.warpControlPoints = list(selectedItems)
		# Update the UI with the number of selected control points
		mc.intFieldGrp(self.m_warpNumControlPoints, edit=True, value1=len(self.warpControlPoints))

#---------------------------------------------------------------------------------------
# Functions for creating the UI
#---------------------------------------------------------------------------------------

	## Recreate the UI
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
		self.m_hfFrequencyControl = mc.floatSliderGrp(label="Frequency:", field=True, minValue=0.0, value=0.0)
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
		mc.separator(st="in")
		mc.text(label="Plugin status:")
		mc.separator(h=5)
		status = mc.pluginInfo("CaveNode.py", query=True, loaded=True)
		self.m_miscCaveNodeCB = mc.checkBox(label="Cave Node", value=status, onc=self.loadCaveNode)
		mc.separator(h=5)
		status = mc.pluginInfo("CaveCmd.py", query=True, loaded=True)
		self.m_miscCaveCmdCB = mc.checkBox(label="Cave Cmd", value=status, onc=self.loadCaveCmd)
		mc.separator(h=5)
		status = mc.pluginInfo("libHeightFieldNode.so", query=True, loaded=True)
		self.m_miscHeightFieldNodeCB = mc.checkBox(label="Height Field Node", value=status, onc=self.loadHeightFieldNode)
		mc.separator(h=5)
		status = mc.pluginInfo("HeightFieldCmd.py", query=True, loaded=True)
		self.m_miscHeightFieldCmdCB = mc.checkBox(label="Height Field Cmd", value=status, onc=self.loadHeightFieldCmd)
		mc.separator(h=5)
		status = mc.pluginInfo("RiverNode.py", query=True, loaded=True)
		self.m_miscRiverNodeCB = mc.checkBox(label="River Node", value=status, onc=self.loadRiverNode)
		mc.separator(h=5)
		status = mc.pluginInfo("RiverCmd.py", query=True, loaded=True)
		self.m_miscRiverCmdCB = mc.checkBox(label="River Cmd", value=status, onc=self.loadRiverCmd)
		mc.separator(h=5)
		status = mc.pluginInfo("CombineCmd.py", query=True, loaded=True)
		self.m_miscCombineCmdCB = mc.checkBox(label="Combine Cmd", value=status, onc=self.loadCombineCmd)
		mc.separator(h=5)
		status = mc.pluginInfo("SculptLayerNode.py", query=True, loaded=True)
		self.m_miscSculptLayerNodeCB = mc.checkBox(label="Sculpt Layer Node", value=status, onc=self.loadSculptLayerNode)
		mc.separator(h=5)
		status = mc.pluginInfo("SculptLayerCmd.py", query=True, loaded=True)
		self.m_miscSculptLayerCmdCB = mc.checkBox(label="Sculpt Layer Cmd", value=status, onc=self.loadSculptLayerCmd)
		mc.separator(h=5)
		status = mc.pluginInfo("WarpNode.py", query=True, loaded=True)
		self.m_miscWarpNodeCB = mc.checkBox(label="Warp Node", value=status, onc=self.loadWarpNode)
		mc.separator(h=5)
		mc.button(label="Load all", command=self.loadAllPlugins)
		mc.separator(st="out")
		mc.setParent("..")

	## Try to load all of the plugins
	def loadAllPlugins(self, *args):
		functions = [self.loadCaveCmd, self.loadCaveNode, self.loadHeightFieldCmd, self.loadHeightFieldNode, self.loadRiverCmd, self.loadRiverNode, self.loadCombineCmd, self.loadSculptLayerCmd, self.loadSculptLayerNode, self.loadWarpNode]
		for func in functions:
			try:
				func(args)
			except:
				pass

	## Load the cave node
	def loadCaveNode(self, *args):
		status = mc.pluginInfo("CaveNode.py", query=True, loaded=True)
		if status == False:
			mc.loadPlugin("CaveNode.py")
			status = mc.pluginInfo("CaveNode.py", query=True, loaded=True)
			mc.checkBox(self.m_miscCaveNodeCB, edit=True, value=status)

	## Load the cave command
	def loadCaveCmd(self, *args):
		status = mc.pluginInfo("CaveCmd.py", query=True, loaded=True)
		if status == False:
			mc.loadPlugin("CaveCmd.py")
			status = mc.pluginInfo("CaveCmd.py", query=True, loaded=True)
			mc.checkBox(self.m_miscCaveCmdCB, edit=True, value=status)

	## Load the height field node
	def loadHeightFieldNode(self, *args):
		status = mc.pluginInfo("libHeightFieldNode.so", query=True, loaded=True)
		if status == False:
			mc.loadPlugin("libHeightFieldNode.so")
			status = mc.pluginInfo("libHeightFieldNode.so", query=True, loaded=True)
			mc.checkBox(self.m_miscHeightFieldNodeCB, edit=True, value=status)

	## Load the height field command
	def loadHeightFieldCmd(self, *args):
		status = mc.pluginInfo("HeightFieldCmd.py", query=True, loaded=True)
		if status == False:
			mc.loadPlugin("HeightFieldCmd.py")
			status = mc.pluginInfo("HeightFieldCmd.py", query=True, loaded=True)
			mc.checkBox(self.m_miscHeightFieldCmdCB, edit=True, value=status)

	## Load the river node
	def loadRiverNode(self, *args):
		status = mc.pluginInfo("RiverNode.py", query=True, loaded=True)
		if status == False:
			mc.loadPlugin("RiverNode.py")
			status = mc.pluginInfo("RiverNode.py", query=True, loaded=True)
			mc.checkBox(self.m_miscRiverNodeCB, edit=True, value=status)

	## Load the river command
	def loadRiverCmd(self, *args):
		status = mc.pluginInfo("RiverCmd.py", query=True, loaded=True)
		if status == False:
			mc.loadPlugin("RiverCmd.py")
			status = mc.pluginInfo("RiverCmd.py", query=True, loaded=True)
			mc.checkBox(self.m_miscRiverCmdCB, edit=True, value=status)

	## Load the combine command
	def loadCombineCmd(self, *args):
		status = mc.pluginInfo("CombineCmd.py", query=True, loaded=True)
		if status == False:
			mc.loadPlugin("CombineCmd.py")
			status = mc.pluginInfo("CombineCmd.py", query=True, loaded=True)
			mc.checkBox(self.m_miscCombineCmdCB, edit=True, value=status)

	## Load the sculpt layer node
	def loadSculptLayerNode(self, *args):
		status = mc.pluginInfo("SculptLayerNode.py", query=True, loaded=True)
		if status == False:
			mc.loadPlugin("SculptLayerNode.py")
			status = mc.pluginInfo("SculptLayerNode.py", query=True, loaded=True)
			mc.checkBox(self.m_miscSculptLayerNodeCB, edit=True, value=status)

	## Load the sculpt layer command
	def loadSculptLayerCmd(self, *args):
		status = mc.pluginInfo("SculptLayerCmd.py", query=True, loaded=True)
		if status == False:
			mc.loadPlugin("SculptLayerCmd.py")
			status = mc.pluginInfo("SculptLayerCmd.py", query=True, loaded=True)
			mc.checkBox(self.m_miscSculptLayerCmdCB, edit=True, value=status)

	## Load the warp node
	def loadWarpNode(self, *args):
		status = mc.pluginInfo("WarpNode.py", query=True, loaded=True)
		if status == False:
			mc.loadPlugin("WarpNode.py")
			status = mc.pluginInfo("WarpNode.py", query=True, loaded=True)
			mc.checkBox(self.m_miscWarpNodeCB, edit=True, value=status)
