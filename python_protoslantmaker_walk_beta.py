import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import os

rs.Command("_SelAll")
rs.Command("_Delete")



dirsname = 'Users\Michal\Desktop\hahaha'
if not os.path.isdir('/' + dirsname + '/'):
    os.makedirs('/' + dirsname + '/')




tiny = 0.000000000001
offset = 0.0625

rhUnitInches = 8
#intSystem = Rhino.UnitSystem(self)

#If (intSystem != 9):
Rhino.UnitSystem.Inches


#move_it = [${xx},${yy},0]
#height = ${hh}

move_it = [2,2,0]
height = 1



def SetUp(offset,h):

    sheet = rs.AddBox([[-10,-10,h],[10,-10,h],[10,10,h],[-10,10,h],[-10,-10,0],[10,-10,0],[10,10,0],[-10,10,0]])
    bigSheet = sheet

    box2 = rs.AddBox([[-5.25,-5.25,1],[5.25,-5.25,1],[5.25,5.25,1],[-5.25,5.25,1],[-5.25,-5.25,-2],[5.25,-5.25,-2],[5.25,5.25,-2],[-5.25,5.25,-2]])

    rs.MoveObject(box2, move_it)

    ribc = rs.BooleanIntersection([box2],[bigSheet],True)



    rs.SelectObject(ribc)
    rs.Command("_-Export C:\\" + dirsname + "\\protoslant_walk.igs ENTER")
    rs.Command("_SelNone")
    Rhino.FileIO.File3dm.Polish
    
    #fileName = Rhino.FileIO.File3dm
    
    #Rhino.FileIO.File3dm.Write(fileName,"C:\\"+dirsname+"\\protoslant_walk.3dm",5)
    rs.Command("_-Save C:\\" + dirsname + "\\protoslant_walk.3dm ENTER")



SetUp(move_it,height)

#this line shuts rhino once the code has run
#rs.Exit()