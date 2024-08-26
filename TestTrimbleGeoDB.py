# TestTrimbleGeoDB.py

# WRITTEN BY: Nick Bywater
# CREATED FOR: National Park Service; the CAKN and the ARCN
# CREATED ON: 2022-October
#
# PURPOSE:
# This module contains functions that help test the Trimble feature
# class data in various ways.

import TrimbleUtility

def FindDuplicateWaterSampleKeys():
    return FindDuplicatePrimaryKeys('Water_Sample_Joined')

def FindDuplicateSecchiKeys():
    return FindDuplicatePrimaryKeys('Secchi_Joined')

def FindDuplicateLoonKeys():
    return FindDuplicatePrimaryKeys('Loons_Joined')

def FindDuplicatePondDepthKeys():
    return FindDuplicatePrimaryKeys('Depth_Joined')

def FindDuplicatePrimaryKeys(FeatureClassName):
    """
    Find only duplicate records in data, and return a dictionary of the
    concatenation of the record's primary key and the duplicate
    count.
    """
    if FeatureClassName == 'Water_Sample_Joined':
        d = GetPrimaryKeys(FeatureClassName)
    elif FeatureClassName == 'Secchi_Joined':
        d = GetPrimaryKeys(FeatureClassName)
    elif FeatureClassName == 'Loons_Joined':
        d = GetPrimaryKeys(FeatureClassName)
    elif FeatureClassName == 'Depth_Joined':
        d = GetPrimaryKeys(FeatureClassName)

    return FilterDuplicates(d)

def GetPrimaryKeys(FeatureClassName):
    d = {}
    for Row in TrimbleUtility.GetFeatureClassRows(FeatureClassName):
        PySampleDateTime = Row['CreationDateTimeLocal']

        # A record without a creation datetime is not a valid record.
        # End this iteration and go to the next row.
        if PySampleDateTime is None:
            continue

        PondName = str(Row['LakeNum'])
        SampleDate = TrimbleUtility.GetDateTime(PySampleDateTime, 'd')


        if FeatureClassName == 'Water_Sample_Joined':
            SampleNumber = str(Row['Sample_Number__A__B__C_'])

            if SampleNumber.strip() == '':
                SampleNumber = 'A'

        if FeatureClassName == 'Depth_Joined':
            GPS_Time = TrimbleUtility.GetDateTime(PySampleDateTime, 't')

        if FeatureClassName == 'Water_Sample_Joined':
            RowKey = PondName + SampleDate + SampleNumber
        elif FeatureClassName == 'Depth_Joined':
            RowKey = PondName + SampleDate + GPS_Time
        else:
            RowKey = PondName + SampleDate

        RowKey = RowKey.upper()

        if RowKey in d:
            d[RowKey] += 1
        else:
            d[RowKey] = 1

    return d

def FilterDuplicates(Dictionary):
    d = Dictionary
    DTarget = {}

    for k in d:
        if d[k] > 1:
            DTarget[k] = d[k]

    return DTarget
