/// @file SculptLayerCmd.h
/// Create a sculpt layer

#ifndef SCULPTLAYERCMD_H__
#define SCULPTLAYERCMD_H__

#include <maya/MArgList.h>
#include <maya/MGlobal.h>
#include <maya/MPxCommand.h>

class SculptLayerCmd : public MPxCommand
{
    public:
        virtual ~SculptLayerCmd();
        MStatus doIt(const MArgList &args);
        MStatus redoIt();
        MStatus undoIt();
        bool isUndoable() const;
        static void* creator();
};

#endif
