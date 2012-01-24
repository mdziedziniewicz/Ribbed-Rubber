import rhinoscriptsyntax as rs
import os
import System.Drawing.Color
import Rhino
import scriptcontext

addresss = "C:\R3\OffCenter\Walk\joint_library2.dat"


#Decimal display and decimal places
#rs.UnitDistanceDisplayMode(0) 
#rs.UnitDistanceDisplayPrecision(7)


def Pt2Str(pt):
    
    return str(pt[0]) + "," + str(pt[1]) + "," + str(pt[2])


def WritePolies(address,jointlist):
    #Rhino used to convert numbers to string to 3 decimal places only unless 
    #rs.UnitDistanceDisplayPrecision is implemented which wasn't 
    #in the Rhino package when this code was written
    
    
    strFile=address 
    
    
    file = open(strFile, "w")
    
    
    #FIRST - SPECIAL CASE FOR THE JOINT 0
    str = ""
    
    poly = jointlist[0]
    
    #placement point
    str = str + Pt2Str(poly[0]) + ";"
    
    #initial add-on vector
    str = str + Pt2Str(poly[1]) + ";"
    
    #the tip
    for j in range(len(poly[2])-1):
        str = str + Pt2Str(poly[2][j]) + "#"
    
    str = str + Pt2Str(poly[2][len(poly[2])-1]) + "\n"
    
    file.write(str) 
    
    
    #THEN - ALL ELSE
    for poly in jointlist[1:]:
        
        str = ""
        
        #placement point
        str = str + Pt2Str(poly[0]) + ";"
        
        #initial add-on vector
        str = str + Pt2Str(poly[1]) + ";"
            
        #Left side of the joint
        
        for j in range(len(poly[2])-1):
            str = str + Pt2Str(poly[2][j]) + "#"
        
        str = str + Pt2Str(poly[2][len(poly[2])-1]) + ";"
        
        #Right side of the joint
        
        for j in range(len(poly[3])-1):
            str = str + Pt2Str(poly[3][j]) + "#"
        
        str = str + Pt2Str(poly[3][len(poly[3])-1]) + ";"
        
        #output direction vector
        
        str = str + Pt2Str(poly[4]) + "\n"
        
        file.write(str)
        
    file.close()




def Main():
    
    jointno = 4
    
    list = []
    
    dir0 = rs.GetPoint("from")
    dir1 = rs.GetPoint("hub")
    dir2 = rs.GetPoints(False,False,"outline_left_to_right")
    
    #THIS VECTOR WILL ALLOW US TO TAKE INTO ACCOUNT POSSIBLE LAYOUT OF DRAWN JOINTS ON THE PAGE
    fix = rs.VectorSubtract([0,0,0],dir1)
    
    dir0 = rs.VectorAdd(dir0,fix)
    dir1 = rs.VectorAdd(dir1,fix)
    indir = rs.VectorSubtract(dir1,dir0)
    
    for j in range(len(dir2)):
        pt = rs.VectorAdd(dir2[j],fix)
        dir2[j] = pt
        
    list.append([dir1,indir,dir2])
    
    
    
    for i in (range(jointno)[1:]):
        
        
        dir0 = rs.GetPoint("from")
        dir1 = rs.GetPoint("hub")
        dir2 = rs.GetPoint("to")
        
        
        
        #THIS VECTOR WILL ALLOW US TO TAKR INTO ACCOUNT POSSIBLE LAYOUT OF DRAWN JOINTS ON THE PAGE
        fix = rs.VectorSubtract([0,0,0],dir1)
        
        #What is this line doing???
        dir0 = rs.VectorAdd(dir0,fix)
        dir1 = rs.VectorAdd(dir1,fix)
        dir2 = rs.VectorAdd(dir2,fix)
        
        #Setting up direction vectors!
        indir = rs.VectorSubtract(dir1,dir0)
        outdir = rs.VectorSubtract(dir2,dir1)
        
        lside = rs.GetPoints(False,False,"left")
        rside = rs.GetPoints(False,False,"right")
        
        for j in range(len(lside)):
            pt = rs.VectorAdd(lside[j],fix)
            lside[j] = pt
        
        
        for j in range(len(rside)):
            pt = rs.VectorAdd(rside[j],fix)
            rside[j] = pt
        
        
        list.append([dir1,indir,lside,rside,outdir])
        
    
    
    WritePolies(addresss,list)



Main()

