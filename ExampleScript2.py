##### Command line usage ######
# When the variable 'GEO_DB_PATH' is set to the path of the
# geodatabase (see below), the expectation is that the user will
# execute this program by using the installed ArcGIS Python typically
# located at a file path that looks similar to (might be located
# somewhere else on your system):
# c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat

# Executing 'ExampleScript2.py' from ArcGIS Pro commandline:

# >c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat ExampleScript2.py

# The output is written to the same directory as the referenced
# geodatabase in the 'GEO_DB_PATH' argument supplied to each function.

# Example script 'ExampleScript2.py':

import arcpy
import TrimbleGeoDBToDatabase
import TestTrimbleGeoDB
import TableUtility
from TableUtility import Feature

def TransformGeoDB():
    """
    This script transforms Feature Classes, processed by Trimble
    Pathfinder, and transforms them into '_Joined' Feature Classes by
    using the imported function 'TableUtility.TransformTable'.
    """

    GEO_DB_PATH = "C:/fake_dir/fake.gdb"
    arcpy.env.workspace = GEO_DB_PATH

    MonumentFCName = "monuments2021"

    WaterSampleFCName = "GCS_2011_Sample_8_15_2024"
    DepthFCName = "GCS_2011_Depths_8_15_2024"
    SecchiFCName = "GCS_2011_Secchi_8_15_2024"
    LoonFCName = "Loons_10_30_2024_NAD_83_2011"
    DeploymentFCName = "GCS_2011_Deployment_8_15_2024"
    RetrievalFCName = "GCS_2011_Retrieval_8_15_2024"

    KeepFieldsFun = TableUtility.GetKeptFieldsFromPathfinder
    AlterFieldsFun = TableUtility.AlterFieldNamesFromPathFinder

    print("Transforming WATER_SAMPLE")
    TableUtility.TransformTable(Feature.WATER_SAMPLE,
                                WaterSampleFCName,
                                MonumentFCName,
                                KeepFieldsFun,
                                AlterFieldsFun,
                                "Water_Sample_Joined")

    print("Transforming DEPTH")
    TableUtility.TransformTable(Feature.DEPTH,
                                DepthFCName,
                                MonumentFCName,
                                KeepFieldsFun,
                                AlterFieldsFun,
                                "Depth_Joined")

    print("Transforming SECCHI")
    TableUtility.TransformTable(Feature.SECCHI,
                                SecchiFCName,
                                MonumentFCName,
                                KeepFieldsFun,
                                AlterFieldsFun,
                                "Secchi_Joined")

    print("Transforming LOON")
    TableUtility.TransformTable(Feature.LOON,
                                LoonFCName,
                                MonumentFCName,
                                KeepFieldsFun,
                                AlterFieldsFun,
                                "Loons_Joined")

    print("Transforming DEPLOYMENT")
    TableUtility.TransformTable(Feature.DEPLOYMENT,
                                DeploymentFCName,
                                MonumentFCName,
                                KeepFieldsFun,
                                AlterFieldsFun,
                                "Deployment_Joined")

    print("Transforming RETRIEVAL")
    TableUtility.TransformTable(Feature.RETRIEVAL,
                                RetrievalFCName,
                                MonumentFCName,
                                KeepFieldsFun,
                                AlterFieldsFun,
                                "Retrieval_Joined")

if __name__ == "__main__":
    TransformGeoDB()
