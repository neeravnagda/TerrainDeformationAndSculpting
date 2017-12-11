#include <iostream>
#include <maya/MDataHandle.h>
#include <maya/MFnData.h>
#include <maya/MFnMesh.h>
#include <maya/MFnMeshData.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MItMeshVertex.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MVector.h>
#include "SculptLayerNode.h"

//-----------------------------------------------------------------------------
// Set static members
MTypeId SculptLayer::m_id(0x1005);
const MString SculptLayer::typeName("SculptLayerNode");
MObject SculptLayer::m_terrain;
MObject SculptLayer::m_originalMesh;
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

	m_originalMesh = typedAttr.create("originalMesh", "mo", MFnData::kMesh);
	typedAttr.setReadable(false);
	typedAttr.setWritable(true);
	typedAttr.setStorable(true);
	stat = addAttribute(m_originalMesh);
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
	attributeAffects(m_originalMesh, m_outMesh);
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

		MDataHandle originalMeshDataHandle = _data.inputValue(m_originalMesh, &stat);
		if (!stat)
			return stat;
		MObject originalMeshValue = originalMeshDataHandle.asMesh();

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
        MFnMesh terrainFn(terrainValue);
		// Create a copy of the terrain
        MFnMeshData terrainDataFn;
        MObject outTerrain = terrainDataFn.create();
        //MObject outTerrain = terrainDataFn.create();
		MFnMesh outMeshFn;
		outMeshFn.copy(terrainValue, outTerrain);

		// Get all the vertices for the terrain
		MPointArray terrainVertices;
        terrainFn.getPoints(terrainVertices, MSpace::kWorld);

		MItMeshVertex meshIt(originalMeshValue);
		MFnMesh sculptedMeshFn(sculptedMeshValue);

		MPoint terrainPoint;
		MPoint originalPoint;
		MPoint sculptedPoint;
		MVector difference;
        int pointID;
		while (!meshIt.isDone())
		{
			// Get the original point
			originalPoint = meshIt.position(MSpace::kWorld);
			// Get the point on the terrain
            outMeshFn.getClosestPoint(originalPoint, terrainPoint, MSpace::kWorld, &pointID);
            std::cout<<originalPoint<<", "<<terrainPoint<<"\n";
			// Get the sculpted point
			sculptedMeshFn.getPoint(meshIt.index(), sculptedPoint, MSpace::kWorld);
			// Compute the difference
			difference = sculptedPoint - originalPoint;
			difference *= sculptStrengthValue;
            //std::cout<<difference<<"\n";
			// Set the vertex
			terrainVertices[pointID] += difference;
			// Iterate
			meshIt.next();
		}
/*
    # Create a new empty curve and curve data function set
            curveDataFn = om.MFnNurbsCurveData()
            curveDataObj = curveDataFn.create()
            curveFn = om.MFnNurbsCurve()
  */


		// Set the mesh vertices
		outMeshFn.setPoints(terrainVertices,MSpace::kWorld);

		// Set the output value
		outMeshDataHandle.set(outTerrain);

		// Set the plug as clean
		stat = _data.setClean(_plug);
		if (!stat)
			return stat;

        return MStatus::kSuccess;
	}
    return MStatus::kUnknownParameter;
}
//-----------------------------------------------------------------------------
SculptLayer::SculptLayer(){}
//-----------------------------------------------------------------------------
SculptLayer::~SculptLayer(){}
//-----------------------------------------------------------------------------
