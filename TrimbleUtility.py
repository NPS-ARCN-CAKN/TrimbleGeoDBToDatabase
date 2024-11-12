# TrimbleUtility.py

# WRITTEN BY: Nick Bywater
# CREATED FOR: National Park Service; the CAKN and the ARCN
# CREATED ON: 2022-October
#
# PURPOSE:
# This module contains utility functions that help the main program.

import arcpy
import datetime

def GetDateTime(PyDateTime, DateTimeType):
    if DateTimeType == 'd':
        DateTime = PyDateTime.strftime('%Y-%m-%d')
    elif DateTimeType == 't':
        DateTime = PyDateTime.strftime('%H:%M:%S')
    elif DateTimeType == 'dt':
        DateTime = PyDateTime.strftime('%Y-%m-%d %H:%M:%S')

    return DateTime

def GetCurrentDatetimeStr():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%dT%H.%M.%S')

def GetFeatureClassRows(FeatureClassName):
    """
    The paramenter 'FeatureClassName' takes as its argument the name
    of the feature class.
    This function returns a list of dictionary records where each
    dictionary contains a set of field names and values of the given
    feature class.
    """
    FIELD_NAME = 0
    FIELD_VALUE = 1

    # Get the feature class field names
    Fields = arcpy.ListFields(FeatureClassName)
    FieldNames = [Field.name for Field in Fields]

    DList = []
    for Row in arcpy.da.SearchCursor(FeatureClassName, FieldNames):
        z = zip(FieldNames, Row)
        d = {}

        for t in z:
            d[t[FIELD_NAME]] = t[FIELD_VALUE]

        DList.append(d)

    return DList
