import rhinoscriptsyntax as rs
import scriptcontext
import os
import math
import Rhino

di = "C:\R3\OffCenter\Walk"
fil = "joint_library.dat"


#Decimal display and decimal places
#NOT IMPLEMENTED IN PYTHON YET
#
#rs.UnitDistanceDisplayMode(0) 
#rs.UnitDistanceDisplayPrecision(7)


fc = 1


arrlist = [0]

#arrlist = [5,10,9,9,4,5,7,10,7,3,9,0]
arrlist = [0]
refpt = [math.sqrt(2)/2,-math.sqrt(2)/2,0]
dir = [math.sqrt(2)/2,-math.sqrt(2)/2,0]






def Shift(res,trim):
    
    left = []
    right = []
    
    
    for j in range(len(res[1])):
        left.append(rs.VectorAdd(res[1][j],[0,0,-1*trim]))
        
    for j in range(len(res[2])):
        right.append(rs.VectorAdd(res[2][j],[0,0,-1*trim]))
    
    
    return [res[0],left,right]

def StripBuild(data1,data2):
    total = []
    
    for i in range(len(data1)-1):
        total.append(rs.AddSrfPt([data1[i],data1[i+1],data2[i+1],data2[i]]))
        
    return total 


def StartCap(stuff):
    
    plyu = [stuff[0][0][0],stuff[0][0][1],stuff[0][1][1],stuff[0][1][0]]
    plyd = [stuff[1][0][0],stuff[1][0][1],stuff[1][1][1],stuff[1][1][0]]
    
    polu = rs.AddPolyline(plyu)
    pold = rs.AddPolyline(plyd)
    
    up = rs.AddPlanarSrf([polu])
    down = rs.AddPlanarSrf([pold])
    
    rs.DeleteObjects([polu,pold])
    
    return [[up[0]],[down[0]]]



def ZeroCap(stuff1,stuff2):
    
    uplink = rs.AddSrfPt([stuff2[0][0][len(stuff2[0][0])-1],stuff1[0][0][0],stuff1[0][1][0],stuff2[0][1][len(stuff2[0][1])-1]])
    downlink = rs.AddSrfPt([stuff2[1][0][len(stuff2[1][0])-1],stuff1[1][0][0],stuff1[1][1][0],stuff2[1][1][len(stuff2[1][1])-1]])
    
    return [[uplink],[downlink]]




def ChainLink(L,R):
    #takes two parts of a closed polygon and makes a valid closed polyline out of it - the paths don't overlap
    path = []
    
    size = len(L)+len(R)+1
    
    for i in range(size):
        path.append(" ")
        
    
    for i in range(size-1):
        if (i <= len(L)-1): 
            path[i] = L[i]
        else:
            path[i] = R[size-2-i]
         
    #this line is to make sure that the starting point of the polyline is indeed doubled
    path[size-1] = L[0]
    
    return path


def EltCap(stuff1,stuff2):
    
    plyu = ChainLink(stuff1[0][0],stuff1[0][1])
    plyd = ChainLink(stuff1[1][0],stuff1[1][1])
    
    polu = rs.AddPolyline(plyu)
    pold = rs.AddPolyline(plyd)
    
    up = rs.AddPlanarSrf([polu])
    down = rs.AddPlanarSrf([pold])
    
    uptransition = [stuff2[0][0][len(stuff2[0][0])-1],stuff1[0][0][0],stuff1[0][1][0],stuff2[0][1][len(stuff2[0][1])-1]]
    dntransition = [stuff2[1][0][len(stuff2[1][0])-1],stuff1[1][0][0],stuff1[1][1][0],stuff2[1][1][len(stuff2[1][1])-1]]
    
    uplink = rs.AddSrfPt(uptransition)
    downlink = rs.AddSrfPt(dntransition)
    
    rs.DeleteObjects([polu,pold])
    
    return [[uplink,up[0]],[downlink,down[0]]]


def EndingCap(stuff1,stuff2):
    
    plyu = ChainLink(stuff1[0][0],stuff1[0][1])
    plyd = ChainLink(stuff1[1][0],stuff1[1][1])
    
    rs.AddPoints(plyu)
    rs.AddPoints(plyd)
    
    polu = Rhino.Geometry.Polyline(plyu)
    pold = Rhino.Geometry.Polyline(plyd)
    
    polu = scriptcontext.doc.Objects.AddPolyline(plyu)
    pold = scriptcontext.doc.Objects.AddPolyline(plyd)
    
    up = rs.AddPlanarSrf([polu])
    down = rs.AddPlanarSrf([pold])
    
    
    rs.AddPoints([stuff2[0][0][len(stuff2[0][0])-1],stuff1[0][0][0],stuff1[0][1][0],stuff2[0][1][len(stuff2[0][1])-1]])
    rs.AddPoints([stuff2[1][0][len(stuff2[1][0])-1],stuff1[1][0][0],stuff1[1][1][0],stuff2[1][1][len(stuff2[1][1])-1]])

    uplink = rs.AddSrfPt([stuff2[0][0][len(stuff2[0][0])-1],stuff1[0][0][0],stuff1[0][1][0],stuff2[0][1][len(stuff2[0][1])-1]])
    downlink = rs.AddSrfPt([stuff2[1][0][len(stuff2[1][0])-1],stuff1[1][0][0],stuff1[1][1][0],stuff2[1][1][len(stuff2[1][1])-1]])
    
    rs.DeleteObjects([polu,pold])
    
    return [[uplink,up[0]],[downlink,down[0]]]



def Transform(dir,ninety,pt):
    
    v1 = Rhino.Geometry.Vector3d(-1,0,0)
    v2 = Rhino.Geometry.Vector3d(0,-1,0)
    v3 = Rhino.Geometry.Vector3d(0,0,1)
    v4 = Rhino.Geometry.Vector3d(0,0,1)
    
    translation = Rhino.Geometry.Vector3d(pt[0],pt[1],pt[2])
    
    xfrm1 = Rhino.Geometry.Transform.Rotation(v1,v2,v3, dir, ninety, v4)
    #xfrm1 = rs.XformRotation5(v1,v2,v3, dir, ninety, v4)
    xfrm2 = Rhino.Geometry.Transform.Translation(translation)
    #xfrm2 = rs.XformTranslation(pt)
    xfrm = Rhino.Geometry.Transform.Multiply(xfrm2,xfrm1)
    #xfrm = rs.XformMultiply(xfrm2,xfrm1)
    
    return xfrm


def Start(refpt,dir,data):
    
    
    xform = Transform(rs.VectorReverse(dir),rs.VectorReverse(rs.VectorRotate(dir,90,[0,0,1])),refpt)
    
    both = []
    
    for point in data[2]:
        
        trans = rs.VectorTransform(point,xform)
        trans = rs.VectorAdd(trans,refpt)
        both.append(trans)
    
    L = [both[1],both[2]]
    R = [both[1],both[0]]
    
    trans = rs.VectorTransform(data[1],xform)
    
    #'Special case here:
    return [rs.VectorReverse(trans),L,R]


def Ending(refpt,dir,data):
    
    
    xform = Transform(dir,rs.VectorRotate(dir,90,[0,0,1]),refpt)
    
    both = []
    
    for point in data[2]:
        
        trans = rs.VectorTransform(point,xform)
        trans = rs.VectorAdd(trans,refpt)
        both.append(trans)
    
    L = [both[0],both[1]]
    R = [both[2],both[1]]
    
    trans = rs.VectorTransform(data[1],xform)
    
    return [trans,L,R]


def Elt(refpt,dir,data):
    
    
    xform = Transform(dir,rs.VectorRotate(dir,90,[0,0,1]),refpt)
    
    L = []
    R = []
    
    
    for point in data[2]:
        
        trans = rs.VectorTransform(point,xform)
        trans = rs.VectorAdd(trans,refpt)
        L.append(trans)
        
    y =0
    for point in data[3]:
        
        trans = rs.VectorTransform(point,xform)
        trans = rs.VectorAdd(trans,refpt)
        R.append(trans)
        
    
    trans = rs.VectorTransform(data[4],xform)
    
    return [trans,L,R]


def __point_from_string(text):
    items = text.strip("()\n").split(",")
    x = float(items[0])
    y = float(items[1])
    z = float(items[2])
    return [x,y,z]


def ReadJoints(dir,file):
    
    arrFileInfo = []
    
    ForReading = 1
    
    #Get the filename to create
    strFileName1 = dir + "\\" + file
    
    
    lineElts = []
    
    
    counter = 0
    
    file = open(strFileName1, "r")
    contents = file.readlines()
    
    for line in contents:
       
        str1stChr = line[0]
        
        left = []
        right = []
        
        if (str1stChr != "'"):
            
            splitLine = line.split(";")
            
            if (counter == 0):
                pt = __point_from_string(splitLine[0])
                indir = __point_from_string(splitLine[1])
                
                point = splitLine[2].split("#")
                for i in range(len(point)):
                    left.append(__point_from_string(point[i]))
                
                lineElts.append([pt,indir,left])
                
            else:
                pt = __point_from_string(splitLine[0])
                indir = __point_from_string(splitLine[1])
                
                point = splitLine[2].split("#")
                for i in range(len(point)):
                    left.append(__point_from_string(point[i]))
                
                point = splitLine[3].split("#")
                for i in range(len(point)):
                    right.append(__point_from_string(point[i]))
                
                
                outdir = __point_from_string(splitLine[4])
                
                
                lineElts.append([pt,indir,left,right,outdir])
                
            
            counter = counter+1
            
        
    file.close
    return lineElts



def Outline(refpt,dir,arrlist):
    
    
    data = ReadJoints(di,fil)
    
    
    O = -1
    
    trim = 1
    
    left = []
    upl = []
    right = []
    upr = []
    
    
    res = Start(refpt,dir,data[0])
    dir = res[0]
    
    for j in range(len(res[1])):
        upl.append(rs.VectorAdd(res[1][j],[0,0,-1*trim]))
        left.append(res[1][j])
    for j in range(len(res[2])):
        upr.append(rs.VectorAdd(res[2][j],[0,0,-1*trim]))
        right.append(res[2][j])
    
    
    store = [[left,right],[upl,upr]]
    
    
    info2 = data[0]
    
    
    for i in range(len(arrlist)):
    
        trim = trim*fc
        
        refpt = rs.VectorAdd(refpt,dir)
        
        info = data[arrlist[i]]
        
        if (i < len(arrlist)-1):   
            
            res = Elt(refpt,dir,info)
            res1 = Shift(res,trim)
            
            dir = res[0]
            for j in range(len(res[1])):
                upl.append(rs.VectorAdd(res[1][j],[0,0,-1*trim]))
                left.append(res[1][j])
            for j in range(len(res[2])):
                upr.append(rs.VectorAdd(res[2][j],[0,0,-1*trim]))
                right.append(res[2][j])
            
            store2 = [[res[1],res[2]],[res1[1],res1[2]]]
            
            
            store = store2
            
        else:
            
            res = Ending(refpt,dir,info)
            res1 = Shift(res,trim)
            
            dir = res[0]
            for j in range(len(res[1])):
                upl.append(rs.VectorAdd(res[1][j],[0,0,-1*trim]))
                left.append(res[1][j])
            for j in range(len(res[2])):
                upr.append(rs.VectorAdd(res[2][j],[0,0,-1*trim]))
                right.append(res[2][j])
            
            store2 = [[res[1],res[2]],[res1[1],res1[2]]]
            
           
            store = store2
            
        
        info2 = info
        
    
    
    l1 = rs.AddPolyline(left)
    r1 = rs.AddPolyline(right)
    #l2 = rs.AddPolyline(upl)
    #r2 = rs.AddPolyline(upr)
    
    
    output = rs.JoinCurves([l1,r1],True)
    
    return rs.PolylineVertices(output[0])


def Arm(refpt,dir,arrlist):
    
    
    data = ReadJoints(di,fil)
    
    
    O = -1
    
    trim = 1
    
    left = []
    upl = []
    right = []
    upr = []
    
    up = []
    down = []
    
    
    res = Start(refpt,dir,data[0])
    dir = res[0]
    
    for j in range(len(res[1])):
        upl.append(rs.VectorAdd(res[1][j],[0,0,-1*trim]))
        left.append(res[1][j])
    for j in range(len(res[2])):
        upr.append(rs.VectorAdd(res[2][j],[0,0,-1*trim]))
        right.append(res[2][j])
    
    
    store = [[left,right],[upl,upr]]
    
    
    srfu = []
    srfd = []
    cps = StartCap(store)
    
    
    for k in range(len(cps[0])):
        srfu.append(cps[0][k])
        srfd.append(cps[1][k])
    
    
    info2 = data[0]
    
    
    
    for i in range(len(arrlist)):
        
        trim = trim*fc
    
        refpt = rs.VectorAdd(refpt,dir)
        
        info = data[arrlist[i]]
        
        if (i < len(arrlist)-1):    
            
            test = 0
            
            res = Elt(refpt,dir,info)
            res1 = Shift(res,trim)
            
            dir = res[0]
            for j in range(len(res[1])):
                upl.append(rs.VectorAdd(res[1][j],[0,0,-1*trim]))
                left.append(res[1][j])
            for j in range(len(res[2])):
                upr.append(rs.VectorAdd(res[2][j],[0,0,-1*trim]))
                right.append(res[2][j])
            
            store2 = [[res[1],res[2]],[res1[1],res1[2]]]
            
            test = 0
            
            if (len(res[1])> 1 or len(res[2])>1):
                
                cps = EltCap(store2,store)
                
                for k in range(len(cps[0])):
                    srfu.append(cps[0][k])
                    srfd.append(cps[1][k])
                
            else:
                
                cps = ZeroCap(store2,store)
                
                for k in range(len(cps[0])):
                    srfu.append(cps[0][k])
                    srfd.append(cps[1][k])
            test = 0
            store = store2
            
        else:
            
            res = Ending(refpt,dir,info)
            res1 = Shift(res,trim)
            
            dir = res[0]
            for j in range(len(res[1])):
                upl.append(rs.VectorAdd(res[1][j],[0,0,-1*trim]))
                left.append(res[1][j])
            for j in range(len(res[2])):
                upr.append(rs.VectorAdd(res[2][j],[0,0,-1*trim]))
                right.append(res[2][j])
            
            store2 = [[res[1],res[2]],[res1[1],res1[2]]]
            
            cps = EndingCap(store2,store)
                            
            for k in range(len(cps[0])):
                srfu.append(cps[0][k])
                srfd.append(cps[1][k])
                
            store = store2
            
            
        info2 = info
        
    
    
    #l1 = rs.AddPolyline(left)
    #r1 = rs.AddPolyline(right)
    #l2 = rs.AddPolyline(upl)
    #r2 = rs.AddPolyline(upr)
    
    
    sidel = StripBuild(left,upl)
    sider = StripBuild(right,upr)

    surf["str0","str1","str2","str3"]
    surf[0] = rs.JoinSurfaces(sidel, True)
    surf[1] = rs.JoinSurfaces(sider, True)
    surf[2] = rs.JoinSurfaces(srfu, True)
    surf[3] = rs.JoinSurfaces(srfd, True)
    
    
    return rs.JoinSurfaces(surf, True) 



#rs.EnableRedraw(False)
Arm(refpt,dir,arrlist)
#rs.EnableRedraw(True)