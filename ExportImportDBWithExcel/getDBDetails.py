import arcpy
import os
import pandas as pd
import common_module as common
from openpyxl import load_workbook
import feature_mapping

class feature_details(object):
    dataset = None
    feture_name = None
    field_name = None
    field_type = None
    field_length = None
    field_alias = None
    field_isrequired = None
    subtype_code = None
    subtype_name = None
    domain_name = None
    domain_type = None

    def __init__(self, dataset = None,feture_name = None,field_name = None,field_type = None,field_length = None,field_alias=None,field_isrequired=None,subtype_code = None,subtype_name = None,domain_name = None,domain_type = None):
        self.dataset = dataset
        self.feture_name = feture_name
        self.field_name = field_name
        self.field_type = field_type
        self.field_length = field_length
        self.field_alias = field_alias
        self.field_isrequired = field_isrequired
        self.subtype_code = subtype_code
        self.subtype_name = subtype_name
        self.domain_name = domain_name
        self.domain_type = domain_type

def getFeatureMapping():
    feature_sheet_name  = common.config.get('Export_Details', 'feature_mapping')

    dictlist = []
    for key, value in feature_mapping.SourceToDestNameMapping.iteritems():
        for item in value:
            temp = [key,item]
            dictlist.append(temp)
    
    data_frame = pd.DataFrame(dictlist, columns = ['COBB_Feature', 'ArcFM_Feature']).sort_values(by=['COBB_Feature','ArcFM_Feature'])  

    common.addExportSheet(data_frame, feature_sheet_name)          


def getFeatureFieldSubtypeDomain():
    dataset = []
    dataset_wildcard = common.config.get('DB_Details', 'dataset_wildcard')    
    feature_wildcard = common.config.get('DB_Details', 'feature_wildcard')        
    feature_sheet_name  = common.config.get('Export_Details', 'feature_sheet_name')
    onlyfirstsubtype  = common.config.get('Export_Details', 'feature_sheet_name_onlyfirstsubtype')

    
    datasets = arcpy.ListDatasets(dataset_wildcard,feature_type='feature')
    datasets = [''] + datasets if datasets is not None else []

    for ds in datasets:
        for fc in arcpy.ListFeatureClasses(feature_wildcard,feature_dataset=ds):
            fc_path = os.path.join(arcpy.env.workspace, ds, fc)
            fields = arcpy.ListFields(fc_path)

            field_dict = {}
            for field in fields:
                field_dict[field.name]= {"type": field.type, "length": field.length,"alias": field.aliasName, "editable":field.editable, "required": field.required, "scale": field.scale, "precision": field.precision}
                #print(ds,fc,field.name, field.type, field.length)

            subtypes = arcpy.da.ListSubtypes(fc_path)
            
            for stcode, stdict in list(subtypes.items()):
                for stkey in list(stdict.keys()):
                    if stkey == 'FieldValues':
                        fields = stdict[stkey]
                        for field, fieldvals in list(fields.items()):
                            if not fieldvals[1] is None:
                                dataset.append(feature_details(ds,fc,field,field_dict[field]["type"],field_dict[field]["length"],field_dict[field]["alias"],field_dict[field]["required"],stcode,stdict["Name"],fieldvals[1].name,fieldvals[1].type))
                            else:
                                dataset.append(feature_details(ds,fc,field,field_dict[field]["type"],field_dict[field]["length"],field_dict[field]["alias"],field_dict[field]["required"],stcode,stdict["Name"],None,None))
                if onlyfirstsubtype:
                    break
                            
    for table in arcpy.ListTables():
        ds = ""
        table_path = os.path.join(arcpy.env.workspace, table)
        fields = arcpy.ListFields(table_path)
        #print(table)

        field_dict = {}
        for field in fields:
            field_dict[field.name]= {"type": field.type, "length": field.length,"alias": field.aliasName, "editable":field.editable, "required": field.required, "scale": field.scale, "precision": field.precision}
        
        subtypes = arcpy.da.ListSubtypes(table_path)
            
        for stcode, stdict in list(subtypes.items()):
            for stkey in list(stdict.keys()):
                if stkey == 'FieldValues':
                    #print(stcode, "\n",stdict, "\n", stdict[stkey])
                    fields = stdict[stkey]
                    for field, fieldvals in list(fields.items()):
                        if not fieldvals[1] is None:
                            dataset.append(feature_details(ds,table,field,field_dict[field]["type"],field_dict[field]["length"],field_dict[field]["alias"],field_dict[field]["required"],stcode,stdict["Name"],fieldvals[1].name,fieldvals[1].type))
                        else:
                            dataset.append(feature_details(ds,table,field,field_dict[field]["type"],field_dict[field]["length"],field_dict[field]["alias"],field_dict[field]["required"],stcode,stdict["Name"],None,None))
            if onlyfirstsubtype:
                break        

    column_list =['dataset','feture_name','field_name','field_type','field_length','field_alias','field_isrequired','subtype_code','subtype_name','domain_name','domain_type']

    df = pd.DataFrame([{field: getattr(set, field) for field in column_list} for set in dataset],columns=column_list).sort_values(by=['dataset','feture_name','field_name'])   

    common.addExportSheet(df, feature_sheet_name)
   

def getDomainDetails():
    domain_sheet_name  = common.config.get('Export_Details', 'domain_sheet_name')

    domain_list = []
    domains = arcpy.da.ListDomains(arcpy.env.workspace)  

    for domain in domains:  
        if domain.domainType == 'CodedValue':  
            domain_name = domain.name  
            coded_value_list = domain.codedValues  
            for value, descrip in coded_value_list.items():  
                domain_list.append([domain_name,value, descrip])            
    
    data_frame = pd.DataFrame(domain_list, columns=['Domain_Name', 'Code', 'Value']).sort_values(by=['Domain_Name','Code'])  

    common.addExportSheet(data_frame,domain_sheet_name)


