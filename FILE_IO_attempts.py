
import System
import System.Collections.Generic as SCG
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext

from Rhino.FileIO import FileWriteOptions
from Rhino.FileIO import FileReadOptions

def importFiles(filePathList):
    '''Import a list of files'''
    opt = FileReadOptions()
    opt.ImportMode = True
    for f in filePathList:
        print 'Importing %s' % f
        scriptcontext.doc.ReadFile(f, opt)

def exportFile(filePath,version=4,geomOnly=False,selectedOnly=False,):

    opt = FileWriteOptions()
    opt.FileVersion = version
    opt.WriteGeometryOnly = geomOnly
    opt.WriteSelectedObjectsOnly = selectedOnly
    gf = scriptcontext.doc.WriteFile(filePath, opt)
    return gf

print exportFile("C:\R3\OffCenter\Walk\\test.3dm",4,False,False)

importFiles(["C:\R3\OffCenter\Walk\\baba.3dm"])