#include "SculptLayerNode.h"
#include <maya/MFnPlugin.h>
//-----------------------------------------------------------------------------
MStatus initializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj, "NeeravNagda", "Any");

    status = plugin.registerNode("SculptLayerNode", SculptLayer::m_id, &SculptLayer::creator, &SculptLayer::initialize, MPxNode::kDependNode);
    if (!status)
    {
        status.perror("Unable to register SculptLayerNode");
        return status;
    }

    return status;
}
//-----------------------------------------------------------------------------
MStatus uninitializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj);

    status = plugin.deregisterNode(SculptLayer::m_id);
    if (!status)
    {
        status.perror("Unable to deregister SculptLayerNode");
        return status;
    }

    return status;
}
//-----------------------------------------------------------------------------
