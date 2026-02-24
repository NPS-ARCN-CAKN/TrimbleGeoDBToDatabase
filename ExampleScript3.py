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
import TrimbleGeoDBToDatabase
import TestTrimbleGeoDB

from TrimbleGeoDBToDatabase import Continuous

def Transform():

    arcpy.env.workspace = GEO_DB_PATH

    # Deployment processing
    TrimbleGeoDBToDatabase.ExportContinuousJoined(Continuous.DEPLOYMENT_INSERT, '2023-09-08', '2023-09-25')

    # Retrieval processing
    TrimbleGeoDBToDatabase.ExportContinuousJoined(Continuous.RETRIEVAL_UPDATE, '2024-05-24', '2024-06-21')

if __name__ == "__main__":
    Transform()
