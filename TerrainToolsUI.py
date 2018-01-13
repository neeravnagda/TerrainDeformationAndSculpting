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
		mc.tabLayout(self.m_tabs, edit=True, tabLabel=((self.m_caveTabLayout, "Cave"),(self.m_heightFieldTabLayout, "HeightField"),(self.m_riverTabLayout, "River"),(self.m_combineTabLayout, "Combine"),(self.m_sculptLayerTabLayout, "Sculpt Layer"),(self.m_warpTabLayout, "Warp"),(self.m_miscTabLayout, "Misc")))
		mc.setParent("..")

	## A tab to create the cave
	def createCaveTab(self):
		self.m_caveTabLayout = mc.columnLayout(adjustableColumn=True)
		self.m_caveNameTextField = mc.textFieldGrp(label="Node name:", pht="CaveNode")
		self.m_caveDepthControl = mc.floatSliderGrp(label="Depth:", field=True, minValue=0.1, value=1.0)
		mc.button(label="Create Cave")
		mc.setParent("..")

	## A tab to create the height field
	def createHeightFieldTab(self):
		self.m_heightFieldTabLayout = mc.columnLayout(adjustableColumn=True)
		self.m_hfNameTextField = mc.textFieldGrp(label="Node name:", pht="HeightFieldNode")
		mc.text(label="Space type:")
		self.m_hfSpaceTypeCollection = mc.radioCollection()
		objectSpaceRB = mc.radioButton(label="Object Space", cl=self.m_hfSpaceTypeCollection, p=self.m_heightFieldTabLayout)
		worldSpaceRB = mc.radioButton(label="World Space", cl=self.m_hfSpaceTypeCollection, p=self.m_heightFieldTabLayout)
		mc.radioCollection(self.m_hfSpaceTypeCollection, edit=True, select=worldSpaceRB)
		mc.text(label="Noise type:")
		self.m_hfNoiseTypeCollection = mc.radioCollection()
		simplexNoiseRB = mc.radioButton(label="Simplex", cl=self.m_hfNoiseTypeCollection, p=self.m_heightFieldTabLayout)
		perlinNoiseRB = mc.radioButton(label="Perlin", cl=self.m_hfNoiseTypeCollection, p=self.m_heightFieldTabLayout)
		cubicNoiseRB = mc.radioButton(label="Cubic", cl=self.m_hfNoiseTypeCollection, p=self.m_heightFieldTabLayout)
		mc.radioCollection(self.m_hfNoiseTypeCollection, edit=True, select=simplexNoiseRB)
		self.m_hfAmplitudeControl = mc.floatSliderGrp(label="Amplitude:", field=True, minValue=0.0, value=1.0)
		self.m_seedControl = mc.intSliderGrp(label="Seed:", field=True, minValue=0, maxValue=10000, value=1337)
		self.m_hfFrequencyControl = mc.floatSliderGrp(label="Frequency:", field=True, minValue=0.0, value=0.01)
		self.m_hfFractalOctavesControl = mc.intSliderGrp(label="Fractal Octaves:", field=True, minValue=0, maxValue=15, value=8)
		self.m_hfLacunarityControl = mc.floatSliderGrp(label="Lacunarity:", field=True, minValue=0.0, value=2.0)
		self.m_hfFractalGainControl = mc.floatSliderGrp(label="Fractal Gain:", field=True, minValue=0.0, value=0.5)
		mc.button(label="Create Height Field")
		mc.setParent("..")

	## A tab to create the river
	def createRiverTab(self):
		self.m_riverTabLayout = mc.columnLayout(adjustableColumn=True)
		self.m_riverNameTextField = mc.textFieldGrp(label="Node name:", pht="RiverNode")
		self.m_riverDepthControl = mc.floatSliderGrp(label="Depth:", field=True, minValue=0.1, value=1.0)
		self.m_riverWidthControl = mc.floatSliderGrp(label="Width:", field=True, minValue=0.1, value=1.0)
		self.m_riverRebuildCurveCheckBox = mc.checkBox(label="Rebuild Curve")
		mc.button(label="Create River")
		mc.setParent("..")

	## A tab to create the combine tab
	def createCombineTab(self):
		self.m_combineTabLayout = mc.columnLayout(adjustableColumn=True)
		self.m_combineNameTextField = mc.textFieldGrp(label="Node name:", pht="Combine")
		mc.button(label="Combine selected")
		mc.setParent("..")

	## A tab to create the sculpt layer
	def createSculptLayerTab(self):
		self.m_sculptLayerTabLayout = mc.columnLayout(adjustableColumn=True)
		self.m_slNameTextField = mc.textFieldGrp(label="Node name:", pht="SculptLayerNode")
		self.m_slSculptStrengthControl = mc.floatSliderGrp(label="Sculpt Strength:", field=True, minValue=0.0, value=1.0)
		self.m_slCurveOffsetControl = mc.floatSliderGrp(label="Curve offset:", field=True, minValue=1.0, value=1.1)
		self.m_slMaxProjectionControl = mc.floatSliderGrp(label="Max Projection Distance:", field=True, minValue=1, maxValue=100000, value=1000)
		mc.button(label="Create Sculpt Layer")
		mc.setParent("..")

	## A tab to create the warp tool
	def createWarpTab(self):
		self.m_warpTabLayout = mc.columnLayout(adjustableColumn=True)
		self.m_warpNameTextField = mc.textFieldGrp(label="Node name:", pht="WarpNode")
		self.m_warpMaxRadius = mc.floatSliderGrp(label="Max Control Point Radius:", field=True, minValue=1.0, value=10.0)
		mc.button(label="Create Warp Node")
		mc.setParent("..")

	## A miscellaneous tab to load the plugins if not already loaded
	def createMiscTab(self):
		self.m_miscTabLayout = mc.columnLayout(adjustableColumn=True)
		mc.setParent("..")
