#include <iostream>
#include <string>
#include <maya/MDataHandle.h>
#include <maya/MFnData.h>
#include <maya/MFnMesh.h>
#include <maya/MFnMeshData.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MGlobal.h>
#include <maya/MIntArray.h>
#include <maya/MItMeshVertex.h>
#include <maya/MPoint.h>
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

		// Get the output data handle
		MDataHandle outMeshDataHandle = _data.outputValue(m_outMesh, &stat);
		if (!stat)
			return stat;

		// computation

		// Calculate the plane normal
		MVector planeNormal;
		MVector planeCentre;
		calculatePlaneNormal(curveMaskValue, planeNormal, planeCentre);

		// Print the normal
    //std::string planeNormalString = "Normal: [" + std::to_string(planeNormal.x) + ", " + std::to_string(planeNormal.y) + ", " + std::to_string(planeNormal.z) + "]";
    //MGlobal::displayInfo(planeNormalString.c_str());

		MFnMesh terrainFn(terrainValue);
		MPointArray meshVertices;
		terrainFn.getPoints(meshVertices, MSpace::kWorld);

		// Project the mesh onto the plane
		projectToPlane(planeNormal, planeCentre, meshVertices);


		// Find the intersections


		// Get the terrain values
		int numVertices = terrainFn.numVertices();
		int numPolygons = terrainFn.numPolygons();

		MIntArray polyCounts;
		MIntArray polyConnects;

		for (unsigned i=0; i<numPolygons; ++i)
		{
			// Get the vertex count and connected indices
			int polyCount = terrainFn.polygonVertexCount(i);
			MIntArray thisPolyConnects;
			terrainFn.getPolygonVertices(i, thisPolyConnects);
			// Append to the arrays
			polyCounts.append(polyCount);
			for (unsigned j=0; j<thisPolyConnects.length(); ++j)
			{
				polyConnects.append(thisPolyConnects[j]);
			}
		}

		// Create a new mesh for the output
		MFnMeshData meshDataFn;
		MObject outMesh = meshDataFn.create();
		MFnMesh outMeshFn;
		outMeshFn.create(numVertices, numPolygons, meshVertices, polyCounts, polyConnects, outMesh);

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
void SculptLayer::calculatePlaneNormal(const MObject &_curve, MVector &_normal, MVector &_centrePoint)
{
	// Get the curve function set
	MFnNurbsCurve curveFn(_curve);
	// Query the tangents, normals and positions on the curve and add to arrays
	MVectorArray curveTangents;
	MVectorArray curveNormals;
	MVectorArray curvePoints;
	for (float i=0.0f; i<=1.0f; i+=0.1f)
	{
		MVector tangent = curveFn.tangent(i, MSpace::kWorld);
		curveTangents.append(tangent);
		MVector normal = curveFn.normal(i, MSpace::kWorld);
		curveNormals.append(normal);
        MPoint point;
		curveFn.getPointAtParam(i, point, MSpace::kWorld);
		curvePoints.append(point);
	}

	MVector tangentAverage(0,0,0);
	MVector normalAverage(0,0,0);
	_centrePoint = MVector(0,0,0);
	for (unsigned i=0; i<curveTangents.length(); ++i)
	{
		tangentAverage += curveTangents[i];
		normalAverage += curveNormals[i];
		_centrePoint += curvePoints[i];
	}
	tangentAverage /= curveTangents.length();
	normalAverage /= normalAverage.length();
	_centrePoint /= curvePoints.length();

	_normal = normalAverage ^ tangentAverage;
	_normal.normalize();
}
//-----------------------------------------------------------------------------
void SculptLayer::projectToPlane(const MVector &_normal, const MVector &_point, MPointArray &_meshVertices)
{
	//p' = p - (n ⋅ (p - o)) * n
	for (unsigned i=0; i<_meshVertices.length(); ++i)
	{
		MVector originalPoint(_meshVertices[i]);
		MVector v = (_normal * (originalPoint - _point)) * _normal;
		MPoint newPoint(originalPoint - v);
		/*
		MVector v = originalPoint - _point;
		MVector w = (v * _normal) * _normal;
		MPoint newPoint(originalPoint - w);
		*/
		_meshVertices[i] = newPoint;
	}
}
//-----------------------------------------------------------------------------
SculptLayer::SculptLayer(){}
//-----------------------------------------------------------------------------
SculptLayer::~SculptLayer(){}
//-----------------------------------------------------------------------------
