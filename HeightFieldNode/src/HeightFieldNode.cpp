#include <maya/MDataHandle.h>
#include <maya/MFnEnumAttribute.h>
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
MTypeId HeightField::m_id(0x1003);
const MString HeightField::typeName("HeightFieldNode");
MObject HeightField::m_inMesh;
MObject HeightField::m_spaceType;
MObject HeightField::m_noiseType;
MObject HeightField::m_amplitude;
MObject HeightField::m_seed;
MObject HeightField::m_frequency;
MObject HeightField::m_fractalOctaves;
MObject HeightField::m_lacunarity;
MObject HeightField::m_fractalGain;
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
    MFnEnumAttribute enumAttr;

	// Input node attributes
    m_inMesh = typedAttr.create("inMesh", "im", MFnData::kMesh);
	typedAttr.setReadable(false);
	typedAttr.setWritable(true);
	typedAttr.setStorable(true);
    stat = addAttribute(m_inMesh);
    if (!stat)
        return stat;

    // Default value = 5, which is SimplexFractal
    m_noiseType = enumAttr.create("noiseType", "nt", 5);
    enumAttr.addField("Simplex", FastNoise::SimplexFractal);
    enumAttr.addField("Perlin", FastNoise::PerlinFractal);
    enumAttr.addField("Cubic", FastNoise::CubicFractal);
    stat = addAttribute(m_noiseType);
    if (!stat)
        return stat;

    // Default value = 2, which is object space
    m_spaceType = enumAttr.create("spaceType", "st", 2);
    enumAttr.addField("Object", MSpace::kObject);
    enumAttr.addField("World", MSpace::kWorld);
    stat = addAttribute(m_spaceType);
    if (!stat)
        return stat;

    m_amplitude = numericAttr.create("amplitude", "a", MFnNumericData::kFloat, 1.0);
	numericAttr.setReadable(false);
	numericAttr.setWritable(true);
	numericAttr.setStorable(true);
    stat = addAttribute(m_amplitude);
    if (!stat)
        return stat;

    // Note 1337 is the default seed from FastNoise
    m_seed = numericAttr.create("seed", "s", MFnNumericData::kInt, 1337);
    numericAttr.setReadable(false);
    numericAttr.setWritable(true);
    numericAttr.setStorable(true);
    stat = addAttribute(m_seed);
    if (!stat)
        return stat;

    m_frequency = numericAttr.create("frequency", "f", MFnNumericData::kFloat, 0.01f);
    numericAttr.setReadable(false);
    numericAttr.setWritable(true);
    numericAttr.setStorable(true);
    stat = addAttribute(m_frequency);
    if (!stat)
        return stat;

    m_fractalOctaves = numericAttr.create("fractalOctaves", "fo", MFnNumericData::kInt, 8);
    numericAttr.setReadable(false);
    numericAttr.setWritable(true);
    numericAttr.setStorable(true);
    stat = addAttribute(m_fractalOctaves);
    if (!stat)
        return stat;

    m_lacunarity = numericAttr.create("lacunarity", "l", MFnNumericData::kFloat, 2.0f);
    numericAttr.setReadable(false);
    numericAttr.setWritable(true);
    numericAttr.setStorable(true);
    stat = addAttribute(m_lacunarity);
    if (!stat)
        return stat;

    m_fractalGain = numericAttr.create("fractalGain", "fg", MFnNumericData::kFloat, 0.5);
    numericAttr.setReadable(false);
    numericAttr.setWritable(true);
    numericAttr.setStorable(true);
    stat = addAttribute(m_fractalGain);
    if (!stat)
        return stat;

    // Output node attributes
    m_outMesh = typedAttr.create("outMesh", "om", MFnData::kMesh);
	typedAttr.setReadable(true);
	typedAttr.setWritable(false);
	typedAttr.setStorable(false);
	stat = addAttribute(m_outMesh);
	if (!stat)
		return stat;

	// Connect input/output dependencies
	attributeAffects(m_inMesh, m_outMesh);
    attributeAffects(m_spaceType, m_outMesh);
    attributeAffects(m_noiseType, m_outMesh);
	attributeAffects(m_amplitude, m_outMesh);
    attributeAffects(m_seed, m_outMesh);
    attributeAffects(m_frequency, m_outMesh);
    attributeAffects(m_fractalOctaves, m_outMesh);
    attributeAffects(m_lacunarity, m_outMesh);
    attributeAffects(m_fractalGain, m_outMesh);

	// Return success
	return MStatus::kSuccess;
}
//-----------------------------------------------------------------------------
MStatus HeightField::compute(const MPlug &_plug, MDataBlock &_data)
{
	MStatus stat;
	// Check if the plug is the output plug
	if (_plug == m_outMesh)
	{
        // Get the input data handles and typecast
        MDataHandle inMeshDataHandle = _data.inputValue(m_inMesh);
		MObject inMeshValue = inMeshDataHandle.asMesh();

        MDataHandle spaceTypeDataHandle = _data.inputValue(m_spaceType);
        MSpace::Space spaceTypeValue = (MSpace::Space)spaceTypeDataHandle.asShort();

        MDataHandle noiseTypeDataHandle = _data.inputValue(m_noiseType);
        FastNoise::NoiseType noiseTypeValue = (FastNoise::NoiseType)noiseTypeDataHandle.asShort();

        MDataHandle amplitudeDataHandle = _data.inputValue(m_amplitude);
        float amplitudeValue = amplitudeDataHandle.asFloat();

        MDataHandle seedDataHandle = _data.inputValue(m_seed);
        int seedValue = seedDataHandle.asInt();

        MDataHandle frequencyDataHandle = _data.inputValue(m_frequency);
        float frequencyValue = frequencyDataHandle.asFloat();

        MDataHandle fractalOctavesDataHandle = _data.inputValue(m_fractalOctaves);
        int fractalOctavesValue = fractalOctavesDataHandle.asInt();

        MDataHandle lacunarityDataHandle = _data.inputValue(m_lacunarity);
        float lacunarityValue = lacunarityDataHandle.asFloat();

        MDataHandle fractalGainDataHandle = _data.inputValue(m_fractalGain);
        float fractalGainValue = fractalGainDataHandle.asFloat();

        // Get the data handle for the output value
        MDataHandle outMeshDataHandle = _data.outputValue(m_outMesh);

		// Set FastNoise parameters
        m_fastNoise.SetNoiseType(noiseTypeValue);
        // Only set the seed if it has changed
        if (m_fastNoise.GetSeed() != seedValue)
            m_fastNoise.SetSeed(seedValue);
        m_fastNoise.SetFrequency(frequencyValue);
        m_fastNoise.SetFractalOctaves(fractalOctavesValue);
        m_fastNoise.SetFractalLacunarity(lacunarityValue);
        m_fastNoise.SetFractalGain(fractalGainValue);

		// Create a function set for the input mesh
        MFnMesh inMeshFn(inMeshValue);

		// Create a mesh data object and a new MObject
        MFnMeshData meshDataFn;
        MObject outMeshObj = meshDataFn.create();
		// Create a function set for the new mesh
		MFnMesh newMeshFn;
        newMeshFn.copy(inMeshValue, outMeshObj);

		// Get the vertices of the original mesh
		MPointArray vertices;
        stat = inMeshFn.getPoints(vertices, spaceTypeValue);

		// Iterate through each point and adjust the y value
		float height = 0.0f;
		MVector heightDisplacement(0.0, 0.0, 0.0);
        size_t numVertices = vertices.length();
		for (size_t i = 0; i < numVertices; ++i)
		{
			MPoint& currentPoint = vertices[i];
            height = m_fastNoise.GetNoise(currentPoint.x, currentPoint.z) * amplitudeValue;
			heightDisplacement.y = height;
			currentPoint += heightDisplacement;
		}
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
HeightField::HeightField(){}
//-----------------------------------------------------------------------------
HeightField::~HeightField(){}
//-----------------------------------------------------------------------------
