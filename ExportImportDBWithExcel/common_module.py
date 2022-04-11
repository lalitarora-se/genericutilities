import os,logging
from six.moves import configparser
import datetime as dt
import pandas as pd
import sys
from openpyxl import load_workbook

config = None
script_run_time = None 

def addExportSheet(df ,excelSheetName):
    global config, script_run_time
    d = script_run_time
    export_file = config.get('Export_Details', 'Export_FilePath')    
    export_file = export_file.replace('.xlsx',''.join(str(x) for x in (d.month, d.day, d.year,'_',d.hour,d.minute,d.second)) + '.xlsx')

    if os.path.isfile(export_file):
        book = load_workbook(export_file)
        writer = pd.ExcelWriter(export_file, engine='openpyxl')
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        df.to_excel(writer,sheet_name=excelSheetName,index = False)
        writer.save()
        writer.close()
    else:
        writer = pd.ExcelWriter(export_file, engine='openpyxl')
        df.to_excel(writer, sheet_name=excelSheetName, index=False)  
        writer.save()
        writer.close()  


def readConfig():
    global config
    config = configparser.ConfigParser()
    config.read('config.ini')    

def setLogger():
    global config, script_run_time
    d = script_run_time
    log_file = os.path.join(config.get('Log_Details', 'Log_FilePath'), config.get('Log_Details', 'Log_FileInitials') + ''.join(str(x) for x in (d.month, d.day, d.year,'_',d.hour,d.minute,d.second))+".log")
    log_level = config.get('Log_Details', 'Log_Level')

    a_logger = logging.getLogger()
    a_logger.setLevel(logging.DEBUG)

    output_file_handler = logging.FileHandler(log_file)
    stdout_handler = logging.StreamHandler(sys.stdout)

    a_logger.addHandler(output_file_handler)
    a_logger.addHandler(stdout_handler)

    
    #logging.basicConfig(filename=log_file, level=logging.INFO)
    logging.info('Logging Started')