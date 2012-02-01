import rhinoscriptsyntax as rs
import os
import Rhino
import scriptcontext



def Pt2Str(pt):
    
    return str(pt[0]) + "," + str(pt[1]) + "," + str(pt[2])



def __point_from_string(text):
    items = text.strip("()\n").split(",")
    x = float(items[0])
    y = float(items[1])
    z = float(items[2])
    return [x,y,z]


def WriteFile(strLocation,str):
    #WRITING A SIMPLE FILE WRAPPER 
    #TAKES AN ADDRESS AND A STRING
    #*
    #*
    #**********
    
    strName="ErrorFromrs.txt"
    
    strFile=strLocation + "\\" + strName
    
    file = open(strFile,"w")
    
    #**********
    #*
    #*
    
    file.WriteLine(str)
    
    file.close()




def WritePolies(address,polies):
    
    #FORMAT IS:
    #[arewealive?#POINT#[jointNO,jointNO,jointNO,jointNO,...]]
    
    strFile=address 
    
    file = open(strFile, "w")
    
    
    for i in range(len(polies)):
        
        string = ""
        
        poly = polies[i]
        
        string = string + str(poly[0]) + "#"
        
        string = string + Pt2Str(poly[1]) + "#"
        
        
        for j in range(len(poly[2])-1):
            
            string = string + str(poly[2][j]) + ","
            
        
        #add the last entry to the string
        string = string + str(poly[2][len(poly[2])-1]) + "\n"
        
        file.write(string)
    
    file.close() 



def ReadPolies(dir,file):
    
    
    #FORMAT IS:
    #[arewealive?#POINT#[jointNO,jointNO,jointNO,jointNO,...]]
    
    strFileName1 = dir + "\\" + file
    
    
    
    #CHECK THERE IS EXISTENT HISTORY. IF THERE ISN'T RETURN NULL    
    if not os.path.exists(strFileName1):
        return None
    
    
    
    file = open(strFileName1, "r")
    
    
    ribList = []
    
    
    lines = file.readlines()
    
    
    for line in lines:
        
        str1stChr = line[0]
        
        if str1stChr != "'":
            
            rib = []
            
            splitLine = line.split("#")
            
            rib.append(int(splitLine[0]))
            
            rib.append(__point_from_string(splitLine[1]))
            
            joints = splitLine[2].split(',')
            
            jointNos = []
            
            for joint in joints:
                
                jointNos.append(int(joint))
            
            rib.append(jointNos)
            
        ribList.append(rib)         
        
    return ribList
    
    file.close()