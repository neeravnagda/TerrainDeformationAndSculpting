/// @file SculptLayerNode.h
/// Create a sculpt layer

#ifndef SCULPTLAYERNODE_H__
#define SCULPTLAYERNODE_H__

#include <unordered_set>
#include <maya/MDataBlock.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MItMeshPolygon.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPoint.h>
#include <maya/MPxNode.h>
#include <maya/MStatus.h>
#include <maya/MTypeId.h>

class SculptLayer : public MPxNode
{
public:
    //-----------------------------------------------------------------------------
    // The ID of the node
    //-----------------------------------------------------------------------------
    static MTypeId m_id;
    //-----------------------------------------------------------------------------
    // The name of the node
    //-----------------------------------------------------------------------------
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
    // Curve offset to see the curve
    //-----------------------------------------------------------------------------
    static MObject m_curveOffset;
    //-----------------------------------------------------------------------------
    // Max projection distance
    //-----------------------------------------------------------------------------
    static MObject m_maxProjectionDistance;
    //-----------------------------------------------------------------------------
    // Output terrain
    //-----------------------------------------------------------------------------
    static MObject m_outMesh;
    //-----------------------------------------------------------------------------
    // Find the centre of a curve
    // @param _curveFn A curve function set
    // @return The centre point of the curve as a MPoint
    //-----------------------------------------------------------------------------
    const MPoint& findCurveCentre(const MFnNurbsCurve &_curveFn) const;
    //-----------------------------------------------------------------------------
    // Find all the vertices inside the curve
    // @param _polyIt A polygon iterator for the mesh
    // @param _startIndex The starting index for the polygon iterator
    // @param _curveFn The curve function set for the curve mask
    // @param _curveCentre The centre of the curve
    // @param _curveOffset Offset the curve so it is still visible
    //-----------------------------------------------------------------------------
    const std::unordered_set<int>& findVerticesInsideCurve(const MItMeshPolygon &_polyIt, const int &_startIndex, const MFnNurbsCurve &_curveFn, const MPoint &_curveCentre, const float &_curveOffset);
    //-----------------------------------------------------------------------------
    // Calculate the soft selection value
    // @param _vertex The position of the vertex
    // @param _curveCentre The centre of the curve
    // @param _curvePoint The closest point on the curve
    //-----------------------------------------------------------------------------
    const float& calculateSoftSelectValue(const MPoint &_vertex, const MPoint &_curveCentre, const MPoint &_curvePoint);
    //-----------------------------------------------------------------------------
};

#endif
