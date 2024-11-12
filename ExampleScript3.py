##### Command line usage ######
# When the variable 'GEO_DB_PATH' is set to the path of the
# geodatabase (see below), the expectation is that the user will
# execute this program by using the installed ArcGIS Python typically
# located at a file path that looks similar to (might be located
# somewhere else on your system):
# c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat

# Executing 'ExampleScript3.py' from ArcGIS Pro commandline:

# >c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat ExampleScript3.py

# The output is written to the same directory as the referenced
# geodatabase by the 'GEO_DB_PATH' variable.

# Example script 'ExampleScript3.py':

import arcpy
import csv
import TrimbleGeoDBToDatabase
import TestTrimbleGeoDB

from TrimbleGeoDBToDatabase import Continuous

def Transform():
    # Deployment processing
    GEO_DB_PATH = "C:/fake_dir/fake_1.gdb"
    arcpy.env.workspace = GEO_DB_PATH

    TrimbleGeoDBToDatabase.ExportContinuousJoined(Continuous.DEPLOYMENT_INSERT, '2023-09-08', '2023-09-25', csv_reader)

    # Retrieval processing

    # Get deployment site names and dates from a CSV file, for which
    # the retrievals make sense.
    DEPLOY_INPUT = 'C:/fake_dir/input.csv'

    GEO_DB_PATH = "C:/fake_dir/fake_2.gdb"
    arcpy.env.workspace = GEO_DB_PATH

    with open(DEPLOY_INPUT, mode='r', newline='') as file:
        # In this case, the CSV file has a tab delimiter.
        csv_reader = csv.DictReader(file, delimiter='\t')

        # Pass in the CSV input as a csv.DictReader.
        # By default, the output does not keep the comments. See doc
        # notes for function 'ExportContinuousJoined'.
        TrimbleGeoDBToDatabase.ExportContinuousJoined(Continuous.RETRIEVAL_UPDATE, '2024-05-24', '2024-06-21', csv_reader)

if __name__ == "__main__":
    Transform()
