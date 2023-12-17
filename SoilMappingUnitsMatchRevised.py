# SoilMappingUnitsMatch
# Chantel Williams
# 10/3/2020

# Objective: Automate selecting soils based on site boundary
# Match selected soil's musyms with soil description
# Adv:      Fill soils legend (txt box) with musym and soils descriptions
#           with correct soil legend title
# Workspace example: C:/CodingProjects/SoilMappingUnits/Soils.gdb/stplnft_NC C:/CodingProjects/SoilMappingUnits/Soils.gdb/stplnft_NC/SiteBoundary C:/GIS/NC/County/Wake/Soils/NRCS/wss_SSA_NC183_soildb_NC_2003_[2019-09-16]/NC183/spatial/soilmu_a_nc183.shp C:/GIS/NC/County/Wake/Soils/NRCS/wss_SSA_NC183_soildb_NC_2003_[2019-09-16]/NC183/tabular/muaggatt.txt C:/CodingProjects/SoilMappingUnits

# Import system modules
import arcpy
import os
import csv
import constants as cn


def print_arc(message):
    """Print message for Script Tool and standard output"""
    print message
    arcpy.AddMessage(message)


class SoilMappingUnitsDetails:
    def __init__(self,
                 work_place=cn.workplace,
                 site_boundary = cn.SiteBoundary,
                 soils=cn.Soils,
                 soil_attributes=cn.SoilsAttributes,
                 output_csv_file=cn.Soilsfile,
                 soil_output_filename=cn.soil_output_filename
                 ):

        self.work_place = work_place
        self.site_boundary = site_boundary
        self.soils = soils
        self.soil_attributes = soil_attributes
        self.output_csv_file = output_csv_file
        self.soil_output_filename = soil_output_filename

    def initialize_soil_mapping_unit_details(self):
        self.set_up_workspace()
        self.nrcs_tabular_converter()
        self.import_csv_to_geodatabase()
        self.extract_soils_in_site_boundary()
        self.match_soils_with_descriptions()

    def execute_soil_mapping_units_details(self):
        self.initialize_soil_mapping_unit_details()

    def set_up_workspace(self):
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = self.work_place

    def nrcs_tabular_converter(self):
        """Converts NRCS Soils muaggatt tabular data to a csv file; creates an output file containing soils found in the
            specified area of interest with soils descriptions in the attribute table."""

        # convert muaggatt.txt to csv file to perform join on SoilsInBoundary File
        dictionary_soil_in_boundary = {}  # create dictionary to reduce duplicates in musysm in output file
        with open(self.soil_attributes, "r") as input_file:  # read text file
            with open(os.path.join(self.output_csv_file, self.soil_output_filename), "w") as output:
                csv.writer(output, lineterminator='\n').writerow(['OID', 'MUSYM', 'DESCRIPTION'])
                # oid = 'ObjectID'
                object_id = 0
                for line in input_file:
                    # First column in musymbols.
                    musym = [str(i) for i in line.split('|')][0].replace('"', '')
                    soil_line = str(
                        str(object_id) + "," + musym + "," + [str(i) for i in line.split('|')][1].replace(',',
                                                                                                          '') + '\n')  # concatenate MUSYM and Description with "," so they are in  seperate columns. 'Description.replace() is used to keep description in same column.
                    if dictionary_soil_in_boundary.get(musym) is not None:
                        print str(musym) + "is already in Dictionary"
                    else:
                        output.writelines(soil_line)
                    object_id += 1

            output.close()
            print_arc('muaggatt.txt converted to csv.')
        input_file.close()

    def import_csv_to_geodatabase(self):
        # import csv to gdb
        arcpy.TableToTable_conversion(os.path.join(self.output_csv_file, self.soil_output_filename),
                                      str(self.work_place)[:-11], 'CountySoilsDescr')
        print_arc('muaggatt.tx has been converted to a .csv file')

    def extract_soils_in_site_boundary(self):
        """ select soils that intersect with site boundary and save to a new featureclass """
        # Make a layer and select soils which overlap site boundary with the Select By Location tool
        arcpy.MakeFeatureLayer_management(self.soils, 'Soils_lyr')
        arcpy.SelectLayerByLocation_management('Soils_lyr', 'intersect', self.site_boundary)

        # Export selected features from Soils layer to new feature class
        arcpy.CopyFeatures_management('Soils_lyr', os.path.join(self.work_place,
                                                                'SoilsInBoundary'))  # copyfeature to workplace (gdb)

    def match_soils_with_descriptions(self):
        # Define outputs
        SoilsWithAttributes = os.path.join(self.work_place,
                                           'SoilsWithAttributes')
        # Match soils with attribute description text file
        with arcpy.da.SearchCursor(os.path.join(str(self.work_place)[:-11], 'CountySoilsDescriptions'),
                                   'MUSYM') as SoilInfile:
            if self.soils.count(self.soils) == (os.path.join(str(self.work_place)[:-11], 'CountySoilsDescr').count(
                    os.path.join(str(self.work_place)[:-11], 'CountySoilsDescriptions'))):
                # Join musyms soils descriptions to Soils in boundary
                soil_descriptions = arcpy.JoinField_management(os.path.join(self.work_place,
                                                                            'SoilsInBoundary'), 'MUSYM',
                                                               os.path.join(str(self.work_place)[:-11],
                                                                            'CountySoilsDescriptions'), 'MUSYM')
                # Export joined layer to new feature class
                arcpy.FeatureClassToFeatureClass_conversion(soil_descriptions, self.work_place, 'SoilsWithAttributes')
                # create csv with no duplicates of soils and soil descriptions found in site boundary for soils legend
                soils_legend = os.path.join(self.output_csv_file, 'soils_legend.xls')  # excel table for soils legend
                # Exports SoilsWithAttributes to an Excel file
                arcpy.TableToExcel_conversion(os.path.join(self.work_place,
                                                           'SoilsInBoundary'), soils_legend)
                print_arc("Soil Descriptions with no duplicated has been created")


def main():
    SMD = SoilMappingUnitsDetails()
    SMD.execute_soil_mapping_units_details()


if __name__ == "__main__":
    main()
