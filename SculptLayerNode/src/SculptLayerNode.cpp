#include <maya/MDataHandle.h>
#include <maya/MFnData.h>
#include <maya/MFnMesh.h>
#include <maya/MFnMeshData.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MVector.h>
#include "SculptLayerNode.h"

//-----------------------------------------------------------------------------
// Set static members
MTypeID SculptLayer::m_id(0x1004);
const MString SculptLayer::typeName("SculptLayerNode");
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
	m_originalMesh = typedAttr.create("originalMesh", "mo", MFnData::kMesh, &stat);
	if (!stat)
		return stat;
	typedAttr.setReadable(false);
	typedAttr.setWritable(true);
	typedAttr.setStorable(true);

	m_sculptedMesh = typedAttr.create("sculptedMesh", "sm", MFnData::kMesh, &stat);
	if (!stat)
		return stat;
	typedAttr.setReadable(false);
	typedAttr.setWritable(true);
	typedAttr.setStorable(true);

	m_sculptStrength = numericAttr.create("sculptStrength", "ss", MFnNumericData::kFloat, &stat);
	if (!stat)
		return stat;
	typedAttr.setReadable(false);
	typedAttr.setWritable(true);
	typedAttr.setStorable(true);

	// Output node attributes
	m_outMesh = typedAttr.create("outMesh", "m", MFnData::kMesh, &stat);
	if (!stat)
		return stat;
	typedAttr.setReadable(true);
	typedAttr.setWritable(false);
	typedAttr.setStorable(false);

	// Add the attributes to the class
	stat = addAttribute(m_originalMesh);
	if (!stat)
		return stat;
	stat = addAttribute(m_sculptedMesh);
	if (!stat)
		return stat;
	stat = addAttribute(m_sculptStrength);
	if (!stat)
		return stat;
	stat = addAttribute(m_outMesh);
	if (!stat)
		return stat;

	// Connect input/output dependencies
	attributeAffects(m_originalMesh, m_outMesh);
	attributeAffects(m_sculptedMesh, m_outMesh);
	attributeAffects(m_sculptStrength, m_outMesh);

	// Return success
	return MStatus::kSuccess;
}
//-----------------------------------------------------------------------------
void SculptLayer::compute(const MPlug &_plug, MDataBlock &_data)
{
	MStatus stat;
	// Check if the plug is the output plug
	if (_plug == m_outMesh)
	{
		// Get the data handles for inputs and convert to the correct type
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
		float sculptStrengthValue = sculptedMeshDataHandle.asFloat();

		// Get the output data handle
		MDataHandle outMeshDataHandle = _data.outputValue(m_outMesh, &stat);
		if (!stat)
			return stat;

		// Do the computation here

		// Set the output value
		// outMeshDataHandle.set();

		// Set the plug as clean
		stat = _data.setClean(_plug);
		if (!stat)
			return stat;
	}
}
//-----------------------------------------------------------------------------
SculptLayer::SculptLayer(){}
//-----------------------------------------------------------------------------
SculptLayer::~SculptLayer(){}
//-----------------------------------------------------------------------------
