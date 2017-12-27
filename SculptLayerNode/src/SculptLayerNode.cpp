#include <stack>
#include <string>
#include <maya/MDataHandle.h>
#include <maya/MFloatPoint.h>
#include <maya/MFloatVector.h>
#include <maya/MFnData.h>
#include <maya/MFnMesh.h>
#include <maya/MFnMeshData.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MGlobal.h>
#include <maya/MIntArray.h>
#include <maya/MPointArray.h>
#include <maya/MVector.h>
#include <maya/MVectorArray.h>
#include "SculptLayerNode.h"

//-----------------------------------------------------------------------------
// Set static members
MTypeId SculptLayer::m_id(0x1005);
const MString SculptLayer::typeName("SculptLayerNode");
MObject SculptLayer::m_terrain;
MObject SculptLayer::m_curveMask;
MObject SculptLayer::m_sculptedMesh;
MObject SculptLayer::m_sculptStrength;
MObject SculptLayer::m_curveOffset;
MObject SculptLayer::m_maxProjectionDistance;
MObject SculptLayer::m_outMesh;
//-----------------------------------------------------------------------------
void* SculptLayer::creator()
{
    return new SculptLayer();
}
//-----------------------------------------------------------------------------
MStatus SculptLayer::initialize()
{
	MStatus stat;
	MFnTypedAttribute typedAttr;
	MFnNumericAttribute numericAttr;

	// Input node attributes
	m_terrain = typedAttr.create("terrain", "t", MFnData::kMesh);
	typedAttr.setReadable(false);
	typedAttr.setWritable(true);
	typedAttr.setStorable(true);
	stat = addAttribute(m_terrain);
	if (!stat)
		return stat;

	m_curveMask = typedAttr.create("curveMask", "cm", MFnData::kNurbsCurve);
	typedAttr.setReadable(false);
	typedAttr.setWritable(true);
	typedAttr.setStorable(true);
	stat = addAttribute(m_curveMask);
	if (!stat)
		return stat;

	m_sculptedMesh = typedAttr.create("sculptedMesh", "sm", MFnData::kMesh);
	typedAttr.setReadable(false);
	typedAttr.setWritable(true);
	typedAttr.setStorable(true);
	stat = addAttribute(m_sculptedMesh);
	if (!stat)
		return stat;

    m_sculptStrength = numericAttr.create("sculptStrength", "ss", MFnNumericData::kFloat, 1.0);
	typedAttr.setReadable(false);
	typedAttr.setWritable(true);
	typedAttr.setStorable(true);
	stat = addAttribute(m_sculptStrength);
	if (!stat)
		return stat;

	// Output node attributes
	m_outMesh = typedAttr.create("outMesh", "m", MFnData::kMesh);
	typedAttr.setReadable(true);
	typedAttr.setWritable(false);
	typedAttr.setStorable(false);
	stat = addAttribute(m_outMesh);
	if (!stat)
		return stat;

	// Connect input/output dependencies
	attributeAffects(m_terrain, m_outMesh);
	attributeAffects(m_curveMask, m_outMesh);
	attributeAffects(m_sculptedMesh, m_outMesh);
	attributeAffects(m_sculptStrength, m_outMesh);

	// Return success
	return MStatus::kSuccess;
}
//-----------------------------------------------------------------------------
MStatus SculptLayer::compute(const MPlug &_plug, MDataBlock &_data)
{
	MStatus stat;
	// Check if the plug is the output plug
	if (_plug == m_outMesh)
	{
		// Get the data handles for inputs and convert to the correct type
		MDataHandle terrainDataHandle = _data.inputValue(m_terrain, &stat);
		if (!stat)
			return stat;
		MObject terrainValue = terrainDataHandle.asMesh();

		MDataHandle curveMaskDataHandle = _data.inputValue(m_curveMask, &stat);
		if (!stat)
			return stat;
		MObject curveMaskValue = curveMaskDataHandle.asNurbsCurve();

		MDataHandle sculptedMeshDataHandle = _data.inputValue(m_sculptedMesh, &stat);
		if (!stat)
			return stat;
		MObject sculptedMeshValue = sculptedMeshDataHandle.asMesh();

		MDataHandle sculptStrengthDataHandle = _data.inputValue(m_sculptStrength, &stat);
		if (!stat)
			return stat;
        float sculptStrengthValue = sculptStrengthDataHandle.asFloat();

        MDataHandle curveOffsetDataHandle = _data.inputValue(m_curveOffset, &stat);
        if (!stat)
            return stat;
        float curveOffsetValue = curveOffsetDataHandle.asFloat();

        MDataHandle maxProjectionDataHandle = _data.inputValue(m_maxProjectionDistance, &stat);
        if (!stat)
            return stat;
        float maxProjectionDistanceValue = maxProjectionDataHandle.asFloat();

		// Get the output data handle
		MDataHandle outMeshDataHandle = _data.outputValue(m_outMesh, &stat);
		if (!stat)
			return stat;

        // Computation
        // Create a copy of the terrain
        MFnMeshData meshDataFn;
        MObject outTerrain = meshDataFn.create();
        MFnMesh outTerrainFn;
        outTerrainFn.copy(terrainValue, outTerrain);

        // Get all the vertices from the terrain
        MFnMesh inTerrainFn(terrainValue);
        MPointArray vertexPositions;
        inTerrainFn.getPoints(&vertexPositions, MSpace::kWorld);

        // Create a polygon iterator
        MItMeshPolygon polygonIterator(terrainValue);

        // Find the centre of the curve and the closest face on the terrain
        MFnNurbsCurve curveFn(curveMaskValue);
        MPoint curveCentre = findCurveCentre(&curveFn);
        int centreFaceIndex;
        inTerrainFn.getClosestPoint(&curveCentre, nullptr, MSpace::kWorld, &centreFaceIndex);

        // Find all the vertices inside the curve
        std::unordered_set<int> polyVertices = findVerticesInsideCurve(&polygonIterator, &centreFaceIndex, &curveFn, &curveCentre, &curveOffsetValue);

        // Create a function set for the sculpted mesh and acceleration parameters
        MFnMesh sculptedMeshFn(sculptedMeshValue);
        MMeshIsectAccelParams accelParams = sculptedMeshFn.autoUniformGridParams();

        // Iterate through the vertices and project onto the sculpted mesh
        unsigned numVertices = polyVertices.size();
        for (int i : polyVertices)
        {
            // Get the ray source and direction as a float point and float vector
            MFloatPoint raySrc(vertexPositions[i]);
            MVector normal;
            inTerrainFn.getVertexNormal(i, true, &normal, MSpace::kWorld);
            MFloatVector rayDir(normal);
            // Find the intersection with the mesh
            MFloatPoint intersectionPoint;
            inTerrainFn.closestIntersection(&raySrc, &rayDir, nullptr, nullptr, False, MSpace::kWorld, &maxProjectionDistanceValue, False, &accelParams, &intersectionPoint, nullptr, nullptr, nullptr, nullptr, nullptr);
            // Calculate a vector from the intersection point to the vertex position
            MVector difference = MPoint(intersectionPoint) - vertexPositions[i];
            // Ensure the vertex is not sliding perpendicular to the normal
            if (difference * normal != 0)
            {
                MPoint closestPointOnCurve = curveFn.closestPoint(vertexPositions[i], NULL, kMFnNurbsEpsilon, MSpace::kWorld);
                vertexPositions[i] += difference * sculptStrengthValue * calculateSoftSelectValue(&vertexPositions[i], &curveCentre, &closestPointOnCurve);
            }
        }

        outTerrainFn.setPoints(vertexPositions);

		// Set the output value
		outMeshDataHandle.set(outMesh);

		// Set the plug as clean
		stat = _data.setClean(_plug);
		if (!stat)
			return stat;

        return MStatus::kSuccess;
	}
    return MStatus::kUnknownParameter;
}
//-----------------------------------------------------------------------------
const MPoint& SculptLayer::findCurveCentre(const MFnNurbsCurve &_curveFn) const
{
    MPointArray curvePoints;
    int numPoints = _curveFn.numCVs() * 2;
    curvePoints.setLength(numPoints);
    MVector curveCentre(0,0,0);
    for (unsigned i=0; i<numPoints; ++i)
    {
        MPoint point;
        _curveFn.getPointAtParam(float(i)/numPoints, &point, MSpace::kWorld);
        curvePoints[i] = point;
        curveCentre += MVector(point);
    }
    curveCentre /= float(numPoints);
    return MPoint(curveCentre);
}
//-----------------------------------------------------------------------------
const std::unordered_set<int>& SculptLayer::findVerticesInsideCurve(const MItMeshPolygon &_polyIt, const int &_startIndex, const MFnNurbsCurve &_curveFn, const MPoint &_curveCentre, const float &_curveOffset)
{
    // Create a stack and set containing face indices
    std::stack<int> uncheckedFaces;
    std::unordered_set<int> checkedFaces;
    // Add the starting index to the list and set
    uncheckedFaces.emplace(_startIndex);
    checkedFaces.insert(_startIndex);

    // Create a set of vertex indices that lie within the curve
    std::unordered_set<int> vertices;

    // Loop through and check the array of unchecked faces if they lie within the curve
    while (uncheckedFaces.size() > 0)
    {
        // Set the iterator to the top of the stack of unchecked faces
        _polyIt.setIndex(uncheckedFaces.top());
        // Pop this from the stack as new items will be added
        uncheckedFaces.pop();
        // Find the centre of this face and the closest point on the curve
        MPoint faceCentre = _polyIt.center(MSpace::kWorld);
        MPoint closestPointOnCurve = _curveFn.closestPoint(&faceCentre, NULL, kMFnNurbsEpsilon, MSpace::kWorld);
        // Calculate two vectors from the centre to the curve to the face centre and the closest point on the curve
        MVector centreToFace = (faceCentre - _curveCentre) * _curveOffset;
        MVector centreToCurve = closestPointOnCurve - _curveCentre;
        // Use the dot product to see if the point is inside
        if (centreToFace * centreToCurve.normal() < centreToCurve.length())
        {
            // Add the vertices to the set of vertices
            MIntArray thisPolyVertices;
            _polyIt.getVertices(&thisPolyVertices);
            for (int vertex : thisPolyVertices)
            {
                vertices.insert(vertex);
            }
            // Find the connected faces
            MIntArray connectedFaces;
            _polyIt.getConnectedFaces(&connectedFaces);
            for (int face : connectedFaces)
            {
                uncheckedFaces.emplace(face);
            }
        }
    }
    return vertices;
}
//-----------------------------------------------------------------------------
const float& SculptLayer::calculateSoftSelectValue(const MPoint &_vertex, const MPoint &_curveCentre, const MPoint &_curvePoint)
{
    float centreVertexLenSquared = ((_curveCentre.x - _vertex.x) * (_curveCentre.x - _vertex.x)) + ((_curveCentre.y - _vertex.y) * (_curveCentre.y - _vertex.y)) + ((_curveCentre.z - _vertex.z) * (_curveCentre.z - _vertex.z));
    float centreCurvePointLenSquared = ((_curveCentre.x - _curvePoint.x) * (_curveCentre.x - _curvePoint.x)) + ((_curveCentre.y - _curvePoint.y) * (_curveCentre.y - _curvePoint.y)) + ((_curveCentre.z - _curvePoint.z) * (_curveCentre.z - _curvePoint.z));
    float ratio = centreVertexLenSquared / centreCurvePointLenSquared;
    return 2.0f + 2.0f/(ratio - 2.0f);
}
//-----------------------------------------------------------------------------
SculptLayer::SculptLayer(){}
//-----------------------------------------------------------------------------
SculptLayer::~SculptLayer(){}
//-----------------------------------------------------------------------------
