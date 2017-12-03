/// @file SculptLayerNode.h
/// Create a sculpt layer

#ifndef SCULPTLAYERNODE_H__
#define SCULPTLAYERNODE_H__

#include <maya/MDataBlock.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MStatus.h>
#include <maya/MTypeId.h>

class SculptLayer : public MPxNode
{
	public:
		static MTypeId m_id;
		static const MString typeName;
		//-----------------------------------------------------------------------------
	    // Creator when the plugin is created
	    //-----------------------------------------------------------------------------
	    static void *creator();
	    //-----------------------------------------------------------------------------
	    // Initialise when the node is created
	    //-----------------------------------------------------------------------------
	    static MStatus initialize();
	    //-----------------------------------------------------------------------------
	    // compute
	    // Calculate the difference between two meshes to allow layer strength
	    //-----------------------------------------------------------------------------
	    virtual MStatus compute(const MPlug &_plug, MDataBlock &_data);
	    //-----------------------------------------------------------------------------
	    // Constructor
	    //-----------------------------------------------------------------------------
	    SculptLayer();
		//-----------------------------------------------------------------------------
	    // destructor
	    //-----------------------------------------------------------------------------
	    virtual ~SculptLayer();

	private:
		//-----------------------------------------------------------------------------
	    // Original mesh
	    //-----------------------------------------------------------------------------
		static MObject m_originalMesh;
		//-----------------------------------------------------------------------------
	    // Sculpted mesh
	    //-----------------------------------------------------------------------------
		static MObject m_sculptedMesh;
		//-----------------------------------------------------------------------------
	    // Sculpt strength, i.e. how much of the sculpted mesh to deform
	    //-----------------------------------------------------------------------------
		static MObject m_sculptStrength;
		//-----------------------------------------------------------------------------
	    // Output terrain
	    //-----------------------------------------------------------------------------
		static MObject m_outMesh;
};

#endif
