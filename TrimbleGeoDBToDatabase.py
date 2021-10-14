# Written by Scott D. Miller
# National Park Service, Arctic Inventory and Monitoring programs
# Shallow Lakes Monitoring Protocol
# https://www.nps.gov/im/cakn/shallowlakes.htm
# Purpose: Import field data into the lakes monitoring database. This python script translates the field data in the geodatabase 
# generated by the Shallow Lakes monitoring Trimble field computer
# into a series of SQL insert scripts that can be executed against the lakes monitoring database.
# U.S. Government Public Domain License

# Import utilities
import getpass
import datetime  
import os
    
# ArcTool input parameters
GeoDB = arcpy.GetParameterAsText(0) # ArcTool parameter # 1: The input geodatabase (Workspace).


# Set the workspace
arcpy.env.workspace = GeoDB

# Get the name of the geodatabase from the full path of the source geodatabase
SourceFilename = os.path.basename(GeoDB) # Extract just the filename from the path from above.

# Get the username
username = getpass.getuser()

# Standard header information to put in each sql script
HeaderInfo = "/*"
HeaderInfo = HeaderInfo + "NPS Arctic and Central Alaska Inventory and Monitoring Program, Shallow Lakes Monitoring\n"
HeaderInfo = HeaderInfo + "This script was generated by the TrimbleGeoDBToDatabase ArcTool available at https://github.com/NPS-ARCN-CAKN/TrimbleGeoDBToDatabase. */\n\n"



# Translates the data in the Secchi_Joined featureclass into a script of SQL insert queries that can be executed on the AK_ShallowLakes database.
# NOTE: secchi depth is stored in the tblEvents table so this script tries to create a new event. There is no Secchi depth table in the database.
# Since events must be present to insert the other records this script must be run first.
# This may not be what you expect.
def Export_Secchi_Joined():
    try:
        FeatureClass = "Secchi_Joined"

        # This will be the output SQL file, same directory as the source geodatabase.
        SqlFile = os.path.dirname(arcpy.env.workspace) + '/' + SourceFilename + '_' + FeatureClass + '_Insert.sql'
        
        # if the SQL file exists already then delete it 
        if os.path.exists(SqlFile):
            arcpy.AddMessage("File exists: " + SqlFile + '. Deleted')
            os.remove(SqlFile)
        SqlFile = open(SqlFile,'a')  

        # Get the featureclass' field names
        Fields = arcpy.ListFields(FeatureClass)
        Field_names =  [Field.name for Field in Fields]

        # We need to ensure all the lakes exist before we can create sampling events, this variable will hold that checking code.
        LakeExistQueries = "-- All the lakes in the input geodatabase must exist in tblPonds before events can be created or updated\n "
        LakeExistQueries = LakeExistQueries + "IF "

        #Write a query to allow the user to preview the secchi data that may be overwritten
        PreviewQuery = "SELECT PONDNAME, SAMPLEDATE, SECCHIDEPTH, SECCHIONBOTTOM, SECCHINOTES FROM tblEvents WHERE "

        # Insert queries
        InsertQueries = ""

        # loop through the data rows and translate the data cells into an SQL insert query
        for row in arcpy.da.SearchCursor(FeatureClass,Field_names):
            i = 0

            # Get the field values into variables
            PondName = str(row[11])
            SampleDate = str(row[8])
            SECCHIDEPTH = str(row[5])
            if row[6] == "Yes":
                SECCHIONBOTTOM = '1' ''
            else: 
                SECCHIONBOTTOM = '0'
            SECCHINOTES = str(row[7])
            SampleDateShort = GetShortDate(SampleDate) # Events in tblEvents should only have a date, not a datetime, this strips the time part off the sample date
            
            # Validate that the lake exists
            LakeExistQueries = LakeExistQueries + "EXISTS\n (SELECT PondName FROM tblPonds WHERE Pondname = '" + PondName + "') And "

            # Write the insert query to file
            # NOTE: Secchi data is stored in tblEvents so the SQL ensures the event exists.
            SelectQuery = "SELECT  PONDNAME, SAMPLEDATE, SECCHIDEPTH, SECCHIONBOTTOM, SECCHINOTES FROM tblEvents WHERE Pondname = '" + PondName + "' And Convert(Datetime,SampleDate,102) = '" + SampleDateShort + "'"
            InsertQueries = InsertQueries + "       -- Ensure the Event for these data edits exists.\n"
            InsertQueries = InsertQueries + "       IF EXISTS (" + SelectQuery + ")\n"
            InsertQueries = InsertQueries + "               -- The event exists, update it.\n"
            InsertQueries = InsertQueries + "               UPDATE tblEvents SET SECCHIDEPTH = " + SECCHIDEPTH + ", SECCHIONBOTTOM = " + SECCHIONBOTTOM + ", SECCHINOTES = '" + SECCHINOTES + "' WHERE Pondname = '" + PondName + "' And SampleDate = '" + SampleDateShort + "'\n\n"
            InsertQueries = InsertQueries + "               -- The event does not exist. If you want to insert it then uncomment the INSERT query below and execute.\n"
            InsertQueries = InsertQueries + "               -- INSERT INTO tblEvents(PONDNAME,SAMPLEDATE,SECCHIDEPTH,SECCHIONBOTTOM,SECCHINOTES) VALUES('" + PondName + "','" + SampleDateShort + "'," + SECCHIDEPTH + "," + SECCHIONBOTTOM + ",'" + SECCHINOTES + "');\n\n"
            InsertQueries = InsertQueries + "               -- Utility SELECT query in case you want to manually see the event. Uncomment and execute.\n"
            InsertQueries = InsertQueries + "               -- " + SelectQuery + "\n\n"
            InsertQueries = InsertQueries + "       ELSE\n"
            InsertQueries = InsertQueries + "           PRINT 'The event for this record does not exist. PondName:" + PondName + " SampleDate: " + SampleDateShort + "'\n\n"
            
            PreviewQuery = PreviewQuery + " (Pondname = '" + PondName + "' And Convert(Datetime,SampleDate,102) = '" + SampleDateShort + "') Or "

        # Write the header info to file
        SqlFile.write(HeaderInfo)
        SqlFile.write("/*\n")
        SqlFile.write("Purpose: Transfer secchi depth data from the field Trimble data collection application to the AK_ShallowLakes monitoring SQL Server database.\n")
        SqlFile.write("Source geodatabase: " + GeoDB  + "\n") 
        SqlFile.write("FeatureClass: " + FeatureClass  + "\n") 
        SqlFile.write("SQL file name : " + SqlFile.name + "\n")
        SqlFile.write("Script generated by: " + username + ".\n")
        SqlFile.write("Datetime: " + str(datetime.datetime.now())  + ".\n")
        SqlFile.write("*/\n\n")

        SqlFile.write("/*\nREAD AND THOROUGHLY UNDERSTAND THIS SCRIPT BEFORE RUNNING.\nRunning this script may change records in the Shallow Lakes monitoring database.\nThe lakes referenced in this script must exist in the tblPonds table prior to running this script. \nSecchi depth data is stored in tblEvents. \nOn error, rollback and correct any problems, then run again. Commit changes when finished.\n*/\n\n")
        SqlFile.write("USE AK_ShallowLakes\n\n")
       
        SqlFile.write("-- PREVIEW OF AFFECTED RECORDS: To see the secchi depth values that may be affected uncomment and run the query below:\n")
        SqlFile.write("-- " + PreviewQuery[:len(PreviewQuery) - 4] + "\n\n")
       
        SqlFile.write("BEGIN TRANSACTION -- COMMIT ROLLBACK -- All queries in this transaction must succeed or fail together. COMMIT if all queries succeed. ROLLBACK if any fail. Failure to COMMIT or ROLLBACK will leave the database in a hanging state.\n\n")
        
        

        SqlFile.write(LakeExistQueries[:len(LakeExistQueries) - 4] + "\n    BEGIN\n") # Trim the trailing ' And'
        SqlFile.write(InsertQueries)
        SqlFile.write("    END\n")
        SqlFile.write("ELSE\n")
        SqlFile.write("    PRINT 'ERROR: One or more lakes are missing from tblPonds. All lakes in the insert query block must exist in tblPonds before sampling events can be created in the tblEvents table.'\n")

        # Let user know we're done
        FinishedMessage = FeatureClass + " data written to " + SqlFile.name.replace("/","\\"+ "\n")
        print(FinishedMessage)
        arcpy.AddMessage(FinishedMessage)

    # When something goes wrong, let user know
    except Exception as e:
        error = 'Error: ' + FeatureClass + ' ' + str(e)
        arcpy.AddMessage(error)
        print(error)


# Translates the data in the Depth_Joined featureclass into a script of SQL insert queries that can be executed on the AK_ShallowLakes database.
def Export_Depth_Joined():
    try:
        FeatureClass = "Depth_Joined"

        # This will be the output SQL file, same directory as the source geodatabase.
        SqlFile = os.path.dirname(arcpy.env.workspace) + '/' + SourceFilename + '_' + FeatureClass + '_Insert.sql'
        
        # if the SQL file exists already then delete it 
        if os.path.exists(SqlFile):
            arcpy.AddMessage("File exists: " + SqlFile + '. Deleted')
            os.remove(SqlFile)
        SqlFile = open(SqlFile,'a')  

        # Create the first half of the SQL insert query
        SqlPrefix = 'INSERT INTO tblPondDepths(PONDNAME,SAMPLEDATE,GPS_TIME,LATITUDE,LONGITUDE,DEPTH,COMMENTS_DEPTHS,DATAFILE,SOURCE) VALUES('

        # This will hold the insert queries as they are built
        InsertQueries = ""

        # We need a query to determine if all the Events needed in the new data to be imported exist in tblEvents or not
        # Build up a query to determine this.
        EventExistsQuery = "-- Determine if all the necessary parent Event records exist before trying to insert\nIF\n"

        # Build a query to select the just inserted records in order to validate them
        ValidateQuery = "SELECT PONDNAME,SAMPLEDATE,GPS_TIME,LATITUDE,LONGITUDE,DEPTH,COMMENTS_DEPTHS,DATAFILE,SOURCE FROM tblPondDepths WHERE\n"

        # Get the featureclass' field names
        Fields = arcpy.ListFields(FeatureClass)
        Field_names =  [Field.name for Field in Fields]

        # Write the header info to file
        SqlFile.write(HeaderInfo)
        SqlFile.write("/*\n")
        SqlFile.write("Purpose: Transfer lake depth data from the field Trimble data collection application to the AK_ShallowLakes monitoring SQL Server database.\n")
        SqlFile.write("Source geodatabase: " + GeoDB  + "\n") 
        SqlFile.write("FeatureClass: " + FeatureClass  + "\n") 
        SqlFile.write("SQL file name : " + SqlFile.name + "\n")
        SqlFile.write("Script generated by: " + username + ".\n")
        SqlFile.write("Datetime: " + str(datetime.datetime.now())  + ".\n")
        SqlFile.write("*/\n\n")

        SqlFile.write("BEGIN TRANSACTION -- COMMIT ROLLBACK\n\n")

        
        # loop through the data rows and translate the data cells into an SQL insert query
        for row in arcpy.da.SearchCursor(FeatureClass,Field_names):
            i = 0

            # Get the field values into variables
            PondName = str(row[10])
            SampleDate = str(row[7])
            GPS_Time = str(row[7])
            Latitude = str(row[9])
            Longitude = str(row[8])
            Depth = str(row[4])
            Comments_Depths = str(row[5])
            DataFile = SourceFilename
            Source = SourceFilename
            SampleDateShort = GetShortDate(SampleDate) # Events in tblEvents should only have a date, not a datetime, this strips the time part off the sample date

            # Validation query
            ValidateQuery = ValidateQuery + "   -- (PondName='" + PondName + "' and  SampleDate = Convert(Date,'" + SampleDate + "')) Or\n"

            # Ensure the parent Event exists
            EventExistsQuery = EventExistsQuery + " EXISTS  (SELECT PONDNAME FROM tblEvents WHERE Pondname='" + PondName + "' And SampleDate = Convert(Date,'" + SampleDate + "')) And \n "

            # Write the insert query to file
            InsertQueries = InsertQueries + "      " + SqlPrefix  + "'" + PondName + "','" + SampleDateShort + "','" + GPS_Time + "'," + Latitude + "," + Longitude + "," + Depth + ",'" + Comments_Depths + "','" + DataFile + "','" + Source  + "');\n"

        # Write out the query that will determine if the required Events all exist
        EventExistsQuery = EventExistsQuery[:len(EventExistsQuery) - 6] + '\n' # Remove the trailing ' and '
        
        SqlFile.write(EventExistsQuery + "\n    BEGIN\n    -- Insert the records\n")
        SqlFile.write(InsertQueries)
        SqlFile.write("   END\n")
        SqlFile.write("ELSE\n   Print 'One or more parent Event records related to the record you are trying to insert does not exist.'\n\n")

        SqlFile.write("-- Execute the query below to validate the inserted records.\n-- " + ValidateQuery[:len(ValidateQuery) - 3])

        # Let user know we're done
        FinishedMessage = FeatureClass + " data written to " + SqlFile.name.replace("/","\\" + "\n")
        print(FinishedMessage)
        arcpy.AddMessage(FinishedMessage)

    # When something goes wrong, let user know
    except expression as identifier:
        error = 'Error: ' + FeatureClass + ' ' + str(e)
        arcpy.AddMessage(error)
        print(error)



# Translates the data in the Depth_Joined featureclass into a script of SQL insert queries that can be executed on the AK_ShallowLakes database.
def Export_Loons_Joined():
    try:
        FeatureClass = "Loons_Joined" # Geodatabase feature class name
        TableName = "tblLoons" # Database table name

        # This will be the output SQL file, same directory as the source geodatabase.
        SqlFile = os.path.dirname(arcpy.env.workspace) + '/' + SourceFilename + '_' + FeatureClass + '_Insert.sql'
        
        # if the SQL file exists already then delete it 
        if os.path.exists(SqlFile):
            arcpy.AddMessage("File exists: " + SqlFile + '. Deleted')
            os.remove(SqlFile)
        SqlFile = open(SqlFile,'a')  

        # This will hold the insert queries as they are built
        InsertQueries = ""

        # We need a query to determine if all the Events needed in the new data to be imported exist in tblEvents or not
        EventExistsQuery = "-- Determine if all the necessary parent Event records exist before trying to insert\n"

        # We need a query to determine if all the Events needed in the new data to be imported exist in tblEvents or not
        RecordExistsQuery = "    -- Determine if records exist already so we can avoid duplication\n"

        # Build a query to select the just inserted records in order to validate them
        ValidateQuery = "SELECT * FROM " + TableName + " WHERE\n"

        # Get the featureclass' field names
        Fields = arcpy.ListFields(FeatureClass)
        Field_names =  [Field.name for Field in Fields]

        # Write the header info to file
        SqlFile.write(HeaderInfo)
        SqlFile.write("/*\n")
        SqlFile.write("Purpose: Transfer " + FeatureClass + " data from the field Trimble data collection application to the AK_ShallowLakes monitoring SQL Server database.\n")
        SqlFile.write("Source geodatabase: " + GeoDB  + "\n") 
        SqlFile.write("FeatureClass: " + FeatureClass  + "\n") 
        SqlFile.write("SQL file name : " + SqlFile.name + "\n")
        SqlFile.write("Script generated by: " + username + ".\n")
        SqlFile.write("Datetime: " + str(datetime.datetime.now())  + ".\n")
        SqlFile.write("*/\n\n")
        
        # loop through the data rows and translate the data cells into an SQL insert query
        i = 0
        for row in arcpy.da.SearchCursor(FeatureClass,Field_names):
            

            # Get the field values into variables
            PondName = str(row[13])
            SampleDate = str(row[10])
            SPECIES = str(row[4])
            NUM_ADULTS = str(row[6])
            NUM_YOUNG = str(row[7])
            DETECTION_TYPE = str(row[5])
            LATITUDE = str(row[12])
            LONGITUDE = str(row[11])
            COMMENTS = str(row[9])
            SOURCE = SourceFilename
            SampleDateShort = GetShortDate(SampleDate) # Events in tblEvents should only have a date, not a datetime, this strips the time part off the sample date

            # Validation query
            ValidateQuery = ValidateQuery + "   -- (PondName='" + PondName + "' and  SampleDate = Convert(Date,'" + SampleDate + "')) Or\n"

            # Ensure the parent Event exists
            EventExistsQuery = EventExistsQuery + "    EXISTS  (SELECT PONDNAME FROM tblEvents WHERE Pondname='" + PondName + "' And SampleDate = Convert(Date,'" + SampleDate + "')) And \n"

            # Ensure the record does not exist already
            RecordExistsQuery = RecordExistsQuery + "            NOT EXISTS (SELECT * FROM tblLoons WHERE Pondname='" + PondName + "' And SampleDate = Convert(Date,'" + SampleDate  + "') And SPECIES = '" + SPECIES + "' And NUM_ADULTS = " + NUM_ADULTS + " And NUM_YOUNG = " + NUM_YOUNG + " And Latitude = " + LATITUDE + " And Longitude = " + LONGITUDE + " And Comments = '" + COMMENTS + "') And \n"
			#SELECT 'NSERT INTO tblLoons(PONDNAME,SAMPLEDATE,SPECIES,NUM_ADULTS,NUM_YOUNG,DETECTION_TYPE,LATITUDE,LONGITUDE,COMMENTS,SOURCE) VALUES(,,None,2,0,Visual,65.4383331948,-143.55705411,,UCH_2020_Deployment.gdb);'
            #--INSERT INTO tblLoons(PONDNAME,SAMPLEDATE,SPECIES,NUM_ADULTS,NUM_YOUNG,DETECTION_TYPE,LATITUDE,LONGITUDE,COMMENTS,SOURCE) VALUES('YUCH-082','2020-6-16','None',2,0,'Visual',65.3324991812,-142.943317472,'','YUCH_2020_Deployment.gdb');
		    #ELSE
			#SELECT 'Record exists'

            # Write the insert query to file
            InsertQueries = InsertQueries + "                INSERT INTO " + TableName + "(PONDNAME,SAMPLEDATE,SPECIES,NUM_ADULTS,NUM_YOUNG,DETECTION_TYPE,LATITUDE,LONGITUDE,COMMENTS,SOURCE) VALUES("  + "'"  + PondName + "','" + SampleDateShort + "','" + SPECIES + "'," + NUM_ADULTS + "," + NUM_YOUNG + ",'" + DETECTION_TYPE + "'," + LATITUDE + "," + LONGITUDE + ",'" + COMMENTS + "','" + SOURCE + "');\n"

            #increment the counter
            i = i + 1
            
        SqlFile.write("USE AK_ShallowLakes\n\n")
        SqlFile.write("-- Execute the query below to view/validate records that may be altered.\n-- " + ValidateQuery[:len(ValidateQuery) - 3] + "\n\n")

        # Write out the query that will determine if the required Events all exist
        EventExistsQuery = "IF " + EventExistsQuery[:len(EventExistsQuery) - 6] + '\n' # Remove the trailing ' and '

        # # If the parent Events don't exist in tblEvents then exit the procedure
        SqlFile.write(EventExistsQuery + "    BEGIN\n")
        SqlFile.write("        PRINT 'The required parent Event records exist in tblEvents.'\n")
        SqlFile.write("        IF " + RecordExistsQuery[:len(RecordExistsQuery) - 6] + "\n")
        SqlFile.write("            BEGIN\n")
        
        # If we get here then the Events exist and the records to be inserted do not exist, insert them.
        SqlFile.write("               -- Danger zone below. ROLLBACK on error.\n")
        SqlFile.write("               -- Insert the records\n")
        SqlFile.write("                PRINT 'Checks complete, inserting the records'\n")
        SqlFile.write("                BEGIN TRANSACTION -- COMMIT ROLLBACK\n")
        SqlFile.write(InsertQueries)
        SqlFile.write("               PRINT '" + str(i) + " records inserted from " + FeatureClass + " into database table " + TableName + ".'\n")
        SqlFile.write("               PRINT 'DO NOT FORGET TO COMMIT OR ROLLBACK OR THE DATABASE WILL BE LEFT IN A HANGING STATE!!!!'\n")
        SqlFile.write("            END\n")
        SqlFile.write("        ELSE\n")
        SqlFile.write("            PRINT 'INSERTS ABORTED: No records were inserted because one or more records you are trying to insert already exists. Uncomment the validation query above and execute it by itself to see the records in question.'\n")
        # # 
        # # 
        # # SqlFile.write("        ELSE\n")
        # # SqlFile.write("            print 'One or more records exist already. Uncomment and use the validation query above to help determine which " + FeatureClass + "\\" + TableName + " records exist already.'\n")
        SqlFile.write("    END\n")
        SqlFile.write("ELSE\n    PRINT 'INSERTS ABORTED: No records were inserted because one or more parent Event records (tblEvents) related to the record you are trying to insert does not exist.'\n\n")

        

        # Let user know we're done
        FinishedMessage = FeatureClass + " data written to " + SqlFile.name.replace("/","\\" + "\n")
        print(FinishedMessage)
        arcpy.AddMessage(FinishedMessage)

    # When something goes wrong, let user know
    except:
        e = sys.exc_info()[0]
        error = '\n-------------------------------------------------\n ERROR: ' + FeatureClass + ' ' + str(e) + "\n-------------------------------------------------\n"
        arcpy.AddMessage(error)
        print(error)





def Export_Water_Profile():
    # try:
        FeatureClass = "Water_Profile_Joined" # Geodatabase feature class name
        TableName = "tblWaterProfiles" # Database table name

        # This will be the output SQL file, same directory as the source geodatabase.
        SqlFile = os.path.dirname(arcpy.env.workspace) + '/' + SourceFilename + '_' + FeatureClass + '_Insert.sql'
        
        # if the SQL file exists already then delete it 
        if os.path.exists(SqlFile):
            arcpy.AddMessage("File exists: " + SqlFile + '. Deleted')
            os.remove(SqlFile)
        SqlFile = open(SqlFile,'a')  

        # Create the first half of the SQL insert query
        SqlPrefix = 'INSERT INTO ' + TableName + '([PONDNAME],[SAMPLEDATE],[SAMPLENUMBER],[SAMPLETIME],[SAMPLEDEPTH]) VALUES('

        # This will hold the insert queries as they are built
        InsertWaterProfileQueries = ""
        InsertWaterSamplesQueries = ""

        # We need a query to determine if all the Events needed in the new data to be imported exist in tblEvents or not
        # Build up a query to determine this.
        EventExistsQuery = "-- Determine if all the necessary parent Event records exist before trying to insert\nIF\n"

        # Build a query to select the just inserted records in order to validate them
        ValidateQuery = "SELECT * FROM " + TableName + " WHERE\n"

        # Get the featureclass' field names
        Fields = arcpy.ListFields(FeatureClass)
        Field_names =  [Field.name for Field in Fields]

        # Write the header info to file
        SqlFile.write(HeaderInfo)
        SqlFile.write("/*\n")
        SqlFile.write("Purpose: Transfer " + FeatureClass + " data from the field Trimble data collection application to the AK_ShallowLakes monitoring SQL Server database.\n")
        SqlFile.write("Source geodatabase: " + GeoDB  + "\n") 
        SqlFile.write("Source FeatureClass: " + FeatureClass  + "\n") 
        SqlFile.write("Destination table name: " + TableName + "\n") 
        SqlFile.write("SQL file name : " + SqlFile.name + "\n")
        SqlFile.write("Script generated by: " + username + ".\n")
        SqlFile.write("Datetime: " + str(datetime.datetime.now())  + ".\n")
        SqlFile.write("*/\n\n")

        SqlFile.write("BEGIN TRANSACTION -- COMMIT ROLLBACK\n\n")
        
        # loop through the data rows and translate the data cells into an SQL insert query
        for row in arcpy.da.SearchCursor(FeatureClass,Field_names):
            i = 0

            # Get the field values into variables
            PondName = str(row[10])
            SampleDate = str(row[7])
            SampleNumber = str(row[5])
            if SampleNumber.strip() == '':
                SampleNumber = 'A'
            SampleTimeLong = str(row[7])
            SampleTime = SampleTimeLong
            SampleDepth = str(row[4])
            SOURCE = SourceFilename
            SampleDateShort = GetShortDate(SampleDate) # Events in tblEvents should only have a date, not a datetime, this strips the time part off the sample date

            # Validation query
            ValidateQuery = ValidateQuery + "   -- (PondName='" + PondName + "' and  SampleDate = Convert(Date,'" + SampleDate + "')) Or\n"

            # Ensure the parent Event exists
            EventExistsQuery = EventExistsQuery + " EXISTS  (SELECT PONDNAME FROM tblEvents WHERE Pondname='" + PondName + "' And SampleDate = Convert(Date,'" + SampleDate + "')) And \n "

            # Write the insert query to file
            InsertWaterProfileQueries = InsertWaterProfileQueries  + SqlPrefix + "'"  + PondName + "',Convert(Date,'" + SampleDateShort + "'),'" + SampleNumber + "','" + SampleTime + "'," + SampleDepth + ");\n"
            InsertWaterSamplesQueries = InsertWaterSamplesQueries + "INSERT INTO tblWaterSamples([PONDNAME],[SAMPLEDATE],[SAMPLENUMBER],[SAMPLETIME],[Depth]) VALUES('"  + PondName + "',Convert(Date,'" + SampleDateShort + "'),'" + SampleNumber + "','" + SampleTime + "'," + SampleDepth + ")\n"
        
        # Write out the query that will determine if the required Events all exist
        EventExistsQuery = EventExistsQuery[:len(EventExistsQuery) - 6] + '\n' # Remove the trailing ' and '
        
        SqlFile.write(EventExistsQuery + "\n    BEGIN\n    -- Insert the records\n\n")
        SqlFile.write("-- Insert the water samples first\n")
        SqlFile.write(InsertWaterSamplesQueries)
        SqlFile.write("\n-- Insert the water profiles\n")
        SqlFile.write(InsertWaterProfileQueries)
        SqlFile.write("   END\n")
        SqlFile.write("ELSE\n   Print 'One or more parent Event records related to the record you are trying to insert does not exist.'\n\n")

        SqlFile.write("-- Execute the query below to validate the inserted records.\n-- " + ValidateQuery[:len(ValidateQuery) - 3])

        # Let user know we're done
        FinishedMessage = FeatureClass + " data written to " + SqlFile.name.replace("/","\\" + "\n")
        print(FinishedMessage)
        arcpy.AddMessage(FinishedMessage)

    # When something goes wrong, let user know
    # except expression as identifier:
    #     error = 'Error: ' + FeatureClass + ' ' + str(e)
    #     arcpy.AddMessage(error)
    #     print(error)







def GetShortDate(LongDate):
    TheDate = datetime.datetime.strptime(LongDate, '%Y-%m-%d %H:%M:%S')
    ShortDate = str(TheDate.year) + "-" + str(TheDate.month) + "-" + str(TheDate.day)
    return ShortDate


# start here
#Export_CheckPondsExist()
Export_Secchi_Joined()
Export_Depth_Joined()
Export_Loons_Joined()
Export_Water_Profile()





