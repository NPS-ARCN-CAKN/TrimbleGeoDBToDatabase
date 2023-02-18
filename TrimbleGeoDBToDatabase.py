# Written by Scott D. Miller, improved by Nick Bywater
# National Park Service, Arctic and Central Alaska Inventory and Monitoring programs
# Shallow Lakes Monitoring Protocol
# https://www.nps.gov/im/cakn/shallowlakes.htm

# Purpose:
# Import field data into the lakes monitoring database. This python
# script translates the field data in the geodatabase generated by the
# Shallow Lakes monitoring Trimble field computer into a series of SQL
# insert scripts that can be executed against the lakes monitoring
# database.

# U.S. Government Public Domain License

# Import utilities
import getpass
import datetime
import os
import TrimbleUtility
import TestTrimbleGeoDB

import arcpy

# ArcTool input parameters
#GeoDB = arcpy.GetParameterAsText(0) # ArcTool parameter # 1: The input geodatabase (Workspace).

##### Command line usage ######
# When the variable 'GEO_DB' is set to the path of the geodatabase
# (see below), the expectation is that the user will execute this
# program by using the installed ArcGIS Python typically located at a
# file path that looks similar to (might be located somewhere else on
# your system):
# C:\Python27\ArcGIS10.8\python.exe

# For example, from the command line, you'd execute:
# >C:\Python27\ArcGIS10.8\python.exe TrimbleGeoDBToDatabase.py

# The output is written to the same directory as the referenced
# geodatabase in the 'GEO_DB' string.

# THIS PATH MUST BE REPLACED BY PATH TO REAL GEODATABASE!
GEO_DB = "c:/fake_directory/geodatabase_name.gdb"

# Set the workspace
arcpy.env.workspace = GEO_DB

# Get the name of the geodatabase from the full path of the source
# geodatabase.
SOURCE_FILE_NAME = os.path.basename(GEO_DB) # Extract just the filename from the path from above.

# Get the username
USER_NAME = getpass.getuser()

# Standard header information to put in each sql script.
HeaderInfo = "/*"
HeaderInfo = HeaderInfo + "NPS Arctic and Central Alaska Inventory and Monitoring Program, Shallow Lakes Monitoring\n"
HeaderInfo = HeaderInfo + "This script was generated by the TrimbleGeoDBToDatabase ArcTool available at https://github.com/NPS-ARCN-CAKN/TrimbleGeoDBToDatabase. */\n\n"

def ExportSecchiJoined():
    """
    Translates the data in the Secchi_Joined featureclass into a
    script of SQL insert queries that can be executed on the
    AK_ShallowLakes database.

    NOTE: secchi depth is stored in the tblEvents table so this script
    the event must exist before the Secchi columns are updated. There
    is no Secchi depth table in the database.
    """
    try:
        FEATURE_CLASS = "Secchi_Joined"

        TARGET_FILE_NAME = SOURCE_FILE_NAME + '_' + FEATURE_CLASS + '_Insert.sql'

        SqlFilePath = os.path.dirname(arcpy.env.workspace) + '/' + TARGET_FILE_NAME

        # if the SQL file exists already then delete it
        if os.path.exists(SqlFilePath):
            arcpy.AddMessage("File exists: " + SqlFilePath)
            os.remove(SqlFilePath)
            arcpy.AddMessage("Deleted file: " + TARGET_FILE_NAME)
        SqlFile = open(SqlFilePath,'a')

        # We need to ensure all the lakes exist before we can create
        # sampling events, this variable will hold that checking code.
        LakeExistQueriesComments = "-- All the lakes in the input geodatabase must exist in tblPonds before events can be created or updated\n"
        LakeExistQueries = []

        # Write a query to allow the user to preview the secchi data
        # that may be overwritten
        PreviewQuery = "SELECT PONDNAME, SAMPLEDATE, SECCHIDEPTH, SECCHIONBOTTOM, SECCHINOTES FROM tblEvents WHERE \n"

        # Insert queries
        InsertQueries = []

        for Row in TrimbleUtility.GetFeatureClassRows(arcpy, FEATURE_CLASS):
            PySampleDateTime = Row['CreationDateTimeLocal']

            # A record without a creation datetime is not a valid
            # record. End this iteration and go to the next row.
            if PySampleDateTime is None:
                continue

            PondName = str(Row['LakeNum'])
            SampleDate = TrimbleUtility.GetDateTime(PySampleDateTime, 'd')

            if Row['Secchi_Depth_in_meters'] is not None:
                SecchiDepth = str(round(Row['Secchi_Depth_in_meters'], 1))
            else:
                SecchiDepth = 'NULL'

            if Row['Is_the_Secchi_on_the_lake_bottom_'] == "Yes":
                SecchiOnBottom = '1'
            else:
                SecchiOnBottom = '0'

            SecchiNotes = Row['Comments'].strip()

            # Validate that the lake exists
            LakeExists = "EXISTS (SELECT PondName FROM tblPonds WHERE Pondname = '" + PondName + "') And \n"

            if len(LakeExistQueries) > 0:
                LakeExistQueries.append("    " + LakeExists)
            else:
                LakeExistQueries.append("IF " + LakeExists)

            # Write the insert query to file
            # NOTE: Secchi data is stored in tblEvents so the SQL
            # ensures the event exists.
            SelectQuery = "SELECT  PONDNAME, SAMPLEDATE, SECCHIDEPTH, SECCHIONBOTTOM, SECCHINOTES FROM tblEvents WHERE Pondname = '" + PondName + "' And SampleDate = '" + SampleDate + "'"
            InsertQueries.append("       -- Ensure the Event for these data edits exists.\n")
            InsertQueries.append("       IF EXISTS (" + SelectQuery + ")\n")
            InsertQueries.append("               -- The event exists, update it.\n")
            InsertQueries.append("               UPDATE tblEvents SET SECCHIDEPTH = " + SecchiDepth + ", SECCHIONBOTTOM = " + SecchiOnBottom + ", ")

            CommentStr = ("SECCHINOTES = NULL"  if SecchiNotes == '' else "SECCHINOTES = '" + SecchiNotes + "'")
            InsertQueries.append(CommentStr +
                                 " WHERE Pondname = '" + PondName + "' And SampleDate = '" + SampleDate + "'\n\n")

            InsertQueries.append("               -- The event does not exist. If you want to insert it then uncomment the INSERT query below and execute.\n")

            CommentStr = (",NULL);\n\n" if SecchiNotes == '' else ",'" + SecchiNotes + "');\n\n")
            InsertQueries.append("               -- INSERT INTO tblEvents(PONDNAME,SAMPLEDATE,SECCHIDEPTH,SECCHIONBOTTOM,SECCHINOTES) VALUES('" +
                                 PondName + "','" + SampleDate + "'," + SecchiDepth + "," + SecchiOnBottom +
                                 CommentStr)

            InsertQueries.append("               -- Utility SELECT query in case you want to manually see the event. Uncomment and execute.\n")
            InsertQueries.append("               -- " + SelectQuery + "\n\n")
            InsertQueries.append("       ELSE\n")
            InsertQueries.append("           PRINT 'The event for this record does not exist. PondName:" + PondName + " SampleDate: " + SampleDate + "'\n\n")

            PreviewQuery = PreviewQuery + "-- (Pondname = '" + PondName + "' And SampleDate = '" + SampleDate + "') Or \n"

        # Write the header info to file
        SqlFile.write(HeaderInfo)
        SqlFile.write("/*\n")
        SqlFile.write("Purpose: Transfer secchi depth data from the field Trimble data collection application to the AK_ShallowLakes monitoring SQL Server database.\n")
        SqlFile.write("Source geodatabase: " + GEO_DB  + "\n")
        SqlFile.write("FeatureClass: " + FEATURE_CLASS  + "\n")
        SqlFile.write("SQL file name : " + SqlFile.name + "\n")
        SqlFile.write("Script generated by: " + USER_NAME + ".\n")
        SqlFile.write("Datetime: " + str(datetime.datetime.now())  + ".\n")
        SqlFile.write("*/\n\n")

        SqlFile.write("/*\nREAD AND THOROUGHLY UNDERSTAND THIS SCRIPT BEFORE RUNNING.\nRunning this script may change records in the Shallow Lakes monitoring database.\nThe lakes referenced in this script must exist in the tblPonds table prior to running this script. \nSecchi depth data is stored in tblEvents. \nOn error, rollback and correct any problems, then run again. Commit changes when finished.\n*/\n\n")
        SqlFile.write("USE AK_ShallowLakes\n\n")

        SqlFile.write("-- PREVIEW OF AFFECTED RECORDS: To see the secchi depth values that may be affected uncomment and run the query below:\n")
        SqlFile.write("-- " + PreviewQuery[:len(PreviewQuery) - 4] + "\n\n")

        SqlFile.write("BEGIN TRANSACTION -- COMMIT ROLLBACK -- All queries in this transaction must succeed or fail together. COMMIT if all queries succeed. ROLLBACK if any fail. Failure to COMMIT or ROLLBACK will leave the database in a hanging state.\n\n")


        LakeExistWrite = LakeExistQueriesComments + ''.join(LakeExistQueries)
        SqlFile.write(LakeExistWrite[:len(LakeExistWrite) - 6] + "\nBEGIN\n") # Trim the trailing ' And'

        SqlFile.write(''.join(InsertQueries))
        SqlFile.write("END\n")
        SqlFile.write("ELSE\n")
        SqlFile.write("    PRINT 'ERROR: One or more lakes are missing from tblPonds. All lakes in the insert query block must exist in tblPonds before sampling events can be created in the tblEvents table.'\n")

        # Let user know we're done
        FinishedMessage = FEATURE_CLASS + " data written to: " + SqlFile.name + '\n'
        arcpy.AddMessage(FinishedMessage)

    except Exception as e:
        Error = 'Error: ' + FEATURE_CLASS + ' ' + str(e)
        arcpy.AddMessage(Error)
        print(Error)

def ExportDepthJoined():
    """
    Translates the data in the Depth_Joined featureclass into a script
    of SQL insert queries that can be executed on the AK_ShallowLakes
    database.
    """
    try:
        FEATURE_CLASS = "Depth_Joined"

        TARGET_FILE_NAME = SOURCE_FILE_NAME + '_' + FEATURE_CLASS + '_Insert.sql'

        SqlFilePath = os.path.dirname(arcpy.env.workspace) + '/' + TARGET_FILE_NAME

        # if the SQL file exists already then delete it
        if os.path.exists(SqlFilePath):
            arcpy.AddMessage("File exists: " + SqlFilePath)
            os.remove(SqlFilePath)
            arcpy.AddMessage("Deleted file: " + TARGET_FILE_NAME)
        SqlFile = open(SqlFilePath,'a')

        # Create the first half of the SQL insert query
        SqlPrefix = 'INSERT INTO tblPondDepths(PONDNAME,SAMPLEDATE,GPS_TIME,LATITUDE,LONGITUDE,DEPTH,COMMENTS_DEPTHS,DATAFILE,SOURCE) VALUES('

        # This will hold the insert queries as they are built
        InsertQueries = ""

        # We need a query to determine if all the Events needed in the
        # new data to be imported exist in tblEvents or not Build up a
        # query to determine this.
        EventExistsQuery = "-- Determine if all the necessary parent Event records exist before trying to insert\nIF\n"

        # Build a query to select the just inserted records in order
        # to validate them
        ValidateQuery = "SELECT PONDNAME,SAMPLEDATE,GPS_TIME,LATITUDE,LONGITUDE,DEPTH,COMMENTS_DEPTHS,DATAFILE,SOURCE FROM tblPondDepths WHERE\n"

        # Write the header info to file
        SqlFile.write(HeaderInfo)
        SqlFile.write("/*\n")
        SqlFile.write("Purpose: Transfer lake depth data from the field Trimble data collection application to the AK_ShallowLakes monitoring SQL Server database.\n")
        SqlFile.write("Source geodatabase: " + GEO_DB  + "\n")
        SqlFile.write("FeatureClass: " + FEATURE_CLASS  + "\n")
        SqlFile.write("SQL file name : " + SqlFile.name + "\n")
        SqlFile.write("Script generated by: " + USER_NAME + ".\n")
        SqlFile.write("Datetime: " + str(datetime.datetime.now())  + ".\n")
        SqlFile.write("*/\n\n")

        SqlFile.write("BEGIN TRANSACTION -- COMMIT ROLLBACK\n\n")

        for Row in TrimbleUtility.GetFeatureClassRows(arcpy, FEATURE_CLASS):
            PySampleDateTime = Row['CreationDateTimeLocal']

            # A record without a creation datetime is not a valid
            # record. End this iteration and go to the next row.
            if PySampleDateTime is None:
                continue

            PondName = str(Row['LakeNum'])
            SampleDate = TrimbleUtility.GetDateTime(PySampleDateTime, 'd')
            GPS_Time = TrimbleUtility.GetDateTime(PySampleDateTime, 't')
            Latitude = str(Row['YCurrentMapCS'])
            Longitude = str(Row['XCurrentMapCS'])
            Depth = str(Row['Depth_in_meters'])

            CommentsDepths = Row['Comment'].strip()

            DataFile = SOURCE_FILE_NAME
            Source = SOURCE_FILE_NAME

            # Validation query
            ValidateQuery = ValidateQuery + "   -- (PondName='" + PondName + "' and  SampleDate = '" + SampleDate + "') Or\n"

            # Ensure the parent Event exists
            EventExistsQuery = EventExistsQuery + " EXISTS  (SELECT PONDNAME FROM tblEvents WHERE Pondname='" + PondName + "' And SampleDate = '" + SampleDate + "') And \n "

            # Write the insert query to file
            CommentStr = (",NULL,'" if CommentsDepths == '' else ",'" + CommentsDepths + "','")
            InsertQueries = (InsertQueries + "      " + SqlPrefix  + "'" + PondName + "','" + SampleDate + "','" + GPS_Time + "'," + Latitude + "," + Longitude + "," + Depth +
                             CommentStr +
                             DataFile + "','" + Source  + "');\n")

        # Write out the query that will determine if the required
        # Events all exist
        EventExistsQuery = EventExistsQuery[:len(EventExistsQuery) - 6] + '\n' # Remove the trailing ' and '

        SqlFile.write(EventExistsQuery + "\n    BEGIN\n    -- Insert the records\n")
        SqlFile.write(InsertQueries)
        SqlFile.write("   END\n")
        SqlFile.write("ELSE\n   Print 'One or more parent Event records related to the record you are trying to insert does not exist.'\n\n")

        SqlFile.write("-- Execute the query below to validate the inserted records.\n-- " + ValidateQuery[:len(ValidateQuery) - 3])

        # Let user know we're done
        FinishedMessage = FEATURE_CLASS + " data written to: " + SqlFile.name + '\n'
        arcpy.AddMessage(FinishedMessage)

    except Exception as e:
        Error = 'Error: ' + FEATURE_CLASS + ' ' + str(e)
        arcpy.AddMessage(Error)
        print(Error)

def ExportLoonsJoined():
    """
    Translates the data in the Loons_Joined featureclass into a script
    of SQL insert queries that can be executed on the AK_ShallowLakes
    database.
    """
    try:
        FEATURE_CLASS = "Loons_Joined"
        TABLE_NAME = "tblLoons"

        TARGET_FILE_NAME = SOURCE_FILE_NAME + '_' + FEATURE_CLASS + '_Insert.sql'
        SqlFilePath = os.path.dirname(arcpy.env.workspace) + '/' + TARGET_FILE_NAME

        # if the SQL file exists already then delete it
        if os.path.exists(SqlFilePath):
            arcpy.AddMessage("File exists: " + SqlFilePath)
            os.remove(SqlFilePath)
            arcpy.AddMessage("Deleted file: " + TARGET_FILE_NAME)
        SqlFile = open(SqlFilePath,'a')

        # This will hold the insert queries as they are built
        InsertQueries = ""

        # We need a query to determine if all the Events needed in the
        # new data to be imported exist in tblEvents or not
        EventExistsQuery = "-- Determine if all the necessary parent Event records exist before trying to insert\n"
        EventExistsQuery = EventExistsQuery + "IF\n"

        # We need a query to determine if all the Events needed in the
        # new data to be imported exist in tblEvents or not
        RecordExistsQuery = "    -- Determine if records exist already so we can avoid duplication\n"
        RecordExistsQuery = "        IF "


        # Build a query to select the just inserted records in order
        # to validate them
        ValidateQuery = "SELECT * FROM " + TABLE_NAME + " WHERE\n"

        # Write the header info to file
        SqlFile.write(HeaderInfo)
        SqlFile.write("/*\n")
        SqlFile.write("Purpose: Transfer " + FEATURE_CLASS + " data from the field Trimble data collection application to the AK_ShallowLakes monitoring SQL Server database.\n")
        SqlFile.write("Source geodatabase: " + GEO_DB  + "\n")
        SqlFile.write("FeatureClass: " + FEATURE_CLASS  + "\n")
        SqlFile.write("SQL file name : " + SqlFile.name + "\n")
        SqlFile.write("Script generated by: " + USER_NAME + ".\n")
        SqlFile.write("Datetime: " + str(datetime.datetime.now())  + ".\n")
        SqlFile.write("*/\n\n")

        i = 0
        for Row in TrimbleUtility.GetFeatureClassRows(arcpy, FEATURE_CLASS):
            PySampleDateTime = Row['CreationDateTimeLocal']

            # A record without a creation datetime is not a valid
            # record. End this iteration and go to the next row.
            if PySampleDateTime is None:
                continue

            PondName = str(Row['LakeNum'])
            SampleDate = TrimbleUtility.GetDateTime(PySampleDateTime, 'd')
            Species = str(Row['Loon_Species'])
            NumAdults = str(Row['a___of_Adults'])
            NumYoung = str(Row['a___of_Young'])
            DetectionType = str(Row['Identification_Method'])
            Latitude = str(Row['YCurrentMapCS'])
            Longitude = str(Row['XCurrentMapCS'])
            Comments = Row['Loon_Comments'].strip()
            Source = SOURCE_FILE_NAME

            # Validation query
            ValidateQuery = ValidateQuery + "   -- (PondName='" + PondName + "' and SampleDate = '" + SampleDate + "') Or\n"

            # Ensure the parent Event exists
            EventExistsQuery = EventExistsQuery + "    EXISTS  (SELECT PONDNAME FROM tblEvents WHERE Pondname='" + PondName + "' And SampleDate = '" + SampleDate + "') And \n"

            # Ensure the record does not exist already
            RecordExistsQuery = RecordExistsQuery + " NOT EXISTS (SELECT * FROM tblLoons WHERE Pondname='" + PondName + "' And SampleDate = '" + SampleDate  + "') And \n"

            # Write the insert query to file
            CommentStr = (",NULL,'" if Comments == '' else ",'" + Comments + "','")
            InsertQueries = (InsertQueries + "                INSERT INTO " + TABLE_NAME + "(PONDNAME,SAMPLEDATE,SPECIES,NUM_ADULTS,NUM_YOUNG,DETECTION_TYPE,LATITUDE,LONGITUDE,COMMENTS,SOURCE) VALUES("  +
                             "'"  + PondName + "','" + SampleDate + "','" + Species + "'," + NumAdults + "," + NumYoung + ",'" + DetectionType + "'," + Latitude + "," + Longitude +
                             CommentStr + Source + "');\n")

            i = i + 1

        SqlFile.write("USE AK_ShallowLakes\n\n")
        SqlFile.write("-- Execute the query below to view/validate records that may be altered.\n-- " + ValidateQuery[:len(ValidateQuery) - 3] + "\n\n")

        # Write out the query that will determine if the required
        # Events all exist
        EventExistsQuery = EventExistsQuery[:len(EventExistsQuery) - 6] + '\n' # Remove the trailing ' and '

        # If the parent Events don't exist in tblEvents then exit the
        # procedure
        SqlFile.write(EventExistsQuery + "    BEGIN\n")
        SqlFile.write("        PRINT 'The required parent Event records exist in tblEvents.'\n")
        SqlFile.write("    " + RecordExistsQuery[:len(RecordExistsQuery) - 6] + "\n\n")
        SqlFile.write("            BEGIN\n")

        # If we get here then the Events exist and the records to be
        # inserted do not exist, insert them.
        SqlFile.write("           -- Danger zone below. ROLLBACK on error.\n")
        SqlFile.write("           -- Insert the records\n")
        SqlFile.write("                PRINT 'inserts'\n")
        SqlFile.write("                BEGIN TRANSACTION -- COMMIT ROLLBACK\n")
        SqlFile.write(InsertQueries)
        SqlFile.write("               PRINT '" + str(i) + " records inserted from " + FEATURE_CLASS + " into database table " + TABLE_NAME + ".'\n")
        SqlFile.write("               PRINT 'DO NOT FORGET TO COMMIT OR ROLLBACK OR THE DATABASE WILL BE LEFT IN A HANGING STATE!!!!'\n")
        SqlFile.write("            END\n")
        SqlFile.write("        ELSE\n")
        SqlFile.write("            PRINT 'One or more records exist already. Uncomment and use the validation query above to help determine which " + FEATURE_CLASS + "\\" + TABLE_NAME + " records exist already.'\n")
        SqlFile.write("    END\n")
        SqlFile.write("ELSE\n    PRINT 'One or more parent Event records (tblEvents) related to the record you are trying to insert does not exist.'\n\n")

        # Let user know we're done
        FinishedMessage = FEATURE_CLASS + " data written to: " + SqlFile.name + '\n'
        arcpy.AddMessage(FinishedMessage)

    except Exception as e:
        Error = 'Error: ' + FEATURE_CLASS + ' ' + str(e)
        arcpy.AddMessage(Error)
        print(Error)

def ExportWaterSampleJoined():
    """
    Translates the data in the Water_Sample_Joined featureclass into a
    script of SQL insert queries that can be executed on the
    AK_ShallowLakes database.
    """
    try:
        FEATURE_CLASS = "Water_Sample_Joined"
        TABLE_NAME = "tblWaterSamples"

        TARGET_FILE_NAME = SOURCE_FILE_NAME + '_' + FEATURE_CLASS + '_Insert.sql'
        SqlFilePath = os.path.dirname(arcpy.env.workspace) + '/' + TARGET_FILE_NAME

        # if the SQL file exists already then delete it
        if os.path.exists(SqlFilePath):
            arcpy.AddMessage("File exists: " + SqlFilePath)
            os.remove(SqlFilePath)
            arcpy.AddMessage("Deleted file: " + TARGET_FILE_NAME)
        SqlFile = open(SqlFilePath,'a')

        # Create the first half of the SQL insert query
        SqlPrefix = 'INSERT INTO ' + TABLE_NAME + '([PONDNAME],[SAMPLEDATE],[SAMPLENUMBER],[SAMPLETIME],[SAMPLEDEPTH],[DEPTH],[018_COLL],[SI_DOC_COLL],[IONS_COLL],[TN_TP_COLL],[CHLA_COLL],[NOTES]) VALUES('

        # This will hold the insert queries as they are built
        InsertWaterSamplesQueries = ""

        # We need a query to determine if all the Events needed in the
        # new data to be imported exist in tblEvents or not build up a
        # query to determine this.
        EventExistsQuery = "-- Determine if all the necessary parent Event records exist before trying to insert\nIF\n"

        # Build a query to select the just inserted records in order
        # to validate them
        ValidateQuery = "SELECT * FROM " + TABLE_NAME + " WHERE\n"

        # Write the header info to file
        SqlFile.write(HeaderInfo)
        SqlFile.write("/*\n")
        SqlFile.write("Purpose: Transfer " + FEATURE_CLASS + " data from the field Trimble data collection application to the AK_ShallowLakes monitoring SQL Server database.\n")
        SqlFile.write("Source geodatabase: " + GEO_DB  + "\n")
        SqlFile.write("Source FeatureClass: " + FEATURE_CLASS  + "\n")
        SqlFile.write("Destination table name: " + TABLE_NAME + "\n")
        SqlFile.write("SQL file name : " + SqlFile.name + "\n")
        SqlFile.write("Script generated by: " + USER_NAME + ".\n")
        SqlFile.write("Datetime: " + str(datetime.datetime.now())  + ".\n")
        SqlFile.write("*/\n\n")

        SqlFile.write("BEGIN TRANSACTION -- COMMIT ROLLBACK\n\n")

        for Row in TrimbleUtility.GetFeatureClassRows(arcpy, FEATURE_CLASS):
            PySampleDateTime = Row['CreationDateTimeLocal']

            # A record without a creation datetime is not a valid
            # record. End this iteration and go to the next row.
            if PySampleDateTime is None:
                continue

            PondName = str(Row['LakeNum'])
            SampleDate = TrimbleUtility.GetDateTime(PySampleDateTime, 'd')
            SampleNumber = str(Row['Sample_Number__A__B__C_']).upper()
            if SampleNumber.strip() == '':
                SampleNumber = 'A'

            SampleTime = TrimbleUtility.GetDateTime(PySampleDateTime, 't')

            if Row['Depth_in_meters'] is not None:
                Depth = str(Row['Depth_in_meters'])
            else:
                Depth = 'NULL'

            SampleDepth = str(0.5)

            Notes = Row['Comment'].strip()

            WaterBottlesCollected = Row['Water_Bottles_Collected_'].strip()
            if WaterBottlesCollected == 'No':
                O18_Coll = '0'
                SI_DOC_Coll = '0'
                IONS_Coll = '0'
                TN_TP_Coll = '0'
                CHLA_Coll = '0'
            elif WaterBottlesCollected == 'Yes':
                O18_Coll = '1'
                SI_DOC_Coll = '1'
                IONS_Coll = '1'
                TN_TP_Coll = '1'
                CHLA_Coll = '1'

            # Validation query
            ValidateQuery = ValidateQuery + "   -- (PondName='" + PondName + "' and  SampleDate = '" + SampleDate + "' and SampleNumber = '" + SampleNumber + "') Or\n"

            # Ensure the parent Event exists
            EventExistsQuery = EventExistsQuery + " EXISTS  (SELECT PONDNAME FROM tblEvents WHERE Pondname='" + PondName + "' And SampleDate = '" + SampleDate + "') And \n "

            # Write the insert query to file
            CommentStr = (",NULL" if Notes == '' else ",'" + Notes + "'")
            InsertWaterSamplesQueries = (InsertWaterSamplesQueries + "INSERT INTO tblWaterSamples([PONDNAME],[SAMPLEDATE],[SAMPLENUMBER],[SAMPLETIME],[SAMPLEDEPTH],[DEPTH],[O18_COLL],[SI_DOC_COLL],[IONS_COLL],[TN_TP_COLL],[CHLA_COLL],[Notes]) VALUES('"  +
                                         PondName + "','" + SampleDate + "','" + SampleNumber + "','" + SampleTime + "'," + SampleDepth + "," + Depth + "," +
                                         O18_Coll + "," + SI_DOC_Coll + "," + IONS_Coll + "," + TN_TP_Coll + "," + CHLA_Coll + CommentStr + ")\n")

        # Write out the query that will determine if the required
        # Events all exist
        EventExistsQuery = EventExistsQuery[:len(EventExistsQuery) - 6] + '\n' # Remove the trailing ' and '

        SqlFile.write(EventExistsQuery + "\n    BEGIN\n    -- Insert the records\n\n")
        SqlFile.write("-- Insert the water samples first\n")
        SqlFile.write(InsertWaterSamplesQueries)
        SqlFile.write("   END\n")
        SqlFile.write("ELSE\n   Print 'One or more parent Event records related to the record you are trying to insert does not exist.'\n\n")

        SqlFile.write("-- Execute the query below to validate the inserted records.\n-- " + ValidateQuery[:len(ValidateQuery) - 3])

        # Let user know we're done
        FinishedMessage = FEATURE_CLASS + " data written to: " + SqlFile.name + '\n'
        arcpy.AddMessage(FinishedMessage)

    except Exception as e:
        Error = 'Error: ' + FEATURE_CLASS + ' ' + str(e)
        arcpy.AddMessage(Error)
        print(Error)

def Main():
    print('\nLog date/time: ' + str(datetime.datetime.now())  + '.\n')

    ExportSecchiJoined()
    ExportDepthJoined()
    ExportLoonsJoined()
    ExportWaterSampleJoined()

    print('\nTEST for DUPLICATES:')
    d = TestTrimbleGeoDB.FindDuplicatePrimaryKeys(arcpy, 'Water_Sample_Joined')
    print('Water sample: ', d)
    d = TestTrimbleGeoDB.FindDuplicatePrimaryKeys(arcpy, 'Secchi_Joined')
    print('Secchi: ', d)
    d = TestTrimbleGeoDB.FindDuplicatePrimaryKeys(arcpy, 'Loons_Joined')
    print('Loon: ', d)
    d = TestTrimbleGeoDB.FindDuplicatePrimaryKeys(arcpy, 'Depth_Joined')
    print('Depth: ', d)

if __name__ == "__main__":
    Main()
