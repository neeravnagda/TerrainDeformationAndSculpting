#include "SculptLayerCmd.h"
#include <maya/MFnPlugin.h>

//----------------------------------------------------------------------------------------------------------------------
MStatus initializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj, "NeeravNagda", "1.0" , "Any");

    status = plugin.registerCommand( "createSculptLayer", SculptLayerCmd::creator );
    if ( !status )
    {
        status.perror("Unable to register command \"createSculptLayer\"");
        return status;
    }

    return status;
}
//----------------------------------------------------------------------------------------------------------------------
MStatus uninitializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj);

    status = plugin.deregisterCommand( "createSculptLayer" );
    if ( !status )
    {
        status.perror("Unable to deregister command \"createSculptLayer\"");
        return status;
    }

    return status;
}
//----------------------------------------------------------------------------------------------------------------------

