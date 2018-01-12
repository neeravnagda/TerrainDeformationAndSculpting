#include <stack>
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

#include <string>
#include <iostream>

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
    numericAttr.setReadable(false);
    numericAttr.setWritable(true);
    numericAttr.setStorable(true);
	stat = addAttribute(m_sculptStrength);
	if (!stat)
		return stat;

    m_curveOffset = numericAttr.create("curveOffset", "co", MFnNumericData::kFloat, 1.1);
    numericAttr.setReadable(false);
    numericAttr.setWritable(true);
    numericAttr.setStorable(true);
    stat = addAttribute(m_curveOffset);
    if (!stat)
        return stat;

    m_maxProjectionDistance = numericAttr.create("maxProjectionDistance", "mpd", MFnNumericData::kFloat, 1000);
    numericAttr.setReadable(false);
    numericAttr.setWritable(true);
    numericAttr.setStorable(true);
    stat = addAttribute(m_maxProjectionDistance);
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
    attributeAffects(m_curveOffset, m_outMesh);
    attributeAffects(m_maxProjectionDistance, m_outMesh);

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
        MDataHandle terrainDataHandle = _data.inputValue(m_terrain);
		MObject terrainValue = terrainDataHandle.asMesh();

        MDataHandle curveMaskDataHandle = _data.inputValue(m_curveMask);
		MObject curveMaskValue = curveMaskDataHandle.asNurbsCurve();

        MDataHandle sculptedMeshDataHandle = _data.inputValue(m_sculptedMesh);
		MObject sculptedMeshValue = sculptedMeshDataHandle.asMesh();

        MDataHandle sculptStrengthDataHandle = _data.inputValue(m_sculptStrength);
        float sculptStrengthValue = sculptStrengthDataHandle.asFloat();

        MDataHandle curveOffsetDataHandle = _data.inputValue(m_curveOffset);
        float curveOffsetValue = curveOffsetDataHandle.asFloat();

        MDataHandle maxProjectionDataHandle = _data.inputValue(m_maxProjectionDistance);
        float maxProjectionDistanceValue = maxProjectionDataHandle.asFloat();

		// Get the output data handle
        MDataHandle outMeshDataHandle = _data.outputValue(m_outMesh);

        // Computation
        // Get the vertices of the original mesh
        MFnMesh inTerrainFn(terrainValue);
        MPointArray vertices;
        inTerrainFn.getPoints(vertices, MSpace::kWorld);

        MFnNurbsCurve curveFn(curveMaskValue);

        bool recompute = false;
        if (m_firstCompute == true)
        {
            recompute = true;
            curveFn.getCVs(m_lastCurvePoints, MSpace::kWorld);
            m_lastCurveOffset = curveOffsetValue;
            int curveCentreClosestVertex;
            MPoint curveCentre = findCurveCentre(curveMaskValue);
            MPoint tempPoint;
            inTerrainFn.getClosestPoint(curveCentre, tempPoint, MSpace::kWorld, &curveCentreClosestVertex);
            m_curveCentreClosestVertex = curveCentreClosestVertex;
            m_firstCompute = false;
        }
        else if (m_lastCurvePoints.length() != curveFn.numCVs())
        {
            recompute = true;
            curveFn.getCVs(m_lastCurvePoints, MSpace::kWorld);
        }
        else if (m_lastCurveOffset != curveOffsetValue)
        {
            recompute = true;
            m_lastCurveOffset = curveOffsetValue;
        }
        else
        {
            int curveCentreClosestVertex;
            MPoint curveCentre = findCurveCentre(curveMaskValue);
            MPoint tempPoint;
            inTerrainFn.getClosestPoint(curveCentre, tempPoint, MSpace::kWorld, &curveCentreClosestVertex);
            if (m_curveCentreClosestVertex != curveCentreClosestVertex)
            {
                recompute = true;
                m_curveCentreClosestVertex = curveCentreClosestVertex;
            }
        }

        // Only compute data if necessary
        if (recompute == true)
        {
            // Find the vertices that lie within the curve
            findVerticesInsideCurve(terrainValue, curveMaskValue, curveOffsetValue);
            // Calculate the soft select values
            calculateSoftSelectValues(vertices, curveMaskValue);
        }

        // Create a function set for the sculpted mesh and acceleration parameters
        MFnMesh sculptedMeshFn(sculptedMeshValue);
        MMeshIsectAccelParams accelerationParams = sculptedMeshFn.autoUniformGridParams();

        // Iterate through the vertices and project onto the sculpted mesh
        MFloatPoint raySource;
        MVector normal;
        MFloatVector rayDirection;
        MFloatPoint intersectionPoint;
        for (auto vertex : m_affectedVerticesData)
        {
            raySource = MFloatPoint(vertices[vertex.first]);
            inTerrainFn.getVertexNormal(vertex.first, true, normal, MSpace::kWorld);
            rayDirection = MFloatVector(normal);
            sculptedMeshFn.closestIntersection(raySource, rayDirection, NULL, NULL, false, MSpace::kWorld, maxProjectionDistanceValue, true, &accelerationParams, intersectionPoint, NULL, NULL, NULL, NULL, NULL, 1e-6f, NULL);
            MVector displacement = MPoint(intersectionPoint) - vertices[vertex.first];
            // Ensure the vertices are not sliding perpendicular to the normal
            if (displacement * normal != 0.0)
            {
                vertices[vertex.first] += displacement * sculptStrengthValue * vertex.second;
            }
        }

        // Create a copy of the terrain
        MFnMeshData meshDataFn;
        MObject outMeshObj = meshDataFn.create();
        MFnMesh newMeshFn;
        newMeshFn.copy(terrainValue, outMeshObj);

        // Set the output mesh vertices
        newMeshFn.setPoints(vertices);
        newMeshFn.setObject(outMeshObj);

		// Set the output value
        outMeshDataHandle.set(outMeshObj);

		// Set the plug as clean
		stat = _data.setClean(_plug);
		if (!stat)
			return stat;

        return MStatus::kSuccess;
	}
    return MStatus::kUnknownParameter;
}
//-----------------------------------------------------------------------------
MPoint SculptLayer::findCurveCentre(const MObject &_curve)
{
    MFnNurbsCurve curveFn(_curve);
    MPoint point;
    int numPoints = curveFn.numCVs() * 2;
    MVector curveCentre(0.0, 0.0, 0.0);
    for (int i=0; i<numPoints; ++i)
    {
        curveFn.getPointAtParam(float(i)/numPoints, point, MSpace::kWorld);
        curveCentre += MVector(point);
    }
    curveCentre /= float(numPoints);
    return MPoint(curveCentre);
}
//-----------------------------------------------------------------------------
void SculptLayer::findVerticesInsideCurve(const MObject &_terrain, const MObject &_curve, const float &_curveOffset)
{
    m_affectedVertices.clear();
    // Create two sets of checked and unchecked face IDs
    std::stack<int> uncheckedFaces;
    std::unordered_set<int> checkedFaces;
    // Calculate the starting index to check
    MPoint curveCentre = findCurveCentre(_curve);
    MFnMesh terrainFn(_terrain);
    MPoint tempPoint;
    int startID;
    terrainFn.getClosestPoint(curveCentre, tempPoint, MSpace::kWorld, &startID);
    // Append the start ID to the checked and unchecked face sets
    uncheckedFaces.emplace(startID);
    checkedFaces.emplace(startID);

    // Create a polygon iterator
    MItMeshPolygon polygonIterator(_terrain);
    int tempIndex;

    MFnNurbsCurve curveFn(_curve);
    MPoint faceCentre;
    MPoint closestPointOnCurve;
    MVector centreToFace;
    MVector centreToCurve;

    while (!uncheckedFaces.empty())
    {
        // Set the iterator to the top of the stack
        polygonIterator.setIndex(uncheckedFaces.top(), tempIndex);
        // Pop from the stack
        uncheckedFaces.pop();
        // Find the face centre
        faceCentre = polygonIterator.center(MSpace::kWorld);
        closestPointOnCurve = curveFn.closestPoint(faceCentre, NULL, kMFnNurbsEpsilon, MSpace::kWorld);
        centreToFace = (faceCentre - curveCentre) * _curveOffset;
        centreToCurve = closestPointOnCurve - curveCentre;
        // Use the dot product to check if the point is inside
        if (centreToFace * centreToCurve.normal() < centreToCurve.length())
        {
            // Get the vertices of the face and append to the set of affected vertices
            MIntArray polyVertices;
            polygonIterator.getVertices(polyVertices);
            for (unsigned i=0; i<polyVertices.length(); ++i)
            {
                m_affectedVertices.emplace(polyVertices[i]);
            }
            // Find the connected faces and append to the list of unchecked faces
            MIntArray connectedFaces;
            polygonIterator.getConnectedFaces(connectedFaces);
            for (unsigned i=0; i<connectedFaces.length(); ++i)
            {
                // If it is not in checked faces, add to the stack
                auto search = checkedFaces.find(connectedFaces[i]);
                if (search == checkedFaces.end())
                {
                    uncheckedFaces.emplace(connectedFaces[i]);
                }
                // Add to the checked faces
                checkedFaces.emplace(connectedFaces[i]);
            }
        }
    }
}
//-----------------------------------------------------------------------------
void SculptLayer::calculateSoftSelectValues(const MPointArray &_vertices, const MObject &_curve)
{
    // Clear the soft select values
    m_affectedVerticesData.clear();

    // Curve centre
    MPoint curveCentre = findCurveCentre(_curve);
    MFnNurbsCurve curveFn(_curve);

    // Closest point on curve
    MPoint curvePoint;
    float centreVertexLenSquared;
    float centreCurvePointLenSquared;
    float ratio;
    float softSelectValue;

    for (int vertexID : m_affectedVertices)
    {
        // Find the closest point on the curve
        curvePoint = curveFn.closestPoint(_vertices[vertexID], NULL, kMFnNurbsEpsilon, MSpace::kWorld);
        centreVertexLenSquared = ((curveCentre.x - _vertices[vertexID].x) * (curveCentre.x - _vertices[vertexID].x)) + ((curveCentre.z - _vertices[vertexID].z) * (curveCentre.z - _vertices[vertexID].z));
        centreCurvePointLenSquared = ((curveCentre.x - curvePoint.x) * (curveCentre.x - curvePoint.x)) + ((curveCentre.z - curvePoint.z) * (curveCentre.z - curvePoint.z));
        ratio = centreVertexLenSquared / centreCurvePointLenSquared;
        softSelectValue = 2.0 + (2.0/(ratio - 2.0));
        if (softSelectValue < 0)
        {
            softSelectValue = 0.0;
        }
        m_affectedVerticesData.emplace_back(std::make_pair(vertexID, softSelectValue));
    }
}
//-----------------------------------------------------------------------------
SculptLayer::SculptLayer(){}
//-----------------------------------------------------------------------------
SculptLayer::~SculptLayer(){}
//-----------------------------------------------------------------------------
