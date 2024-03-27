import pnr_functions 
import timeit
import pandas as pd
import glob
from pathlib import Path
import json
import os
import re

def read_txt_file(filename):
    with open(filename) as f:
        lines=f.readlines() #returns a list
    return lines
def read_txt_file_v2(filename): #not read the info related to max capacitance and max transition in reports
    linees=[]
    with open(filename) as f:
        #lines=f.readlines() #returns a list
        for line in f:
            if "max_transition" in line or "min_capacitance" in line or "sequential_clock_min_period" in line:
                return linees
            linees.append(line)

def convert_table_dataframe(file_name,delay_type,pathgroup): 
    txtt=get_endpoints_based_on_pathgroup_delay(file_name,delay_type,pathgroup,"_delay")
    filename=os.path.basename(file_name)
    corner_name=re.match(r"sta_si(.*)_func.*",filename) #get the corner name from each filename containing the list of violations
    Scenario_name="func"+corner_name.group(1) 
    lines = []
    if txtt is None:
        #print("yes")
        return pd.DataFrame()
    else:
        for line in txtt.split('\n'):
            if "No paths" in line:
                pass
            else :
                if "group" in line: continue
                if "Sigma" in line : continue
                if line.startswith('Endpoint '): continue #ecraser avec une seule
                if line.startswith('-'): continue #ecraser avec une seule
                if line == '': continue #ecraser avec une seule
                if len(line.split())<3: continue
                data = [i.strip() for i in line.split() ] #ecraser avec une seule
                data = [data[0],data[1],data[2]] #ecraser avec une seule
                lines.append(data)  #ecraser avec une seule
        df = pd.DataFrame(lines, columns=['Endpoint','Slack',"violated or met"])
    #new_df = df.assign(Scenario=Scenario_name)
        del df['violated or met']
        df.insert(1, "Scenario",Scenario_name,True)
        return df
def get_endpoints_dataframe_per_pathgroup(filenames,delay_type,pathgroup):#We consider that we have already gather automatically the name of the files with the extensio .rpt all all violators path and store them in a list
    frames=[]
    
    for filename in filenames:
        df=convert_table_dataframe(filename,delay_type,pathgroup)
        frames.append(df)
    merged_df=pd.concat(frames) #concatenate all the dataframes that concern a pathgroup into one
    merged_df=pd.DataFrame(merged_df)
    df=merged_df[merged_df.columns[::-1]]
    df=df[(df['Slack']!="0.0000")] #avoid the display of the violations with 0 pico
    
    return df
def get_line_indexes_containing_delay_type(filename,pattern):
    indexes={}
    for index,line in enumerate(read_txt_file_v2(filename)):
        if pattern in line:
            indexes[line]=index
    return indexes

def get_line_indexes_containing_delay_type_summary(filename,pattern):
    indexes={}
    for index,line in enumerate(read_txt_file(filename)):
        if pattern in line:
            indexes[line]=index
    return indexes

def get_next_index_line_summary(filename,line,pattern):
    indexes=get_line_indexes_containing_delay_type_summary(filename,pattern)
    for index,key in enumerate(indexes.keys()) :
        if (line+"\n").strip()==key.strip():
            
            return indexes[list(indexes.keys())[index+1]]

def get_next_index_line(filename,line,pattern):
    indexes=get_line_indexes_containing_delay_type(filename,pattern)
    for index,key in enumerate(indexes.keys()) :
        if (line+"\n").strip()==key.strip():
            if index!=len(list(indexes.keys()))-1:
                return indexes[list(indexes.keys())[index+1]]
            
def get_endpoints_based_on_pathgroup_delay(filename,delay_type,pathgroup,pattern):
    indexes=get_line_indexes_containing_delay_type(filename,pattern)
    paragraph=""
    for key in indexes.keys():
        end=get_next_index_line(filename,key,pattern)
        if (key.__contains__(delay_type) and key.__contains__(pathgroup)):
            start=indexes[key]
            if end !=None:
                list=read_txt_file_v2(filename)[start:end]
            else:
                list=read_txt_file_v2(filename)[start:-2]
            for line in list:
                paragraph=paragraph+line
            return paragraph
def get_summary_based_on_delay(filename,delay_type,pattern): ### CHECK TYPE as pattern
    indexes=get_line_indexes_containing_delay_type_summary(filename,pattern)
    paragraph=""
    for key in indexes.keys():
        if (key.__contains__(delay_type)):
            start=indexes[key]
            end=get_next_index_line_summary(filename,key,pattern)-1
            for line in (read_txt_file(filename))[start:end-1]:
                paragraph=paragraph+line
            return paragraph
def get_metrics_per_path_version(file_name,endpoints_filenames):#10s with THE display
    
    listt=[] 
    for delay in list(["setup","hold"]):
        paragraph=get_summary_based_on_delay(file_name,delay,"## CHECK TYPE")
        #paragraphs = store_paragraphs(file_name,"^## CHECK TYPE.+")
        metrics={}
        for x in re.finditer( r'There are a total of (\d+).+group ([\S]+)\s+ .+: ([-\d.]+)',paragraph,re.MULTILINE):
                
            Path_group=x.group(2) #get the second group of the matching here the name of the group
                
            df=get_endpoints_dataframe_per_pathgroup(endpoints_filenames,delay,Path_group)   
            #extract just the numeric value from the Slack column
            df['Slack'] = df['Slack'].apply(pd.to_numeric)
                #print(df['Slack'])
            PATHS=x.group(1)
            WNS=x.group(3)
            TNS=df['Slack'].sum()
                #print(TNS)
            greater_than0=df[(df['Slack']>float(-0.05)) & (df['Slack']<float(0))]
                #print(delay,Path_group,greater_than0)
            greater_than50=df[(df['Slack']>float(-0.1)) & (df['Slack']<=float(-0.05))]
            greater_than100=df[(df['Slack']<=float(-0.1))]
                
            metrics[Path_group]=list([float('%.3f' %(float(WNS))),float('%.3f' %(float(TNS))),int(PATHS),len(greater_than0.index),len(greater_than50.index),len(greater_than100.index)])
            listt.append(metrics)
        return listt
def convert_violated_endpoints_to_csv(endpoints_filenames,delay_type,pathgroup,csvFile):
    df=get_endpoints_dataframe_per_pathgroup(endpoints_filenames,delay_type,pathgroup)
    df=df.sort_values(by='Slack',ascending=False) #sort the violated endpoint by slack values
    csv_data = df.to_csv(csvFile, index = False) 

def store_metrics(file_name,endpoints_filenames,jsonFile_setup,jsonFile_hold):
    
    setup_and_hold_metrics_dict=get_metrics_per_path_version(file_name,endpoints_filenames)
    setup_metrics=setup_and_hold_metrics_dict[0]
    hold_metrics=setup_and_hold_metrics_dict[1]
    setup_metrics=pnr_functions.total_key(setup_metrics)
    hold_metrics=pnr_functions.total_key(hold_metrics)
    with open(jsonFile_setup, 'w') as json_file1:
        json.dump(setup_metrics, json_file1)
    with open(jsonFile_hold, 'w') as json_file2:
        json.dump(hold_metrics, json_file2)