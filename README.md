# TerrainDeformationAndSculpting
Terrain deformation and sculpting tools

Installation and Usage:

1. Add the plugin folder to the Maya plugin path.
2. Navigate to the HeightFieldNode folder in the terminal.
3. Type "qmake" and then "make"
4. Move TerrainToolsUI.py to the Maya scripts folder.
5. Open Maya and run the UI using:
	import TerrainToolsUI
	TerrainToolsUI.UserInterface().start()
6. Load the plugins from the plugin manager or from the misc tab of the UI


Note:
The SculptLayerNode is written in both C++ and Python. The C++ version was used for a performance comparison.
The C++ version does not need to be compiled or used as there is no noticable perfomance difference between the C++ and Python versions.
