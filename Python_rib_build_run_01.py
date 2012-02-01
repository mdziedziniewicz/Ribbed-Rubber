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



def SaveNClean(defject,vertices,i,k,content):
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



def MainS():
    
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
    
    helper =[]
    
    
    #if we read nothing we should save 1 starting point - namely [0,0,0]
    if content is None:
        endpts = [[0,0,0]]
        npolies = 0
        #polylines is an array of polylines
        #polyline is an array of points
        #point is an array of numbers
        
        #life#starting_point#joints_used
        sequence = [1,[0,0,0],[0]]
        #content = [[sequence],0]
        content = [sequence]
        
    else:
        
        #checking if new rib has actualy been started
        #[0,0,0] will always be the lasrt one
        for i = 0 To content(1]
            if rs.Distance(content(0](i](1],[0,0,0]]<tiny Then
                endcheck = endcheck*0
            End if
        Next
        
        # in not and we have less than 4 legs start a new leg at [0,0,0]    
        if endcheck <> 0 And content(1]<3 Then
            
            ReDim helper(content(1]+1]
            for i = 0 To content(1]
                helper(i] = content(0](i]
            Next
            helper(content(1]+1] = [1,[0,0,0],[0]]
    
            content = [helper, UBound(helper]]
            
        
              
        ReDim endpts(content(1]]
    
        for i = 0 To content(1] 
            #taking the first point of the ith poly to build from
            endpts(i] = content(0](i](1]
        Next
    
        npolies = content(1]
    
    ########################################################################
    ##
    
    narm = []
    #ReDim narm(npolies]
    setforbool =[]
    content2 = [] 
    crack = []
    
    ##
    ########################################################################
    #need to rewrite the polylines everytime!!!
    
    numb = 0
    
    #THE OUTERMOST POINT ROTATES THROUGH THE END POINTS - whatever that means:P
    for k = 0 To npolies
        

        #OOOOOOO
        #OOOOOOO
        #OOOOOOO
        #OOOOOOO
        #if RIB IS ALIVE THEN DO WHAT FOLLOWS OTHERWISE THERE IS NOTHING TO LOOK AT
        #WHAT if ALL DIES??? I WILL WORRY ABOUT IT LATER
        
        if content(0](k](0] <> 0 Then
         
            
            
            for i = 0 To noribs-1
            
                #rs.Print("buahaha"]
                rs.Command("_-Import C:\R3\OffCenter\Walk\Temp\protoslant_walk.igs ENTER"]

                rs.Command("_SelAll"]
                rs.Command("_Join"]
                rs.Command("_SelNone"]
                rs.Command("_SelAll"]
                defject = rs.GetObject(,,True]

                
                box2 = rs.AddPolyline([[-5.25,-5.25,0],[5.25,-5.25,0],[5.25,5.25,0],[-5.25,5.25,0],[-5.25,-5.25,0]]]
                rs.MoveObject(box2, move_it]
    
                pass = 1
                con2 = -1

                if rs.Distance(endpts(k],[0,0,0]] < tiny Then
            
                    line1 = [1,0,0]
                    line1 = rs.VectorRotate(line1,i*360/(noribs],zaxis]
                
                    sequence = [1,line1,[0]]
                
                
                    #TEST1 - CHECK for LEAVING OFF IN THE SAME DIRECTION
                    for j = 0 To npolies
                      
                        if rs.Distance(sequence(1],content(0](j](1]] < tiny And j <> k Then
                        
                            pass = 0
                            Exit for                 
                    
                        End if
                        
                    Next  
                
                 
                    #TEST2 - CHECK for OVERLAP WITH OTHER CURVES
                     
                    if pass = 1 Then
                    
                        for j = 0 To npolies
                        
                            #CAN#T DO INTERSECTION WITH CURVE THAT HASN#T GROWN YET - OUTLINE PRODUCTION
                            
                            if rs.Distance(content(0](j](1],[0,0,0]] > tiny And j<>k Then
                                
                        
                                
                                    carrier = content(0](j]
                                    con2 = con2 + 1
                                    ReDim Preserve content2(con2]
                                    content2(con2] = Outline(carrier(1],carrier(1],carrier(2]]
                                
                                    ReDim Preserve vrt(con2]
                                    vrt(con2] = rs.PolylineVertices(content2(j]]                        
                            Elseif rs.Distance(content(0](j](1],[0,0,0]] < tiny And j=k Then
                                    
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
                    
                        
                        for j = 0 To npolies
                            
                            if j <> k Then
                             
                                intersection = rs.CurveCurveIntersection(verte(k],verte(j]]
                             
                                if Not isNull(intersection] Then
                                    rs.DeleteObjects(verte]
                                    pass = 0
                                    Exit for                 
                                End if
                    
                            End if 
                        
                        Next  
                        
                        rs.DeleteObjects(verte]
                    
                    End if
                

                    
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
                                        pass = 0
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
                    
                            setforbool(0] = defject 
                    
                            for j = 0 To con2
                                setforbool(j+1] = Arm(content2(j](1],content2(j](1],content2(j](2]]
                            Next
                    
                    
                            #BOOLEAN THINGS UP
                     
                            container = rs.BooleanUnion(setforbool]
            
                            if Not IsNull(container] Then
                                defject =  container(0]
                            End if
                    
    
                            SaveNClean(defject,vrt,numb,k,content2] 
 
                            numb = numb + 1  
                    
                        End if      
        
                    Else
                        
                        objects = rs.AllObjects(] 
                        rs.DeleteObjects(objects]
                        
                    End if
            
                End if 
        
            Next
            
        End if
        
    Next
    
    ##
    ########################################################################
    #making a text file that will be read by python to decide how many iterations to run on testing
    ########################################################################
    WriteOutputNo(tempfolder,numb]
    ########################################################################
    ##
    
    #DONE
    
     
    #SET UP A CLEAN EXIT
    rs.Command("-saveas C:\\R3\OffCenter\Walk\Temp\rubbish.3dm"]
    #rs.Exit(]



MainS()