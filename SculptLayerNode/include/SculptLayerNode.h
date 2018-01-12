/// @file SculptLayerNode.h
/// Create a sculpt layer

#ifndef SCULPTLAYERNODE_H__
#define SCULPTLAYERNODE_H__

#include <unordered_set>
#include <vector>
#include <maya/MDataBlock.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MItMeshPolygon.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
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
    // Store affected vertices
    //-----------------------------------------------------------------------------
    std::unordered_set<int> m_affectedVertices;
    std::vector<std::pair<int, float> > m_affectedVerticesData;
    //-----------------------------------------------------------------------------
    // Store info from last computation
    //-----------------------------------------------------------------------------
    bool m_firstCompute = true;
    MPointArray m_lastCurvePoints;
    float m_lastCurveOffset;
    int m_curveCentreClosestVertex;
    //-----------------------------------------------------------------------------
    // Find the centre of a curve
    // @param _curve The curve to find the centre of
    // @return The centre point of the curve as a MPoint
    //-----------------------------------------------------------------------------
    MPoint findCurveCentre(const MObject &_curve);
    //-----------------------------------------------------------------------------
    // Find all the vertices inside the curve
    // @param _terrain The terrain
    // @param _curve The curve mask
    // @param _curveOffset Offset the curve so it is still visible
    //-----------------------------------------------------------------------------
    void findVerticesInsideCurve(const MObject &_terrain, const MObject &_curve, const float &_curveOffset);
    //-----------------------------------------------------------------------------
    // Calculate the soft selection value
    // @param _vertex The position of the vertex
    // @param _curveCentre The centre of the curve
    // @param _curvePoint The closest point on the curve
    //-----------------------------------------------------------------------------
    void calculateSoftSelectValues(const MPointArray &_vertices, const MObject &_curve);
    //-----------------------------------------------------------------------------
};

#endif
