# # Set workspace
# workplace = arcpy.GetParameterAsText(0)
#
# # User inputs; get parameter
# SiteBoundary = arcpy.GetParameterAsText(1)
# Soils = arcpy.GetParameterAsText(2)  # NRCS Soils in county(s) of interest
# SoilsAttributes = arcpy.GetParameterAsText(3)  # muaggatt text file
# Soilsfile = arcpy.GetParameterAsText(4)  # path to output csv file

# Set workspace
workplace = 'C:/CodingProjects/SoilMappingUnits/Soils.gdb/stplnft_NC'
# User inputs
SiteBoundary = r'C:/CodingProjects/SoilMappingUnits/Soils.gdb/stplnft_NC/SiteBoundary'
Soils = r'C:/GIS/NC/County/Wake/Soils/NRCS/wss_SSA_NC183_soildb_NC_2003_[2019-09-16]/NC183/spatial/soilmu_a_nc183.shp'
SoilsAttributes = r'C:/GIS/NC/County/Wake/Soils/NRCS/wss_SSA_NC183_soildb_NC_2003_[2019-09-16]/NC183/tabular/muaggatt.txt'
Soilsfile = r'C:/CodingProjects/SoilMappingUnits'
soil_output_filename = 'soilsOut.csv'
