#------------------------------------------------------------------------------
# QT settings
#------------------------------------------------------------------------------

# Remove QT core and gui
QT -= core gui

#------------------------------------------------------------------------------
# Plugin settings
#------------------------------------------------------------------------------

# Name of the plugin
TARGET = HeightFieldNode
# Need a bundle for Mac OS
macx:TARGET=HeightFieldNode.bundle

#------------------------------------------------------------------------------
# File paths
#------------------------------------------------------------------------------

DESTDIR = ../
OBJECTS_DIR = obj
INCLUDEPATH+=include

#------------------------------------------------------------------------------
# Files
#------------------------------------------------------------------------------

SOURCES+=src/*.cpp
HEADERS+=include/*.h

#------------------------------------------------------------------------------
# Maya settings
#------------------------------------------------------------------------------

DEFINES+=REQUIRE_IOSTREAM \
         _BOOL

MAYALIBS=-lOpenMaya \
        -lFoundation

#------------------------------------------------------------------------------
# Linux settings
#------------------------------------------------------------------------------

linux-*:TEMPLATE = lib
linux-*:MAYALOCATION=/opt/autodesk/maya2017/
linux-*:DEVKITLOCATION=/home/i7421407/Maya2017_Update3_DEVKIT_Linux/devkitBase

linux-*:INCLUDEPATH += $$DEVKITLOCATION/include \
                        /usr/X11R6/include

linux-*:LIBS += -L$$MAYALOCATION/lib \
                   $$MAYALIBS

linux:DEFINES+=linux

#------------------------------------------------------------------------------
# Mac OS settings
#------------------------------------------------------------------------------

macx:DEFINES+=OSMac_
macx:DEFINES+=__x86_64__
macx:MAYALOCATION=/Applications/Autodesk/maya2017
macx:CONFIG -= app_bundle
macx:INCLUDEPATH+=$$MAYALOCATION/devkit/include
macx:INCLUDEPATH+=/opt/X11/include
macx:LIBS+= -framework OpenGL
macx:QMAKE_MAC_SDK = macosx10.11

macx:LIBS +=-bundle
mac:LIBS -=-dynamiclib
macx:LIBS += -L$$MAYALOCATION/Maya.app/Contents/MacOS \
             $$MAYALIBS
