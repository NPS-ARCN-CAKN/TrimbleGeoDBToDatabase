##### Command line usage ######
# When the variable 'GEO_DB_PATH' is set to the path of the
# geodatabase (see below), the expectation is that the user will
# execute this program by using the installed ArcGIS Python typically
# located at a file path that looks similar to (might be located
# somewhere else on your system):
# c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat

# Example script 'script.py':

# import arcpy
# import TrimbleGeoDBToDatabase
# import TestTrimbleGeoDB
#
# def TransformGeoDB():
#     GEO_DB_PATH = "C:/fake_dir/fake.gdb"
#     arcpy.env.workspace = GEO_DB_PATH
#
#     # Transform and write SQL 'INSERT' statements.
#     TrimbleGeoDBToDatabase.ExportSecchiJoined()
#
#     # Find duplicate keys in records; collect duplicates in a
#     # dictionary.
#     # 'd' is a dictionary.
#     d = TestTrimbleGeoDB.FindDuplicateSecchiKeys()
#     print('Secchi: ', d)
#
# if __name__ == "__main__":
#     TransformGeoDB()

# Executing 'script.py' from ArcGIS Pro commandline:

# >c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat script.py

# The output is written to the same directory as the referenced
# geodatabase in the 'GEO_DB_PATH' argument supplied to each function.
