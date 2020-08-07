#Written by Scott D. Miller
#National Park Service, Arctic and Central Alaska Inventory and Monitoring programs
#2020-08-07

# Imports
import arcpy
import os
import csv


# Input parameters
GeoDB = arcpy.GetParameterAsText(0) # The input geodatabase (Workspace)

# set the workspace
arcpy.env.workspace = GeoDB

# Function to export a featureclass as a json file
def ExportJSON(FeatureClass):
    try:
        # This will be the output json file
        JsonFile = os.path.dirname(arcpy.env.workspace) + '\\' + FeatureClass + '.json'
        
        # If the json file exists already then delete it 
        if os.path.exists(JsonFile):
            arcpy.AddMessage("File exists: " + JsonFile + '. Deleted')
            os.remove(JsonFile)

        # Export the FeatureClass
        arcpy.AddMessage("Exporting " + JsonFile)
        arcpy.FeaturesToJSON_conversion(FeatureClass, JsonFile, "NOT_FORMATTED")
    except Exception as e:
        arcpy.AddMessage('Export failed for FeatureClass: ' + FeatureClass + ' ' + str(e))


# loop through all the feature classes in the geodatabase and export them to json files
try:
    FeatureClasses = arcpy.ListFeatureClasses()
    for FeatureClass in FeatureClasses:
        arcpy.AddMessage("Processing " + FeatureClass)
        ExportCSV(FeatureClass)
        ExportJSON(FeatureClass)
except Exception as e:
    arcpy.AddMessage('Error: ' + str(e))

