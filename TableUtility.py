# TableUtility.py

# WRITTEN BY: Nick Bywater
# CREATED FOR: National Park Service; the CAKN and the ARCN
# CREATED ON: 2024-November
# LICENSE: Public Domain
#
# PURPOSE:
# This module contains functions that:
# - Join the Trimble feature classes (processed from Trimble data
#   dictionary) to a monument's feature class.
#   - Creates new feature classes from these joins.
# - Modifies the feature class table joins for further processing.
#   This includes:
#   - Mapping the Pathfinder field names to the names as processed by
#     the older "Positions" software.
#   - Combining the date and time columns into a date/time column.
#   - Calculating the coordinates from the joined feature class
#     coordinate system (which should be NAD 83).

import arcpy
import os

from enum import Enum

class Feature(Enum):
    WATER_SAMPLE = 1
    DEPTH = 2
    SECCHI = 3
    LOON = 4
    DEPLOYMENT = 5
    RETRIEVAL = 6
    MONUMENT = 7

# The naming convention for some of these parameters matches those of
# the underlying API function. For example 'TargetFeatures' is named
# 'target_features' in the documentation for the
# 'arcpy.SpatialJoin_analysis' function. A better name might have been
# 'TargetLayer'.
def CreateTableJoin(FeatureType, TargetFeatures, JoinFeatures, KeepFieldsFunction, AlterFunction, OutputFeatureClass, OverwriteOutput):
    """
    This function:
    - Joins two tables (one-to-one, keep all columns, closest points).
    - Keeps a subset of columns from this join, based on the
      'FeatureType' argument.
      - The specific fields to keep are retrieved by the
        'KeepFieldsFunction'.
    - Renames a subset of the columns of the join to those indicated
      by the 'AlterFunction' argument.
    """

    arcpy.env.overwriteOutput = OverwriteOutput

    FieldMappings = arcpy.FieldMappings()

    # Add all fields from inputs.
    FieldMappings.addTable(TargetFeatures)
    FieldMappings.addTable(JoinFeatures)

    KeepFields = KeepFieldsFunction(FeatureType)

    # Remove the fields we don't want.
    RemoveFields(FieldMappings, KeepFields)

    # Run the Spatial Join tool.
    arcpy.SpatialJoin_analysis(TargetFeatures,
                               JoinFeatures,
                               OutputFeatureClass,
                               "JOIN_ONE_TO_ONE",
                               "KEEP_ALL",
                               FieldMappings,
                               "CLOSEST")

    # Rename fields to match the older 'Positions' names.
    AlterFunction(OutputFeatureClass, FeatureType)

def GetKeptFieldsFromPathfinder(FeatureType):

    if FeatureType == Feature.WATER_SAMPLE:
        KeepFields = ["Depth_m",              #Depth_in_meters
                      "WaterSamp",            #Water_Bottles_Collected_
                      "SampleNum",            #Sample_Number__A__B__C_
                      "SampCom",              #Comment

                      "Horiz_Prec",           #HorizEstAcc
                      "Vert_Prec",            #VertEstAcc
                      "Corr_Type",            #CorrStatus
                      "GNSS_Heigh",           #FeatureHeight
                      "Rcvr_Type",            #DeviceType
                      "Max_PDOP",             #PDOP
                      "Max_HDOP",             #HDOP
                      "LakeNum",
                      "Datafile",
                      "GPS_Date",             #CreationDateTimeLocal
                      "GPS_Time"]             #CreationDateTimeLocal

    elif FeatureType == Feature.DEPTH:
        KeepFields = ["Depth_m",              #Depth_in_meters
                      "DepthCom",             #Comment

                      "Horiz_Prec",           #HorizEstAcc
                      "Vert_Prec",            #VertEstAcc
                      "Corr_Type",            #CorrStatus
                      "GNSS_Heigh",           #FeatureHeight
                      "Rcvr_Type",            #DeviceType
                      "Max_PDOP",             #PDOP
                      "Max_HDOP",             #HDOP
                      "LakeNum",
                      "Datafile",
                      "GPS_Date",             #CreationDateTimeLocal
                      "GPS_Time"]             #CreationDateTimeLocal

    elif FeatureType == Feature.SECCHI:
        KeepFields = ["Depth_m",              #Lake_Depth_in_meters
                      "SecchiDept",           #Secchi_Depth_in_meters
                      "OnBottom",             #Is_the_Secchi_on_the_lake_bottom_
                      "SeccCom",              #Comment

                      "Horiz_Prec",           #HorizEstAcc
                      "Vert_Prec",            #VertEstAcc
                      "Corr_Type",            #CorrStatus
                      "GNSS_Heigh",           #FeatureHeight
                      "Rcvr_Type",            #DeviceType
                      "Max_PDOP",             #PDOP
                      "Max_HDOP",             #HDOP
                      "LakeNum",
                      "Datafile",
                      "GPS_Date",             #CreationDateTimeLocal
                      "GPS_Time"]             #CreationDateTimeLocal

    elif FeatureType == Feature.LOON:
        KeepFields = ["Species",              #Loon_Species
                      "NumAdults",            #a__of__Adults
                      "NumYoung",             #a__of__Young
                      "OnWater",              #On_Water_
                      "Identifica",           #Identification_Method
                      "Comments",             #Loon_Comments

                      "Horiz_Prec",           #HorizEstAcc
                      "Vert_Prec",            #VertEstAcc
                      "Corr_Type",            #CorrStatus
                      "GNSS_Heigh",           #FeatureHeight
                      "Rcvr_Type",            #DeviceType
                      "Max_PDOP",             #PDOP
                      "Max_HDOP",             #HDOP
                      "LakeNum",
                      "Datafile",
                      "GPS_Date",             #CreationDateTimeLocal
                      "GPS_Time"]             #CreationDateTimeLocal

    elif FeatureType == Feature.DEPLOYMENT:
        KeepFields = ["Depth_m",              #Lake_Depth_in_meters
                      "DeployType",           #Deployment_Type
                      "DepCom",               #Comments

                      "Horiz_Prec",           #HorizEstAcc
                      "Vert_Prec",            #VertEstAcc
                      "Corr_Type",            #CorrStatus
                      "GNSS_Heigh",           #FeatureHeight
                      "Rcvr_Type",            #DeviceType
                      "Max_PDOP",             #PDOP
                      "Max_HDOP",             #HDOP
                      "LakeNum",
                      "Datafile",
                      "GPS_Date",             #CreationDateTimeLocal
                      "GPS_Time"]             #CreationDateTimeLocal

    elif FeatureType == Feature.RETRIEVAL:
        KeepFields = ["Depth_m",              #Lake_Depth_in_meters
                      "DeployType",           #Deployment_Type
                      "RetCom",               #Comments

                      "Horiz_Prec",           #HorizEstAcc
                      "Vert_Prec",            #VertEstAcc
                      "Corr_Type",            #CorrStatus
                      "GNSS_Heigh",           #FeatureHeight
                      "Rcvr_Type",            #DeviceType
                      "Max_PDOP",             #PDOP
                      "Max_HDOP",             #HDOP
                      "LakeNum",
                      "Datafile",
                      "GPS_Date",             #CreationDateTimeLocal
                      "GPS_Time"]             #CreationDateTimeLocal

    elif FeatureType == Feature.MONUMENT:
        KeepFields = [
                      "Horiz_Prec",           #HorizEstAcc
                      "Vert_Prec",            #VertEstAcc
                      "Corr_Type",            #CorrStatus
                      "GNSS_Heigh",           #FeatureHeight
                      "Rcvr_Type",            #DeviceType
                      "Max_PDOP",             #PDOP
                      "Max_HDOP",             #HDOP
                      "LakeNum",
                      "Datafile",
                      "GPS_Date",             #CreationDateTimeLocal
                      "GPS_Time"]             #CreationDateTimeLocal

    return KeepFields

def RemoveFields(FieldMappings, KeepFields):
    for f in FieldMappings.fields:
        if f.name not in KeepFields:
            FieldMappings.removeFieldMap(FieldMappings.findFieldMapIndex(f.name))

def AlterFieldNamesFromPathFinder(FeatureClassName, FeatureType):
    """
    The program GIS Pathfinder Office creates a different set of
    column names than Positions software. This function renames the
    feature class column names to those in this existing code (which
    was written with the Positions column names).
    """

    if FeatureType == Feature.WATER_SAMPLE:
        Fields = arcpy.ListFields(FeatureClassName)

        for f in Fields:
            if f.name == "SampleNum":
                arcpy.AlterField_management(FeatureClassName, f.name, "Sample_Number__A__B__C_")
            elif f.name == "Depth_m":
                arcpy.AlterField_management(FeatureClassName, f.name, "Depth_in_meters")
            elif f.name == "SampCom":
                arcpy.AlterField_management(FeatureClassName, f.name, "Comment")
            elif f.name == "WaterSamp":
                arcpy.AlterField_management(FeatureClassName, f.name, "Water_Bottles_Collected_")

    elif FeatureType == Feature.DEPTH:
        Fields = arcpy.ListFields(FeatureClassName)

        for f in Fields:
            if f.name == "Depth_m":
                arcpy.AlterField_management(FeatureClassName, f.name, "Depth_in_meters")
            elif f.name == "DepthCom":
                arcpy.AlterField_management(FeatureClassName, f.name, "Comment")

    elif FeatureType == Feature.SECCHI:
        Fields = arcpy.ListFields(FeatureClassName)

        for f in Fields:
            if f.name == "Depth_m":
                arcpy.AlterField_management(FeatureClassName, f.name, "Lake_Depth_in_meters")
            elif f.name == "SecchiDept":
                arcpy.AlterField_management(FeatureClassName, f.name, "Secchi_Depth_in_meters")
            # elif f.name == "OnBottom":
            #     arcpy.AlterField_management(FeatureClassName, f.name, "Is_the_Secchi_on_the_lake_bottom_")
            elif f.name == "SeccCom":
                arcpy.AlterField_management(FeatureClassName, f.name, "Comments")

    elif FeatureType == Feature.LOON:
        Fields = arcpy.ListFields(FeatureClassName)

        for f in Fields:
            if f.name == "Species":
                arcpy.AlterField_management(FeatureClassName, f.name, "Loon_Species")
            elif f.name == "NumAdults":
                arcpy.AlterField_management(FeatureClassName, f.name, "a___of_Adults")
            elif f.name == "NumYoung":
                arcpy.AlterField_management(FeatureClassName, f.name, "a___of_Young")
            elif f.name == "OnWater":
                arcpy.AlterField_management(FeatureClassName, f.name, "On_Water_")
            elif f.name == "Identifica":
                arcpy.AlterField_management(FeatureClassName, f.name, "Identification_Method")
            elif f.name == "Comments":
                arcpy.AlterField_management(FeatureClassName, f.name, "Loon_Comments")

    elif FeatureType == Feature.DEPLOYMENT:
        Fields = arcpy.ListFields(FeatureClassName)

        for f in Fields:
            if f.name == "Depth_m":
                arcpy.AlterField_management(FeatureClassName, f.name, "Lake_Depth_in_meters")
            elif f.name == "DeployType":
                arcpy.AlterField_management(FeatureClassName, f.name, "Deployment_Type")
            elif f.name == "DepCom":
                arcpy.AlterField_management(FeatureClassName, f.name, "Comments")

    elif FeatureType == Feature.RETRIEVAL:
        Fields = arcpy.ListFields(FeatureClassName)

        for f in Fields:
            if f.name == "Depth_m":
                arcpy.AlterField_management(FeatureClassName, f.name, "Lake_Depth_in_meters")
            elif f.name == "DeployType":
                arcpy.AlterField_management(FeatureClassName, f.name, "Deployment_Type")
            elif f.name == "RetCom":
                arcpy.AlterField_management(FeatureClassName, f.name, "Comments")

def AddNewDateField(TargetFeatureClassName, FieldName):
    arcpy.management.AddField(TargetFeatureClassName, FieldName, "DATE")

def AddNewDoubleField(TargetFeatureClassName, FieldName):
    arcpy.management.AddField(TargetFeatureClassName, FieldName, "DOUBLE")

def CombineDateAndTime(TargetFeatureClassName, TargetFieldName, DateFieldName, TimeFieldName):
    """
    This function assumes that the date field is an ESRI 'Date' type,
    and that the time field is a 'Text' type as is found in the output
    of the Trimble Pathfinder software.
    """
    Expression = "!" + DateFieldName + "!.strftime('%Y-%m-%d') + ' ' + !" + TimeFieldName + "!"
    arcpy.management.CalculateField(TargetFeatureClassName, TargetFieldName, Expression)

def TransformTable(FeatureType, TargetFeatures, JoinFeatures, KeepFieldsFunction, AlterFunction, OutputFeatureClass, OverwriteOutput = True):
    """
    This function:
    - Creates a table join.
      - If 'OverwriteOutput = True' (default), then any previously
        created join table is overwritten in place.
    - Creates new date/time column, and concats the separate date and
      time columns.
    - Creates new columns 'XCurrentMapCS' and 'YCurrentMapCS' and
      calculates the point geometry (lat/long) for the underlying
      coordinate system.
    """

    if arcpy.Exists(TargetFeatures):
        CreateTableJoin(FeatureType, TargetFeatures, JoinFeatures, KeepFieldsFunction, AlterFunction, OutputFeatureClass, OverwriteOutput)

        AddNewDateField(OutputFeatureClass, "CreationDateTimeLocal")
        AddNewDoubleField(OutputFeatureClass, "XCurrentMapCS")
        AddNewDoubleField(OutputFeatureClass, "YCurrentMapCS")

        CombineDateAndTime(OutputFeatureClass, "CreationDateTimeLocal", "GPS_Date", "GPS_Time")
        CalculatePointGeometry(OutputFeatureClass, "XCurrentMapCS", "YCurrentMapCS")
    else:
        print("TargetFeatures argument does not exit.")

def CalculatePointGeometry(TargetFeatureClassName, XFieldName, YFieldName):
    """
    From the Python docs:
    - "The coordinate system of the input features is used by default."
    """
    arcpy.management.CalculateGeometryAttributes(TargetFeatureClassName,
                                                 [[XFieldName, "POINT_X"],
                                                  [YFieldName, "POINT_Y"]])
