import rhinoscriptsyntax as rs
import os
import System.Drawing.Color
import Rhino
import scriptcontext
from Rhino.FileIO import FileWriteOptions

#SELF-MADE LIBRARIES
import History
import JointAccess


tiny = 0.000000000001
offset = 0.0625
depth = 1
move_it = [0,0,0]


#DIRECTORIES
di = "C:\R3\OffCenter\Walk"
fil = "joint_library.dat"
folder = "C:\R3\OffCenter\Walk\Data"
tempfolder = "C:\R3\OffCenter\Walk\Temp"
file = "polies.txt"

#TAPER FACTOR
fc = 0.9


#CONSTANTS
noribs = 16


#Decimal display and decimal places
#NOT YET IMPLEMENTED
#rs.UnitDistanceDisplayMode (0] 
#rs.UnitDistanceDisplayPrecision (7]



def exportFile(filePath,version=4,geomOnly=False,selectedOnly=False,):

    opt = FileWriteOptions()
    opt.FileVersion = version
    opt.WriteGeometryOnly = geomOnly
    opt.WriteSelectedObjectsOnly = selectedOnly
    gf = scriptcontext.doc.WriteFile(filePath, opt)
    print gf
    return gf

def SaveNClean(defject,vertices,i,content):
    #save all there is to run from current iteration and clean up proper
    
    rs.Command("_SelNone")
    rs.Command("_SelPolysrf")
    
    index = i 
    if index<10:
        j = "0" + str(index)
    if index>= 10:
        j = str(index)
    
    #Quite probably there is a purely scripted way of writing the export now
    #It would be through the Rhino and scriptcontext
    rs.Command("_-Export C:\R3\OffCenter\Walk\Temp\proto2o" + j + ".igs ENTER")
    rs.DeleteObject(defject)
    
    all = rs.AllObjects()
    rs.DeleteObjects(all)
    
    for vrtx in vertices:
        rs.AddPolyline(vrtx)    
    
    #Again
    exportFile("C:\\R3\OffCenter\Walk\Temp\sth" + j + ".3dm",4,False,False)
    
    objects = rs.AllObjects() 
    rs.DeleteObjects(objects)
    
    #need a place to write our polies to!!!
    
    History.WritePolies(tempfolder + "\polies" + j + ".txt",content)



def Generation():
    
    #SETTING UP THE FILE ACCESS TO READ ALL THERE IS TO BE READ
    #THE SCRIPT FROM NOW ON LOOKS for FILE AND if IT CANNOT FIND ONE IT WILL HAVE TO MAKE ONE
    
    #SOOO WE START BY LOOKING for AND READING THE FILE if WE FIND IT
    
    ##     
    ########################################################################
    #READ INFO IN THE FILE
    ########################################################################
   
    #ReadFile returns an array of [isAlive,startPoint,jointNos]
    content = History.ReadPolies(folder,file)
    
    
    rhUnitInches = 8
    rs.UnitSystem(rhUnitInches, False, True)
    
    zero = [0,0,0]
    zaxis = [0,0,1]
    
    vrt = []
    
    
    
    #Decimal display and decimal places
    #rs.UnitDistanceDisplayMode(0) 
    #rs.UnitDistanceDisplayPrecision(7)
    
    
    #sth to control that we have an [0,0,0] to check
    endcheck = 1
    
    size = 1
    living = []
    startpts = []
    sequences = []
    
    
    #if we read nothing we should save 1 starting point - namely [0,0,0]
    if content is None:
        
        living = [1]
        startpts = [[0,0,0]]
        sequences = [[0]]
        npolies = 0
        content = [[living[0],startpts[0],sequences[0]]]
        endcheck = 0
        
    else:
        
        for rib in content:
            living.append(rib[0])
            startpts.append(rib[1])
            sequences.append(rib[2])
        
        #checking if new rib has actualy been started
        #[0,0,0] will always be there to be grown
        if rs.Distance(content[-1][1],[0,0,0])<tiny:
            endcheck = 0
            
        
        # if not and we have less than 4 legs start a new leg at [0,0,0]    
        if (endcheck != 0 and len(content)<4):
            ribs = content
            ribs.append([1,[0,0,0],[0]])
            content = ribs
            endcheck = 0
            
            living.append(1)
            startpts.append([0,0,0])
            sequences.append([0])
    
    npolies = len(content)
    
    
    narm = []
    setforbool =[]
    content2 = [] 
    crack = []
    numb = 0
    
        
    # P R O C E S S I N G
    
    #CASE 1. NOTHING HAS BEEN MADE. WE HAVE ONE EXISTING RIB. IT IS BUDDING (IT THINKS IT STARTS AT [0,0,0])
    #NO CHECKS, NO INTERSECTIONS, THE B A S I C STUFF
    if npolies == 1:
        
        for i in range(noribs):
            
            
            rs.Command("_-Import C:\R3\OffCenter\Walk\Temp\protoslant_walk.igs ENTER")
            rs.Command("_SelAll")
            rs.Command("_Join")
            rs.Command("_SelNone")
            rs.Command("_SelAll")
            
            defject = rs.SelectedObjects(False,False)
            
            box2 = rs.AddPolyline([[-5.25,-5.25,0],[5.25,-5.25,0],[5.25,5.25,0],[-5.25,5.25,0],[-5.25,-5.25,0]])
            rs.MoveObject(box2, move_it)
            
            line1 = [1,0,0]
            line1 = rs.VectorRotate(line1,i*360/(noribs),zaxis)
            
            sequence = [1,line1,[0]]
            
            polypoints = JointAccess.Outline(sequence[1],sequence[1],sequence[2])
            
            verte = rs.AddPolyline(polypoints)
            
            intersection = rs.CurveCurveIntersection(verte,box2)
            
            if len(intersection) != 0:
                sequence[0] = 0
            
            
            rs.DeleteObject(verte)
            
            
            setforbool = []
            setforbool.append(defject)
            setforbool.append(JointAccess.Arm(sequence[1],sequence[1],sequence[2],fc))
            
            container = rs.BooleanUnion(setforbool)
            
            if not container is None:
                defject =  container[0]
            
            SaveNClean(defject,[polypoints],numb,[sequence])
            
            numb = numb + 1  
            
    #CASE 2 ONE RIB HAS STARTED GROWING AND ONE RIB IS BUDDING (THINKS THE ENDPOINT IS (0,0,0))
    #THE EXISTING RIB NEEDS TO CHECK FOR INTERECTIONS WITH ITSELF ALONE [MAYBE WITH THE BASE AS WELL????]
    #THE NEW RIB MUST MAKE SURE IT IS STARTING FROM A DIFFERENT POINT A N D THAT IT DOES NOT INTERSECT WITH EXISTING RIB
    elif npolies == 2 and rs.Distance(startpts[-1],[0,0,0]) <= tiny:
        
        #copying the list so that it won't get overwritten
        content2 = content[:]
        
        
        #ADDING TO THE EXISTING RIB
        #THE LOOP BELOW IS INFRASTRUCTURE FOR CASE 3. RIGHT NOW IT ONLY HAS ONE ITERATION
        for j in range(npolies-1):
            
            insequence = content[j]
            
            #do sth only if this particular rib is NOT DEAD
            if insequence[0] != 0:
                
                for i in range(noribs)[1:]:
                    #i is going through 1 to 15 for different endings
                    #in [s,e,q,u,e,n,c,e,0] we will get [s,e,q,u,e,n,c,e,i,0]
                    
                    rs.Command("_-Import C:\R3\OffCenter\Walk\Temp\protoslant_walk.igs ENTER")
                    rs.Command("_SelAll")
                    rs.Command("_Join")
                    rs.Command("_SelNone")
                    rs.Command("_SelAll")
                    
                    defject = rs.SelectedObjects(False,False)
                    
                    box2 = rs.AddPolyline([[-5.25,-5.25,0],[5.25,-5.25,0],[5.25,5.25,0],[-5.25,5.25,0],[-5.25,-5.25,0]])
                    rs.MoveObject(box2, move_it)
                    
                    joints = insequence[2][:-1]
                    joints.append(i)
                    joints.append(0)
                    
                    sequence = [1,insequence[1],joints]
                    
                    polypoints = JointAccess.Outline(sequence[1],sequence[1],sequence[2])
                    
                    verte = rs.AddPolyline(polypoints)
                    
                    #CHECKING FOR SELF INTERSECTION
                    #continue continues with the loop without reading the stuff below
                    int = rs.CurveCurveIntersection(verte,None,0.000001)
                    if len(int) != 0:
                        everything = rs.AllObjects()
                        rs.DeleteObjects(everything)
                        continue
                    
                    intersection = rs.CurveCurveIntersection(verte,box2)
                    #FRAME VS OUTLINE INTERSECTION CHECK
                    if len(intersection) != 0:
                        sequence[0] = 0
                    
                    rs.DeleteObject(verte)
                    
                    
                    setforbool = []
                    setforbool.append(defject)
                    setforbool.append(JointAccess.Arm(sequence[1],sequence[1],sequence[2],fc))
                    
                    container = rs.BooleanUnion(setforbool)
                    
                    if not container is None:
                        defject =  container[0]
                    else:
                        #print error message
                        message = str(datetime.datetime.now()) + "\n" + "BOOLEAN UNION FAIL"
                        History.WriteFile("C:\R3\OffCenter\Walk\ErrorMessage.dat",message)
                    
                    
                    polies = []
                    for i in range(len(content)-1):
                        if i != j:
                            chckpts = JointAccess.Outline(content2[i][1],content2[i][1],content2[i][2])
                            polies.append(chckpts)
                    polies.append(polypoints)
                    
                    SaveNClean(defject,polies,numb,[sequence,content[-1]])
                    
                    numb = numb + 1  
        
        #THE END 
        #MAKING OF THE NEW RIB
        
        other_ribs = []
        for j in range(len(content)-1):
            other_ribs.append(content[j])
        
        
        for i in range(noribs):
            
            rs.Command("_-Import C:\R3\OffCenter\Walk\Temp\protoslant_walk.igs ENTER")
            rs.Command("_SelAll")
            rs.Command("_Join")
            rs.Command("_SelNone")
            rs.Command("_SelAll")
            
            defject = rs.SelectedObjects(False,False)
            
            box2 = rs.AddPolyline([[-5.25,-5.25,0],[5.25,-5.25,0],[5.25,5.25,0],[-5.25,5.25,0],[-5.25,-5.25,0]])
            rs.MoveObject(box2, move_it)
            
            line1 = [1,0,0]
            line1 = rs.VectorRotate(line1,i*360/(noribs),zaxis)
            
            sequence = [1,line1,[0]]
            
            polypoints = JointAccess.Outline(sequence[1],sequence[1],sequence[2])
            
            verte = rs.AddPolyline(polypoints)
            
            
            #CHECKING FOR INTERSECTION with any of the already existent ribs
            #continue continues with the loop without reading the stuff below
            chck = False
            for i in range(len(content)-1):
                chckpts = JointAccess.Outline(content2[i][1],content2[i][1],content2[i][2])
                chckcrv = rs.AddPolyline(chckpts)
                int = rs.CurveCurveIntersection(verte,chckcrv,0.000001)
                if len(int) != 0:
                    chck = True
            
            if chck:
                everything = rs.AllObjects()
                rs.DeleteObjects(everything)
                continue
            
            
            intersection = rs.CurveCurveIntersection(verte,box2)
            
            if len(intersection)!=0:
                sequence[0] = 0
            
            rs.DeleteObject(verte)
            
            
            setforbool = []
            setforbool.append(defject)
            setforbool.append(JointAccess.Arm(sequence[1],sequence[1],sequence[2],fc))
            for i in range(len(content)-1):
                setforbool.append(JointAccess.Arm(content2[i][1],content2[i][1],content2[i][2],fc))
                
            container = rs.BooleanUnion(setforbool)
            
            if not container is None:
                defject =  container[0]
            else:
                #print error message
                message = str(datetime.datetime.now()) + "\n" + "BOOLEAN UNION FAIL"
                History.WriteFile("C:\R3\OffCenter\Walk\ErrorMessage.dat",message)
            
            
            polies = []
            for i in range(len(content)-1):
                chckpts = JointAccess.Outline(content2[i][1],content2[i][1],content2[i][2])
                polies.append(chckpts)
            
            polies.append(polypoints)
            
            content2[-1]=sequence
            SaveNClean(defject,polies,numb,content2)
            
            numb = numb + 1  
            
            
    #CASE 3 with more than one alive node and a budding one
    #scrolling through an arbitrary number of 
    elif npolies > 2 and rs.Distance(startpts[-1],[0,0,0]) <= tiny:
        
        #print "case npolies>2 and one budding not coded yet"
        
        
        #ADDING TO THE EXISTING RIBS
        #THE LOOP BELOW HAS TWO OR MORE ITERATIONS
        for j in range(npolies-1):
            
            insequence = content[j]
            
            #do sth only if this particular rib is NOT DEAD
            if insequence[0] != 0:
                
                for i in range(noribs)[1:]:
                    #i is going through 1 to 15 for different endings
                    #in [s,e,q,u,e,n,c,e,0] we will get [s,e,q,u,e,n,c,e,i,0]
                    
                    rs.Command("_-Import C:\R3\OffCenter\Walk\Temp\protoslant_walk.igs ENTER")
                    rs.Command("_SelAll")
                    rs.Command("_Join")
                    rs.Command("_SelNone")
                    rs.Command("_SelAll")
                    
                    defject = rs.SelectedObjects(False,False)
                    
                    box2 = rs.AddPolyline([[-5.25,-5.25,0],[5.25,-5.25,0],[5.25,5.25,0],[-5.25,5.25,0],[-5.25,-5.25,0]])
                    rs.MoveObject(box2, move_it)
                    
                    joints = insequence[2][:-1]
                    joints.append(i)
                    joints.append(0)
                    
                    sequence = [1,insequence[1],joints]
                    
                    polypoints = JointAccess.Outline(sequence[1],sequence[1],sequence[2])
                    
                    verte = rs.AddPolyline(polypoints)
                    
                    #CHECKING FOR SELF INTERSECTION
                    #continue continues with the loop without reading the stuff below
                    int = rs.CurveCurveIntersection(verte,None,0.000001)
                    if len(int) != 0:
                        everything = rs.AllObjects()
                        rs.DeleteObjects(everything)
                        continue
                    
                    intersection = rs.CurveCurveIntersection(verte,box2)
                    #NEED A SELF INTERSECTIOn CHECK
                    if len(intersection) != 0:
                        sequence[0] = 0
                    
                    
                    #CHECKING FOR INTERSECTION with any of the already existent ribs
                    chck = False
                    for i in range(len(content)-1):
                        if i != j:
                            chckpts = JointAccess.Outline(content[i][1],content[i][1],content[i][2])
                            chckcrv = rs.AddPolyline(chckpts)
                            int = rs.CurveCurveIntersection(verte,chckcrv,0.000001)
                            if len(int) != 0:
                                chck = True
                    
                    if chck:
                        everything = rs.AllObjects()
                        rs.DeleteObjects(everything)
                        continue
                    
                    rs.DeleteObject(verte)
                    
                    setforbool = []
                    setforbool.append(defject)
                    
                    for i in range(len(content)-1):
                        if i != j:
                            setforbool.append(JointAccess.Arm(content[i][1],content[i][1],content[i][2],fc))
                        else:
                            setforbool.append(JointAccess.Arm(sequence[1],sequence[1],sequence[2],fc))
                    
                    container = rs.BooleanUnion(setforbool)
                    
                    if not container is None:
                        defject =  container[0]
                    else:
                        #print error message
                        message = str(datetime.datetime.now()) + "\n" + "BOOLEAN UNION FAIL"
                        History.WriteFile("C:\R3\OffCenter\Walk\ErrorMessage.dat",message)
                    
                    
                    polies = []
                    for i in range(len(content)):
                        if i != j:
                            chckpts = JointAccess.Outline(content[i][1],content[i][1],content[i][2])
                            polies.append(chckpts)
                    polies.append(polypoints)
                    
                    #copying the list so that it won't get overwritten
                    content2 = content[:]
                    content2[j] = sequence
                    
                    SaveNClean(defject,polies,numb,content2)
                    
                    numb = numb + 1  
        
        #THE END 
        #MAKING OF THE NEW RIB
        
        
        for i in range(noribs):
            
            rs.Command("_-Import C:\R3\OffCenter\Walk\Temp\protoslant_walk.igs ENTER")
            rs.Command("_SelAll")
            rs.Command("_Join")
            rs.Command("_SelNone")
            rs.Command("_SelAll")
            
            defject = rs.SelectedObjects(False,False)
            
            box2 = rs.AddPolyline([[-5.25,-5.25,0],[5.25,-5.25,0],[5.25,5.25,0],[-5.25,5.25,0],[-5.25,-5.25,0]])
            rs.MoveObject(box2, move_it)
            
            line1 = [1,0,0]
            line1 = rs.VectorRotate(line1,i*360/(noribs),zaxis)
            
            sequence = [1,line1,[0]]
            
            polypoints = JointAccess.Outline(sequence[1],sequence[1],sequence[2])
            
            verte = rs.AddPolyline(polypoints)
            
            
            #CHECKING FOR INTERSECTION with any of the already existent ribs
            #continue continues with the loop without reading the stuff below
            chck = False
            for i in range(len(content)-1):
                chckpts = JointAccess.Outline(content[i][1],content[i][1],content[i][2])
                chckcrv = rs.AddPolyline(chckpts)
                int = rs.CurveCurveIntersection(verte,chckcrv,0.000001)
                if len(int) != 0:
                    chck = True
            
            if chck:
                everything = rs.AllObjects()
                rs.DeleteObjects(everything)
                continue
            
            
            intersection = rs.CurveCurveIntersection(verte,box2)
            
            if len(intersection)!=0:
                sequence[0] = 0
            
            rs.DeleteObject(verte)
            
            
            setforbool = []
            setforbool.append(defject)
            setforbool.append(JointAccess.Arm(sequence[1],sequence[1],sequence[2],fc))
            
            for i in range(len(content)-1):
                setforbool.append(JointAccess.Arm(content[i][1],content[i][1],content[i][2],fc))
                
            container = rs.BooleanUnion(setforbool)
            
            if not container is None:
                defject =  container[0]
            else:
                #print error message
                message = str(datetime.datetime.now()) + "\n" + "BOOLEAN UNION FAIL"
                History.WriteFile("C:\R3\OffCenter\Walk\ErrorMessage.dat",message)
            
            
            polies = []
            for i in range(len(content)-1):
                chckpts = JointAccess.Outline(content[i][1],content[i][1],content[i][2])
                polies.append(chckpts)
            
            polies.append(polypoints)
            
            content2 = content[:]
            content2[-1] = sequence
            
            SaveNClean(defject,polies,numb,content2)
            
            numb = numb + 1  
        
    else:
        
        #print "case npolies>2 and one budding not coded yet"
        
        
        #ADDING TO THE EXISTING RIBS
        #THE LOOP BELOW HAS TWO OR MORE ITERATIONS
        for j in range(npolies):
            
            insequence = content[j]
            
            #do sth only if this particular rib is NOT DEAD
            if insequence[0] != 0:
                
                for i in range(noribs)[1:]:
                    #i is going through 1 to 15 for different endings
                    #in [s,e,q,u,e,n,c,e,0] we will get [s,e,q,u,e,n,c,e,i,0]
                    
                    rs.Command("_-Import C:\R3\OffCenter\Walk\Temp\protoslant_walk.igs ENTER")
                    rs.Command("_SelAll")
                    rs.Command("_Join")
                    rs.Command("_SelNone")
                    rs.Command("_SelAll")
                    
                    defject = rs.SelectedObjects(False,False)
                    
                    box2 = rs.AddPolyline([[-5.25,-5.25,0],[5.25,-5.25,0],[5.25,5.25,0],[-5.25,5.25,0],[-5.25,-5.25,0]])
                    rs.MoveObject(box2, move_it)
                    
                    joints = insequence[2][:-1]
                    joints.append(i)
                    joints.append(0)
                    
                    sequence = [1,insequence[1],joints]
                    
                    polypoints = JointAccess.Outline(sequence[1],sequence[1],sequence[2])
                    
                    verte = rs.AddPolyline(polypoints)
                    
                    #CHECKING FOR SELF INTERSECTION
                    #continue continues with the loop without reading the stuff below
                    int = rs.CurveCurveIntersection(verte,None,0.000001)
                    if len(int) != 0:
                        everything = rs.AllObjects()
                        rs.DeleteObjects(everything)
                        continue
                    
                    intersection = rs.CurveCurveIntersection(verte,box2)
                    #NEED A SELF INTERSECTIOn CHECK
                    if len(intersection) != 0:
                        sequence[0] = 0
                    
                    
                    #CHECKING FOR INTERSECTION with any of the already existent ribs
                    chck = False
                    for i in range(len(content)):
                        if i != j:
                            chckpts = JointAccess.Outline(content[i][1],content[i][1],content[i][2])
                            chckcrv = rs.AddPolyline(chckpts)
                            int = rs.CurveCurveIntersection(verte,chckcrv,0.000001)
                            if len(int) != 0:
                                chck = True
                    
                    if chck:
                        everything = rs.AllObjects()
                        rs.DeleteObjects(everything)
                        continue
                    
                    rs.DeleteObject(verte)
                    
                    setforbool = []
                    setforbool.append(defject)
                    
                    for i in range(len(content)):
                        if i != j:
                            setforbool.append(JointAccess.Arm(content[i][1],content[i][1],content[i][2],fc))
                        else:
                            setforbool.append(JointAccess.Arm(sequence[1],sequence[1],sequence[2],fc))
                    
                    container = rs.BooleanUnion(setforbool)
                    
                    if not container is None:
                        defject =  container[0]
                    else:
                        #print error message
                        message = str(datetime.datetime.now()) + "\n" + "BOOLEAN UNION FAIL"
                        History.WriteFile("C:\R3\OffCenter\Walk\ErrorMessage.dat",message)
                    
                    
                    polies = []
                    for i in range(len(content)):
                        if i != j:
                            chckpts = JointAccess.Outline(content[i][1],content[i][1],content[i][2])
                            polies.append(chckpts)
                             
                    polies.append(polypoints)
                    
                    #copying the list so that it won't get overwritten
                    content2 = content[:]
                    content2[j] = sequence
                    
                    SaveNClean(defject,polies,numb,content2)
                    
                    numb = numb + 1  
    
    ##
    ########################################################################
    #making a text file that will be read by python to decide how many iterations to run on testing
    ########################################################################
    History.WriteFile(tempfolder + "\\OutputNo.txt",str(numb))
    #History.WriteFile(tempfolder + "\\" + "ribcount", str(numb))
    ########################################################################
    ##
    
    
    #SET UP A CLEAN EXIT
    exportFile("C:\\R3\OffCenter\Walk\Temp\\rubbish.3dm",4,False,False)
    #rs.Exit(]


everyone = rs.AllObjects()
rs.DeleteObjects(everyone)

reload(History)
reload(JointAccess)

Generation()