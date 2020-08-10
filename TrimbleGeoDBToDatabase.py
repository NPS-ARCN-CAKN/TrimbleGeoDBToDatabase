#Written by Scott D. Miller
#National Park Service, Arctic and Central Alaska Inventory and Monitoring programs
#2020-08-07

# Imports
import arcpy
import os
import csv


# Input parameters
# GeoDB = arcpy.GetParameterAsText(0) # The input geodatabase (Workspace)
GeoDB = "C:/Work/VitalSigns/ARCN-CAKN Shallow Lakes/Local/2020-07 Geodatabase/2020/YUCH_2020/YUCH_2020_Deployment.gdb"
print(GeoDB)

# set the workspace
arcpy.env.workspace = GeoDB

# loop through all the feature classes in the geodatabase and export them to json files
try:
    FeatureClasses = arcpy.ListFeatureClasses()
    for FeatureClass in FeatureClasses:
        #arcpy.AddMessage("Processing " + FeatureClass)
        print("  " + FeatureClass)
except Exception as e:
    arcpy.AddMessage('Error: ' + str(e))

