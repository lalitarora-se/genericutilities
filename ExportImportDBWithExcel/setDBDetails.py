import arcpy
import os
import pandas as pd
import common_module as common
import re
import feature_mapping
import logging

def readExcel():
    import_file = common.config.get('Import_Details', 'Import_FilePath')
    feature_sheet_name  = common.config.get('Import_Details', 'feature_sheet_name')
    field_details = df = pd.read_excel(import_file, sheetname=feature_sheet_name)  
    return field_details    
    
def prepFieldList():
    data_set = {}
    dataset_wildcard = common.config.get('DB_Details', 'dataset_wildcard')    
    feature_wildcard = common.config.get('DB_Details', 'feature_wildcard')   
    fieldNamesToSkip = common.config.get('DB_Details', 'fieldNamesToSkip')     
    
    datasets = arcpy.ListDatasets(dataset_wildcard,feature_type='feature')
    datasets = [''] + datasets if datasets is not None else []

    
    for ds in datasets:
        for fc in arcpy.ListFeatureClasses(feature_wildcard,feature_dataset=ds):
            fc_path = os.path.join(arcpy.env.workspace, ds, fc)
            fields = arcpy.ListFields(fc_path)
            field_dict = {}
            fieldToBeRemoved = []
            for field in fields:
                if field.name in ('WORKREQUESTID', 'DESIGNID', 'WORKLOCATIONID', 'WORKFLOWSTATUS', 'WORKFUNCTION'):
                    fieldToBeRemoved.append(field.name)
                else:
                    field_dict[field.name]= {"type": field.type, "length": field.length}
                #print(ds,fc,field.name, field.type, field.length)
            if len(fieldToBeRemoved) > 0:
                arcpy.DeleteField_management(fc_path, fieldToBeRemoved)
            if not (ds in data_set.keys()):
                data_set[ds] = {fc: field_dict}
            data_set[ds][fc] = field_dict
    
    for table in arcpy.ListTables():
        ds = ""
        table_path = os.path.join(arcpy.env.workspace, table)
        fields = arcpy.ListFields(table_path)
        field_dict = {}
        fieldToBeRemoved = []

        for field in fields:
            if field.name in ('WORKREQUESTID', 'DESIGNID', 'WORKLOCATIONID', 'WORKFLOWSTATUS', 'WORKFUNCTION'):
                fieldToBeRemoved.append(field.name)
            else:
                field_dict[field.name]= {"type": field.type, "length": field.length}
            #print(ds,fc,field.name, field.type, field.length)
        if len(fieldToBeRemoved) > 0:
            arcpy.DeleteField_management(table_path, fieldToBeRemoved)        
        if not (ds in data_set.keys()):
            data_set[ds] = {table: field_dict}
        data_set[ds][table] = field_dict

    return data_set


def FixFieldType(fieldType):
    gdbType = fieldType
    gdbLength = None
    
    textTypeRE = re.compile('Text\s*\((\d+)\)', re.IGNORECASE)
    TypeMap = {'Integer': 'LONG', 'Small Integer': 'SHORT','SmallInteger': 'SHORT', 'Double': 'DOUBLE', 'Date': 'DATE'}
    SDMLCaseFieldToCreateTypeMap = {'double': 'Double','text': 'String', 'long': 'Integer', 'short': 'SmallInteger', 'guid': 'Guid', 'date': 'Date'}
    
    textMatch = textTypeRE.match(fieldType)
    if textMatch:
        gdbLength = int(textMatch.group(1))
        gdbType = 'TEXT'
    elif gdbType in TypeMap:
        gdbType = TypeMap[gdbType]
    return (gdbType, gdbLength)
            
def CreateOrModifyMissingFeatureClassFields():
    FieldsFromExcel = readExcel()    
    FieldsFromDatabase = prepFieldList()
    
        
    print(FieldsFromDatabase.keys())
    
    options = ['Y','Yes','y','yes']
  
    # selecting rows based on condition
    fieldsToBeMigrated = FieldsFromExcel[FieldsFromExcel['Migrate?'].isin(options)]

    for index, row in fieldsToBeMigrated.iterrows(): #drop_duplicates('Feature Name', keep='first').
        if row['Feature Name'] not in feature_mapping.SourceToDestNameMapping.keys():
            logging.warning("Mapping for %s does not exists." %(row['Feature Name']))
        else:
            for feature in feature_mapping.SourceToDestNameMapping[row['Feature Name']]:
                field = row['Field Name'].replace("gs_","",1)
                if '/' in feature:
                    dataset = feature.split('/')[0]
                    featname = feature.split('/')[1]
                else:
                    dataset = ""
                    featname = feature
                
                if featname not in FieldsFromDatabase[dataset].keys():
                    logging.warning("Found excel mapping for %s feature in database as %s. But feature does not exist in database." %(row['Feature Name'],feature))
                    continue
                #else:
                    #logging.info("Found excel mapping for %s feature in database as %s." %(row['Feature Name'],feature))
                if field.upper() == "SHAPE":
                    continue

                if field not in FieldsFromDatabase[dataset][featname]:
                    try: 	
                        fullFCName = os.path.join(arcpy.env.workspace, dataset, featname)
                        (gdbType, gdbLength) = FixFieldType(row['Data Type'])
                        if gdbLength is None:
                            gdbLength = 100
                        domain = None #row['Domain']
                        arcpy.AddField_management (fullFCName, field, gdbType, None, None, gdbLength, None, True, 'NON_REQUIRED', domain)                  
                        logging.info("Added %s (%s type,%s length ) in %s" %(field, gdbType,  gdbLength,fullFCName))                        

                    except arcpy.ExecuteError as EEF:
                        logging.info("Error while adding %s (%s type,%s length ) in %s" %(field, gdbType,  gdbLength,fullFCName))
                        logging.warning('skipped:' + str(EEF))
                #else:
                    #logging.info(field+ " field already exists in feature "+ feature)

        '''
        field = row['field_name']
        if row['dataset'] not in FieldsFromDatabase.keys():
            print("%s dataset don't exist in DB." %(row['dataset']))
            continue
        if row['feture_name'] not in FieldsFromDatabase[row['dataset']].keys():
            print("%s feature don't exist in %s dataset of DB." %(row['feture_name'], row['dataset']))
            continue
        if field not in FieldsFromDatabase[row['dataset']][row['feture_name']]:
            try: 	
                fullFCName = os.path.join(arcpy.env.workspace, row['dataset'], row['feture_name'])
                (gdbType, gdbLength) = FixFieldType(row['field_type'])
                if gdbLength is None:
                    gdbLength = row['field_length']
                domain = row['domain_name']

                print("Adding", fullFCName, field, gdbType,  gdbLength)
                #FeatureClass, FieldName, FieldType (eg SHORT), fieldPrecision, fieldScale, fieldLength, alias, isNullable
                #arcpy.AddField_management (fullFCName, field, gdbType, None, None, gdbLength, None, True, 'NON_REQUIRED', domain)                
            except arcpy.ExecuteError as EEF:
                print 'skipped:', FieldsFromExcel, EEF
        '''


        

