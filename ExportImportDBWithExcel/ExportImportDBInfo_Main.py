import arcpy
import logging
import common_module as common
import getDBDetails
import setDBDetails
import datetime as dt


def ExportImportDBInfo_Main():    
    common.readConfig()
    arcpy.env.workspace = common.config.get('DB_Details', 'conn_path')
    arcpy.env.overwriteOutput = True  

    common.script_run_time = dt.datetime.now() 
    common.setLogger()
    
    #Import
    #setDBDetails.CreateOrModifyMissingFeatureClassFields()

    #Export
    getDBDetails.getFeatureMapping()
    getDBDetails.getFeatureFieldSubtypeDomain()
    getDBDetails.getDomainDetails()

if __name__ == "__main__":
    ExportImportDBInfo_Main()