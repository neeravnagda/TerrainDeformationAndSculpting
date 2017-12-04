#include <unordered_set>

#include <maya/MSelectionList.h>
#include <maya/MObject.h>
#include <maya/MDagPath.h>
#include <maya/MItMeshVertex.h>
#include <maya/MIntArray.h>

#include "SculptLayerCmd.h"

SculptLayerCmd::~SculptLayerCmd(){}

MStatus SculptLayerCmd::doIt(const MArgList &args)
{
    // Since there is no argument parsing, just call the redo function
    return redoIt();
}

MStatus SculptLayerCmd::redoIt()
{
    // Get the selection list
    MSelectionList selectionList;
    MGlobal::getActiveSelectionList(selectionList);

    // Get the vertices component from the selection list
    MDagPath dagPath;
    MObject vertices;
    selectionList.getDagPath(0,dagPath, vertices);

    std::unordered_set<int> faceList;

    MItMeshVertex vertexIterator(dagPath, vertices);
    while (!vertexIterator.isDone())
    {
        MIntArray faces;
        vertexIterator.getConnectedFaces(faces);

        for (size_t i=0; i<faces.length(); ++i)
        {
            faceList.emplace(faces[i]);
        }

        vertexIterator.next();
    }

    return MStatus::kSuccess;
}

MStatus SculptLayerCmd::undoIt()
{
    return MStatus::kSuccess;
}

bool SculptLayerCmd::isUndoable() const
{
    return true;
}

void* SculptLayerCmd::creator()
{
    return new SculptLayerCmd();
}
