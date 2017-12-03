/// @file HeightFieldNode.h
/// Create a height field with noise

#ifndef HEIGHTFIELDNODE_H__
#define HEIGHTFIELDNODE_H__

#include <maya/MDataBlock.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MStatus.h>
#include <maya/MTypeId.h>
#include "FastNoise.h"

class HeightField : public MPxNode
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
    // Calculate noise on each point
    //-----------------------------------------------------------------------------
    virtual MStatus compute(const MPlug &_plug, MDataBlock &_data);
    //-----------------------------------------------------------------------------
    // Constructor
    //-----------------------------------------------------------------------------
    HeightField();
    //-----------------------------------------------------------------------------
    // destructor
    //-----------------------------------------------------------------------------
    virtual ~HeightField();

  private:
    //-----------------------------------------------------------------------------
    // Input mesh
    //-----------------------------------------------------------------------------
    static MObject m_inMesh;
    //-----------------------------------------------------------------------------
    // Amplitude
    //-----------------------------------------------------------------------------
    static MObject m_amplitude;
    //-----------------------------------------------------------------------------
    // Amplitude
    //-----------------------------------------------------------------------------
    static MObject m_outMesh;
    //-----------------------------------------------------------------------------
    // FastNoise object
    //-----------------------------------------------------------------------------
    FastNoise m_fastNoise;
};

#endif
