import rhinoscriptsyntax as rs
import os
import System.Drawing.Color
import Rhino
import scriptcontext
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
file = "joints.txt"

#TAPER FACTOR
fc = 0.9


#CONSTANTS
noribs = 16


#Decimal display and decimal places
#NOT YET IMPLEMENTED
#rs.UnitDistanceDisplayMode (0] 
#rs.UnitDistanceDisplayPrecision (7]


def SaveNClean(defject,vertices,i,content):
    #save all there is to run from current iteration and clean up proper
    
    rs.Command("_SelNone")
    rs.Command("_SelPolysrf")
    
    index = i 
    if index<10:
        j = "0" + str(index)
    if index>= 10:
        j = index
    
    #Quite probably there is a purely scripted way of writing the export now
    #It would be through the Rhino and scriptcontext
    rs.Command("_-Export C:\R3\OffCenter\Walk\Temp\proto2o" + j + ".igs ENTER")
    rs.DeleteObject(defject)
    
    for vrtx in vertices:
        rs.AddPolyline(vrtx)    
    
    #Again
    rs.Command("-saveas C:\\R3\OffCenter\Walk\Temp\sth" + j + ".3dm")  
    
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
            
            if not intersection is None:
                sequence[0] = 0
            
            rs.DeleteObject(verte)
            
            
            setforbool = []
            setforbool.append(defject)
            setforbool.append(JointAccess.Arm(sequence[1],sequence[1],sequence[2],fc))
            
            container = rs.BooleanUnion(setforbool)
            
            if not container is None:
                defject =  container(0)
            
            SaveNClean(defject,polypoints,numb,content2)
            
            numb = numb + 1  
            
    #CASE 2 ONE RIB HAS STARTED GROWING AND ONE RIB IS BUDDING (THINKS THE ENDPOINT IS (0,0,0))
    #THE EXISTING RIB NEEDS TO CHECK FOR INTERECTIONS WITH ITSELF ALONE [MAYBE WITH THE BASE AS WELL????]
    #THE NEW RIB MUST MAKE SURE IT IS STARTING FROM A DIFFERENT POINT A N D THAT IT DOES NOT INTERSECT WITH EXISTING RIB
    elif npolies == 2 and rs.Distance(startpts[-1],[0,0,0]) <= tiny:
        
        #ADDING TO THE EXISTING RIB
        #THE LOOP BELOW IS INFRASTRUCTURE FOR CASE 3. RIGHT NOW IT ONLY HAS ONE ITERATION
        for i in range(npolies-1):
            
            insequence = content[i]
            
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
                    if not intersection is None:
                        sequence[0] = 0
                    
                    rs.DeleteObject(verte)
                    
                    
                    setforbool = []
                    setforbool.append(defject)
                    setforbool.append(JointAccess.Arm(sequence[1],sequence[1],sequence[2],fc))
                    
                    container = rs.BooleanUnion(setforbool)
                    
                    if not container is None:
                        defject =  container(0)
                    else:
                        
                        #print error message
                        message = str(datetime.datetime.now()) + "\n" + "BOOLEAN UNION FAIL"
                        History.WriteFile("C:\R3\OffCenter\Walk\ErrorMessage.dat",message)
                        
                    SaveNClean(defject,polypoints,numb,content2)
                    
                    numb = numb + 1  
        
        #MAKING OF THE NEW RIB
        
        other_ribs = []
        for i in range(len(content)-1):
            other_ribs.append(content[i])
        
        
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
                
            if not intersection is None:
                sequence[0] = 0
            
            rs.DeleteObject(verte)
            
            
            setforbool = []
            setforbool.append(defject)
            setforbool.append(JointAccess.Arm(sequence[1],sequence[1],sequence[2],fc))
            for i in range(len(content)-1):
                setforbool.append(JointAccess.Arm(content[i][1],content[i][1],content[i][2],fc))
                
            container = rs.BooleanUnion(setforbool)
            
            if not container is None:
                defject =  container(0)
            else:
                #print error message
                message = str(datetime.datetime.now()) + "\n" + "BOOLEAN UNION FAIL"
                History.WriteFile("C:\R3\OffCenter\Walk\ErrorMessage.dat",message)
        
            SaveNClean(defject,polypoints,numb,content2)
            
            numb = numb + 1  
            
            
    elif npolies > 2 and rs.Distance(startpts[-1],[0,0,0]) <= tiny:
        
        print "case npolies>2 and one budding not coded yet"
        
        
    else:
        
        print "case npolies>2 and none budding"
        
        #THE OUTERMOST POINT ROTATES THROUGH THE END POINTS - whatever that means:P
        
        """
        for k in range(len(content)):
            
            
            #OOOOOOO 
            #OOOOOOO
            #OOOOOOO
            #OOOOOOO
            #G O I N G   T H R O U G H   L I V I N G   R I B S
            #if RIB IS ALIVE THEN DO WHAT FOLLOWS OTHERWISE THERE IS NOTHING TO LOOK AT
            #WHAT if ALL DIES??? I WILL WORRY ABOUT IT LATER
            
            
                
                for i in range(len(noribs)):
                
                rs.Command("_-Import C:\R3\OffCenter\Walk\Temp\protoslant_walk.igs ENTER")
                rs.Command("_SelAll")
                rs.Command("_Join")
                rs.Command("_SelNone")
                rs.Command("_SelAll")
            
            defject = rs.SelectedObjects(False,False)
            
            box2 = rs.AddPolyline([[-5.25,-5.25,0],[5.25,-5.25,0],[5.25,5.25,0],[-5.25,5.25,0],[-5.25,-5.25,0]])
            rs.MoveObject(box2, move_it)
            
            pas = 1
            con2 = -1
            
            if rs.Distance(endpts[k],[0,0,0]) < tiny:
                
                #If we are working with a new rib then we need to set a new beginning.
                line1 = [1,0,0]
                line1 = rs.VectorRotate(line1,i*360/(noribs),zaxis)
                
                sequence = [1,line1,[0]]
                
                
                #TEST1 - CHECK for LEAVING OFF IN THE SAME DIRECTION
                pas = 1
                
                for pt in startpts:                        
                    if rs.Distance(pt,line1)<tiny:
                        pas = 0
                    
                    
                    
                #TEST2 - CHECK for OVERLAP WITH OTHER CURVES
                
                if pas = 1:
                    
                    for j = 0 To npolies
                        
                        #CAN#T DO INTERSECTION WITH CURVE THAT HASN#T GROWN YET - OUTLINE PRODUCTION
                        
                        if rs.Distance(content(0](j](1],[0,0,0]] > tiny And j<>k Then
                            
                            carrier = content(0](j]
                            con2 = con2 + 1
                            ReDim Preserve content2(con2]
                            content2(con2] = Outline(carrier(1],carrier(1],carrier(2]]
                            
                            ReDim Preserve vrt(con2]
                            vrt(con2] = rs.PolylineVertices(content2(j]]                        
                        elif rs.Distance(content(0](j](1],[0,0,0]] < tiny And j=k Then
                            
                            carrier = sequence
                            con2 = con2 + 1
                            ReDim Preserve content2(con2]
                            content2(con2] = Outline(carrier(1],carrier(1],carrier(2]]
                            
                            ReDim Preserve vrt(con2]
                            vrt(con2] = rs.PolylineVertices(content2(j]]
                            
                        
                        
                        
                    
                    verte = content2
                    
                    
                    #TEST3 - CHECK for OVERLAP WITH THE BORDER - OVERLAP = KILL
                    intersection = rs.CurveCurveIntersection(verte(k],box2]
                    
                    if intersection not is None:
                        sequence(0] = 0
                    
                    
                    
                    for j = 0 To npolies
                        
                        if j <> k Then
                         
                            intersection = rs.CurveCurveIntersection(verte(k],verte(j]]
                         
                            if Not isNull(intersection] Then
                                rs.DeleteObjects(verte]
                                pass = 0
                                Exit for                 
                        
                        rs.DeleteObjects(verte]
                    
                    
                    #STEP 4 - PRINT THE ARMS AND BOOLEAN THE HELL OUT OF THEM SAVE THEM ETC
                    if pass = 1 Then
                    
                    
                        for j = 0 To npolies
                        
                            if j <> k Then
                                content2(j] = content(0](j]
                            Else
                                content2(k] = sequence
                            End if
                        
                        Next
                    
                        ReDim setforbool(npolies+1]
                    
                        setforbool(0] = defject 
                    
                        for j = 0 To npolies
                            setforbool(j+1] = Arm(content2(j](1],content2(j](1],content2(j](2]]
                        Next
                    
                    
                        #BOOLEAN THINGS UP
                     
                        container = rs.BooleanUnion(setforbool]
            
                        if Not IsNull(container] Then
                            defject =  container(0]
                        End if
                    
    
                        SaveNClean(defject,vrt,numb,k,content2] 

                        numb = numb + 1  
                    
                    Else
                    
                        objects = rs.AllObjects(] 
                        rs.DeleteObjects(objects]
                    
                    End if
                    
                Else
                     
                    if i <> 0 Then
                        #STEP0 - MAKE A NEW RIB
                    
                        line1 = i
                        size2 = UBound(content(0](k](2]]
                     
                        ReDim crack(size2+1]
                    
                        for j = 0 To size2-1
                            crack(j] = content(0](k](2](j]
                        Next
                     
                        crack(size2] = line1
                        crack(size2+1] = 0
                    
                        sequence = [content(0](k](0],content(0](k](1],crack]                
                
                    
                        #TEST1 - CHECK for LEAVING OFF IN THE SAME DIRECTION
                        #DROPPED
                
                 
                        if pass = 1 Then
                    
                            for j = 0 To npolies
                        
                                #CAN#T DO INTERSECTION WITH CURVE THAT HASN#T GROWN YET - OUTLINE PRODUCTION
                                if rs.Distance(content(0](j](1],[0,0,0]] > tiny Then
                                    carrier = sequence
                                    con2 = con2 + 1
                                    ReDim Preserve content2(con2]
                                    content2(con2] = Outline(carrier(1],carrier(1],carrier(2]]
                                
                                    ReDim Preserve vrt(con2]
                                    vrt(con2] = rs.PolylineVertices(content2(j]]                        

                                End if
                          
                            Next
                     
                            verte = content2
                     
                        
                        
                            #TEST3 - CHECK for OVERLAP WITH THE BORDER - OVERLAP = KILL
                            intersection = rs.CurveCurveIntersection(verte(k],box2]
                    
                            if Not isNull(intersection] Then
                                sequence(0] = 0
                            End if
                            
                    
                            #TEST2 - CHECK for OVERLAP WITH OTHER CURVES 

                            for j = 0 To con2
                             
                                if j <> k Then
                             
                                    intersection = rs.CurveCurveIntersection(verte(k],verte(j]]
                             
                                    if Not isNull(intersection] Then
                                        pas = 0
                                        Exit for                 
                                    End if
                     
                                End if 
                        
                            Next  
                         
                            rs.DeleteObjects(verte]
                    
                        End if
                
                
                
                        #STEP 4 - PRINT THE ARMS AND BOOLEAN THE HELL OUT OF THEM SAVE THEM ETC
                        if pass = 1 Then
                    
                    
                            for j = 0 To con2 #[0,0,0] can only happen in the last poly
                                
                        
                                if j <> k Then
                                    content2(j] = content(0](j]
                                Else
                                    content2(k] = sequence
                                End if
                        
                            Next
                    
                            ReDim setforbool(con2+1]
                    
                            setforbool[0] = defject 
                    
                            for j = 0 To con2
                                setforbool[j+1] = Arm(content2[j][1],content2[j][1],content2[j][2])
                            container = rs.BooleanUnion(setforbool)
                            if container not is None:
                                defject =  container(0)
                            SaveNClean(defject,vrt,numb,k,content2)
                            numb = numb + 1  
                    
                    
                    else:
                        
                        objects = rs.AllObjects(] 
                        rs.DeleteObjects(objects]
                        """
    
    ##
    ########################################################################
    #making a text file that will be read by python to decide how many iterations to run on testing
    ########################################################################
    History.WriteFile(tempfolder, str(numb))
    ########################################################################
    ##
    
    #DONE
    
    
    
    History.WriteFile(tempfolder + "OutputNo.txt",str(numb))
    
    #SET UP A CLEAN EXIT
    rs.Command("-saveas C:\\R3\OffCenter\Walk\Temp\rubbish.3dm")
    #rs.Exit(]


everyone = rs.AllObjects()
rs.DeleteObjects(everyone)

reload(History)
reload(JointAccess)

Generation()