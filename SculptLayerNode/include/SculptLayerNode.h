/// @file SculptLayerNode.h
/// Create a sculpt layer

#ifndef SCULPTLAYERNODE_H__
#define SCULPTLAYERNODE_H__

#include <maya/MDataBlock.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPxNode.h>
#include <maya/MStatus.h>
#include <maya/MTypeId.h>
#include <maya/MVector.h>
#include <maya/MPointArray.h>

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
	    // Terrain
	    //-----------------------------------------------------------------------------
		static MObject m_terrain;
		//-----------------------------------------------------------------------------
	    // Curve mask
	    //-----------------------------------------------------------------------------
		static MObject m_curveMask;
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
		//-----------------------------------------------------------------------------
	  // Calculate the normal to the plane bounded by the curve
		// @param [in] _curve The curveMask
		// @param [out] The plane normal
		// @param [out] The centre point of the curve
	  //-----------------------------------------------------------------------------
		void calculatePlaneNormal(const MObject &_curve, MVector &_normal, MVector &_centrePoint);
		//-----------------------------------------------------------------------------
		// Project all the points of the mesh onto a plane
		// param [in] _normal The plane normal
		// param [in] _point A point on the plane
		// param [in out] _meshVertices The new mesh vertices
		//-----------------------------------------------------------------------------
		void projectToPlane(const MVector &_normal, const MVector &_point, MPointArray &_meshVertices);
		//-----------------------------------------------------------------------------

};

#endif
