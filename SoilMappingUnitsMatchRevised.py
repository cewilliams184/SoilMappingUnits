
#SoilMappingUnitsMatch
#Chantel Williams
#10/3/2020

#Objective: Automate selecting soils based on site boundary
#	    Match selected soil's musyms with soil description
# Adv:      Fill soils legend (txt box) with musym and soils descriptions
#           with correct soil legend title
#Workspace example: C:/CodingProjects/SoilMappingUnits/Soils.gdb/stplnft_NC C:/CodingProjects/SoilMappingUnits/Soils.gdb/stplnft_NC/SiteBoundary C:/GIS/NC/County/Wake/Soils/NRCS/wss_SSA_NC183_soildb_NC_2003_[2019-09-16]/NC183/spatial/soilmu_a_nc183.shp C:/GIS/NC/County/Wake/Soils/NRCS/wss_SSA_NC183_soildb_NC_2003_[2019-09-16]/NC183/tabular/muaggatt.txt C:/CodingProjects/SoilMappingUnits

#Import system modules
import sys, arcpy, os,csv
arcpy.env.overwriteOutput = True

#Set workspace
workplace = arcpy.env.workspace =arcpy.GetParameterAsText(0)

#User inputs
SiteBoundary =arcpy.GetParameterAsText(1)
Soils= arcpy.GetParameterAsText(2)#NRCS Soils in county(s) of interest
SoilsAttributes =  arcpy.GetParameterAsText(3) #muaggatt text file
Soilsfile= arcpy.GetParameterAsText(4) #path to output csv file



#Define Function printArc; which shows message in Interactive Window and IDE
def printArc(message):
    '''Print message for Script Tool and standard output'''
    print message
    arcpy.AddMessage(message)

#Define Function convert muaggatt.txt to csv file
def NRCSTabularConverter(Muaggatt, SoilsFileOut,Work_Place):
    '''Converts NRCS Soils muaggatt tabular data to a csv file; creates an output file containing soils found in the
        specified area of interest with soils descriptions in the attribute table.'''
    #Define outputs
    soilsOut= os.path.join(SoilsFileOut,'soilsOut.csv')
    #Text file with soils attributes downloaded from NRCS Soils site (muname.txt?)
    CountySoilsDescr = os.path.join(str(Work_Place)[:-11], 'CountySoilsDescr') # table to be created in gdb with soil in county of interest joined with the soil descriptions

    #convert muaggatt.txt to csv file to perform join on SoilsInBoundary File
    fields = ['OID','MUSYM', 'DESCRIPTION']
    DictSoilInBound = {} # create dictionary to reduce duplicates in musysm in output file
    with open(Muaggatt, "r") as infile:    #read text file
        with open(soilsOut,"w") as output: #write text to file soilsOut.csv
            writer = csv.writer(output, lineterminator = '\n')
            writer.writerow(fields) #writes header containing a list of fields
            OID= 'ObjectID'
            ObjectID = 0
            for line in infile:
                #String to list of strings
                lineList = line.split('|')
                #First column in musymbols. 
                MuColumn = [str(i) for i in lineList]
                MUSYM = MuColumn[0].replace('"','')
                Description = MuColumn[1].replace(',','')
                SoilLine = str(str(ObjectID) + "," + MUSYM +"," + Description + '\n') #concatenate MUSYM and Description with "," so they are in  seperate columns. 'Description.replace() is used to keep description in same column. 
                if DictSoilInBound.get(MUSYM) is not None:
                    print str(MUSYM) + "is not in Dictionary"
                else:
                    output.writelines(SoilLine)
                ObjectID = ObjectID + 1
            
        output.close()
        printArc('muaggatt.txt converted to csv.')
    infile.close()
    #import csv to gdb
    arcpy.TableToTable_conversion(soilsOut, str(workplace)[:-11],'CountySoilsDescr')
    printArc('CSV has been imported into workspace gdb')
    

#Make a layer and select soils which overlap site boundary with the Select By Location tool
arcpy.MakeFeatureLayer_management(Soils, 'Soils_lyr')
arcpy.SelectLayerByLocation_management('Soils_lyr','intersect',SiteBoundary)

#Export selected features from Soils layer to new feature class

SoilsInBoundary = os.path.join(workplace, 'SoilsInBoundary') #Determine the new output feature class path and name
arcpy.CopyFeatures_management('Soils_lyr', SoilsInBoundary) #copyfeature to workplace (gdb)


NRCSTabularConverter(SoilsAttributes,Soilsfile, workplace) # run table converter function

#Define outputs
SoilsWithAttributes = os.path.join(workplace,'SoilsWithAttributes') #outfile of soils in boundary with descriptions in attributes
SoilMuDescriptions = os.path.join(workplace, 'SoilMuDescriptions') #csv of soils in boundary with descriptions
#Text file with soils attributes downloaded from NRCS Soils site (muname.txt?)
CountySoilsDescr = os.path.join(str(workplace)[:-11], 'CountySoilsDescr') # table to be created in gdb with soil in county of interest joined with the soil descriptions       
#Match soils with attribute description text file

soilscount = Soils.count(Soils) # count number of soil files entered
soilsAttrCount = CountySoilsDescr.count(CountySoilsDescr) # count number of soil attribute files entered        
SoilsJoined=os.path.join(str(workplace)[:-11],'CountySoilsDescr')
with arcpy.da.SearchCursor(SoilsJoined,'MUSYM') as SoilInfile:
    if soilscount == soilsAttrCount:  # check if number of soil files entered match number of soils attribute text files entered
        #Join musyms soils descriptions to Soils in boundary
        SoilDescriptions = arcpy.JoinField_management(SoilsInBoundary, 'MUSYM',CountySoilsDescr,'MUSYM') 
        #Export joined layer to new feature class
        SoilsWithAttributes = arcpy.FeatureClassToFeatureClass_conversion(SoilDescriptions, workplace, 'SoilsWithAttributes')
        #export attribute table of joined layer to csv? file
        
        NRCSTabularConverter(SoilsWithAttributes, SoilMuDescriptions, str(workplace)[:-11])
        arcpy.TableToTable_conversion(SoilsWithAttributes, str(workplace)[:-11],'SoilMuDescriptions')
    printArc("Table with soils and soils descriptions within Project Boundary has been created")              

    #export boundary file and remove duplicates
    #use dictionary and keys (check if key in dic pg 342
   # DictSoilInBound = []
#SoilMuDescriptions = arcpy.TableToTable_conversion(SoilsWithAttributes, str(workplace)[:-11],'SoilMuDescriptions')

