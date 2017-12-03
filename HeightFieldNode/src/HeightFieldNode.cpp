#include <maya/MDataHandle.h>
#include <maya/MFnData.h>
#include <maya/MFnMesh.h>
#include <maya/MFnMeshData.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MIntArray.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MVector.h>
#include "HeightFieldNode.h"
#include "FastNoise.h"

//-----------------------------------------------------------------------------
// Set static members
MTypeID HeightField::m_id(0x1003);
const MString HeightField::typeName("HeightFieldNode");
MObject HeightField::m_inMesh;
MObject HeightField::m_amplitude;
MObject HeightField::m_outMesh;
//-----------------------------------------------------------------------------
void* HeightField::creator()
{
    return new HeightField();
}
//-----------------------------------------------------------------------------
MStatus HeightField::initialize()
{
	MStatus stat;
	MFnTypedAttribute typedAttr;
	MFnNumericAttribute numericAttr;

	// Input node attributes
	m_inMesh = typedAttr.create("inMesh", "im", MFnData::kMesh, &stat);
	if (!stat)
		return stat;
	typedAttr.setReadable(false);
	typedAttr.setWritable(true);
	typedAttr.setStorable(true);

	m_amplitude = numericAttr.create("amplitude", "a", MFnNumericData::kFloat, 1.0, &stat);
	if (!stat)
		return stat;
	numericAttr.setReadable(false);
	numericAttr.setWritable(true);
	numericAttr.setStorable(true);

	// Output node attributes
	m_outMesh = typedAttr.create("outMesh", "om", MFnData::kMesh, &stat);
	if (!stat)
		return stat;
	typedAttr.setReadable(true);
	typedAttr.setWritable(false);
	typedAttr.setStorable(false);

	// Add the attributes to the class
	stat = addAttribute(m_inMesh);
	if (!stat)
		return stat;
	stat = addAttribute(m_amplitude);
	if (!stat)
		return stat;
	stat = addAttribute(m_outMesh);
	if (!stat)
		return stat;

	// Connect input/output dependencies
	attributeAffects(m_inMesh, m_outMesh);
	attributeAffects(m_amplitude, m_outMesh);

	// Return success
	return MStatus::kSuccess;
}
//-----------------------------------------------------------------------------
void HeightField::compute(const MPlug &_plug, MDataBlock &_data)
{
	MStatus stat;
	// Check if the plug is the output plug
	if (_plug == m_outMesh)
	{
		// Get the data handle for the mesh input
		MDataHandle inMeshDataHandle = _data.inputValue(m_inMesh, &stat);
		if (!stat)
			return stat;
		// Get the input mesh as a MObject
		MObject inMeshValue = inMeshDataHandle.asMesh();

		// Get the data handle for the amplitude input
		MDataHandle inAmplitudeDataHandle = _data.inputValue(m_amplitude, &stat);
		if (!stat)
			return stat;
		// Get the amplitude as a float
		float amplitudeValue = inAmplitudeDataHandle.asFloat();

		// Get the data handle for the output value
		MDataHandle outMeshDataHandle = _data.outputValue(m_outMesh, &stat);
		if (!stat)
			return stat;

		// Set FastNoise parameters
		m_fastNoise.SetNoiseType(FastNoise::SimplexFractal);

		// Create a function set for the input mesh
		MFnMesh inMeshFn(inMeshValue, &stat);
		if (!stat)
			return stat;
		// Create a mesh data object and a new MObject
		MFnMeshData meshData;
		MObject meshDataObj = meshData.create(&stat);
		if (!stat)
			return stat;
		// Create a function set for the new mesh
		MFnMesh newMeshFn;
		MObject outMesh = newMeshFn.copy(inMeshValue, meshDataObj, &stat);
		if (!stat)
			return stat;

		// Get the vertices of the original mesh
		MPointArray vertices;
		stat = inMeshFn.getPoints(&vertices, MSpace::kObject);
		if (!stat)
			return stat;

		// Iterate through each point and adjust the y value
		float height = 0.0f;
		MVector heightDisplacement(0.0, 0.0, 0.0);
		size_t numVertices = vertices.length();
		for (size_t i = 0; i < numVertices; ++i)
		{
			MPoint& currentPoint = vertices[i];
			height = m_fastNoise.GetNoise(currentPoint.x, currentPoint.z);
			heightDisplacement.y = height;
			currentPoint += heightDisplacement;
		}
		// Set the output mesh vertices
		stat = outMesh.setPoints(vertices, MSpace::kWorld);
		if (!stat)
			return stat;

		// Set the output value
		outMeshDataHandle.set(outMesh);

		// Set the plug as clean
		stat = _data.setClean(_plug);
		if (!stat)
			return stat;
	}
}
//-----------------------------------------------------------------------------
HeightField::HeightField(){}
//-----------------------------------------------------------------------------
HeightField::~HeightField(){}
//-----------------------------------------------------------------------------
