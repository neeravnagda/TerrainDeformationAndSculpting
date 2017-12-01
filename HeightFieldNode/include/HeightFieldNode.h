/// @file HeightFieldNode.h
/// Create a height field with noise

#ifndef HEIGHTFIELDNODE_H__
#define HEIGHTFIELDNODE_H__

#include <maya/MTypeId.h>
#include <maya/MStatus.h>
#include <maya/MGlobal.h>
#include <maya/MPxLocatorNode.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MNodeMessage.h>
#include <maya/MMessage.h>
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
    ~HeightField();

  private:
    //-----------------------------------------------------------------------------
    // Width of the height field
    //-----------------------------------------------------------------------------
    MObject m_width;
    //-----------------------------------------------------------------------------
    // Depth of the height field
    //-----------------------------------------------------------------------------
    MObject m_depth;
    //-----------------------------------------------------------------------------
    // Resolution of the height field
    //-----------------------------------------------------------------------------
    MObject m_resolution;
    //-----------------------------------------------------------------------------
    // Amplitude
    //-----------------------------------------------------------------------------
    MObject m_amplitude;
    //-----------------------------------------------------------------------------
    // FastNoise object
    //-----------------------------------------------------------------------------
    FastNoise m_fastNoise;

};

#endif
