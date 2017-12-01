#include "HeightFieldNode.h"
#include <maya/MFnPlugin.h>
//-----------------------------------------------------------------------------
MStatus initializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj, "NeeravNagda", "Any");

    status = plugin.registerNode("HeightFieldNode", HeightField::m_id, &HeightField::creator, &HeightField::initialize, MPxNode::kDependNode);
    if (!status)
    {
        status.perror("Unable to register HeightFieldNode");
        return status;
    }

    return status;
}
//-----------------------------------------------------------------------------
MStatus uninitializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj);

    status = plugin.deregisterNode(HeightField::m_id);
    if (!status)
    {
        status.perror("Unable to deregister HeightFieldNode");
        return status;
    }

    return status;
}
//-----------------------------------------------------------------------------
