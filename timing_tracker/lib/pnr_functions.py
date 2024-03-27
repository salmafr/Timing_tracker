#some pnr functions are commun between pnr and sta so I'll import the pnr module in the sta script wwhen needed
import re
import pandas as pd
import glob
import json
import csv
def read_txt_file(filename):
    with open(filename) as f:
        lines=f.readlines() 
    return lines

#the next function will join all the lines of a file in one
def join_file(filename):
    with open(filename) as f:
        return " ".join(line.strip() for line in f)

#split a file into paragraphs based on the same start and end pattern
def split_paragraphs(filename,pattern):
    joined_file=join_file(filename)
    listt=[]
    #store in a list the paragraphs extracted 
    for x in re.finditer( pattern, str(joined_file)):
        listt.append(x.group())
    return listt

def get_metric_per_pattern (paragraph,pattern):
    #get a specific value or string in a paragraph based on the pattern indicated 
    for x in re.finditer( pattern,paragraph):
        return(x.group(1))

def get_scenarios_per_path(paragraphs):
    path_listt=[] #store all the pathgroups existed in a list 
    path_scenario={} #create a dictionnary that will associated each pathgroup with the scenarios
      
    for paragraph in paragraphs: #for each paragraph we will extract the scenario and the pathgroup
        scenario= get_metric_per_pattern (paragraph,r"Scenario[\s]+'([\w\S]+)'")
        path_group= get_metric_per_pattern (paragraph,r"Timing.*[\s]+'([\w\S]+)'")

        if path_group not in path_listt :
            path_listt.append(path_group) 
            #print(path_group)
            path_scenario[path_group]=list([scenario])   
        else:
            for path in path_listt:
                if path_group==path: #if a pathgroup is already stored and existed in another paragraph we'll extract just the scenario and add it to the list of scenarios associated to this pathgroup  
                    path_scenario[path_group].append(scenario)
    return path_scenario

   
def get_setup_metrics_per_paragraph(paragraphs):
    setup_metrics={} #create a dictionary:the key will be the pathgroup 
    scenario_set_up_metrics={}
    path_scenario=get_scenarios_per_path(paragraphs)
    for key in path_scenario.keys():
        scenario_set_up_metrics={}
        for index,paragraph in enumerate(paragraphs):
            path_group= get_metric_per_pattern (paragraph,r"Timing.*[\s]+'([\w\S]+)'")
            scenario= get_metric_per_pattern (paragraph,r"Scenario[\s]+'([\w\S]+)'")
            if key==path_group :
                for index,scenarios in enumerate(path_scenario[key]):
                    if (path_scenario[key][index]==scenario):
                        if re.search(r'No.*Violating.*Paths',paragraph):#extract the setup information after testing that the paragraph contains them since there are some paragraphs that contains just hold information 
                            setup_Npaths= get_metric_per_pattern (paragraph,r"No.*Violating.*Paths:[\s]+([-\d.]+)")

                            if int(setup_Npaths) >0: #extract setup metrics (wns and tns) for each pathgroup for each scenario if there are violations

                                setup_wns= get_metric_per_pattern (paragraph,r"Critical\sPath\sSlack:[\s]+([-\d.]+)")
                                setup_tns= get_metric_per_pattern (paragraph,r"Total.+Slack:[\s]+([-\d.]+)")
                            else : #if there is no violation in a specific scenario of a path group we set 0 by default to the metrics showing that there is  no violation
                                setup_wns=0
                                setup_tns=0
                        else:
                            setup_Npaths=0
                            #print("No setup information")
                            setup_wns=0
                            setup_tns=0
                        #for each scenario store the 3 metrics( wns,tns and number of violating path) as values in a dictionary
                        scenario_set_up_metrics[path_scenario[key][index]]=list([setup_Npaths,setup_wns,setup_tns])
    #the next dictionary has the following form:{pathgroup1:{scenario1:[wns,tns,Npaths],scenario2:[wns,tns,Npaths]},pathgroup2:{scenario}....}
        setup_metrics[key]=scenario_set_up_metrics
    return setup_metrics #store for each pathgroup for each scenario associated the setup metrics values
#the next function follows the same logic as the previous one but for the hold timing 
def get_hold_metrics_per_paragraph(paragraphs):
    hold_metrics = {}
    scenario_hold_metrics={}
    path_scenario=get_scenarios_per_path(paragraphs)
    for key in path_scenario.keys():
        scenario_hold_metrics={}
        for index,paragraph in enumerate(paragraphs):
            path_group= get_metric_per_pattern (paragraph,r"Timing.*[\s]+'([\w\S]+)'")
            scenario= get_metric_per_pattern (paragraph,r"Scenario[\s]+'([\w\S]+)'")
            if key==path_group :
                for index,scenarios in enumerate(path_scenario[key]):
                    if (path_scenario[key][index]==scenario):
                        hold_Npaths= get_metric_per_pattern (paragraph,r"No.\sof\sHold\sViolations:[\s]+([-\d.]+)")
                        if int(hold_Npaths) >0:
                            hold_wns= get_metric_per_pattern (paragraph,r"Worst.*?Violation:[\s]+([-\d.]+)")
                            hold_tns= get_metric_per_pattern (paragraph,r"Total\sHold\sViolation:[\s]+([-\d.]+)")
                        else :
                            hold_wns=0
                            hold_tns=0
                        scenario_hold_metrics[path_scenario[key][index]]=list([hold_Npaths,hold_wns,hold_tns])
            #print(scenario_hold_metrics)
        hold_metrics[key]=scenario_hold_metrics
            #print(scenario_hold_metrics)
            #print(hold_metrics)   
    return hold_metrics

#the following function will return the list of indexes of the start and the end of all the paragraphs of the detailed report so we can be based on them to extract the whole paragraph of an endpoint and store from the start to the end without including the not interesting paragraph not 
def get_startpoints_indexes(filename):
    list_scenarios=[]
    list_slack=[]
    for index,line in enumerate(read_txt_file(filename)) :
        if "Startpoint" in line:
            list_scenarios.append(index)
        if "slack" in line :
            list_slack.append(index)
        
    return list_scenarios,list_slack
#get the index of the endpoint specified as argument 
def get_endpoint_indexe(filename,endpoint):
    for index,line in enumerate(read_txt_file(filename)) :
        if endpoint in line:
            return index
#the following function will return the paragraph in the detailed report containing the endpoint specified as argument 
def get_start_and_stop_index_basedon_endpoint_index(filename,endpoint):
    startpoints_index=[]
    slack_index=[]
    endpoint_index=get_endpoint_indexe(filename,endpoint)
    #print(endpoint_index)
    startpoint_indexes,slack_indexes=get_startpoints_indexes(filename)
    if endpoint_index is not None:
        
        for startpoint in startpoint_indexes:
            if startpoint <endpoint_index: #the start index of the paragraph will be less than the index of the endpoint 
                startpoints_index.append(startpoint)
        #print(startpoints_index)
        #the start index will be the line having the index the more near from the index of the endpoint specified as argument that's why we specify the max of the indexes of the startpoint less than the index of the endpoint
        start_index= max(startpoints_index)
        #print(start_index)
        for slack in slack_indexes:
            if slack >endpoint_index:
                slack_index.append(slack)
        #specify the end pf the paragraph by extracting the index of the line containing the slack which is the nearst from the endpoint index
        stop_index= min(slack_index)
        #print(stop_index)
        paragraph=""
        for line in (read_txt_file(filename))[start_index:stop_index+1]:
            paragraph=paragraph+line
        return paragraph #return the whole paragraph from the strtpoint to the slack based on the endpoint 
#the following function will extract the part where the endpoints table exist in the file based on the line containg the heading  
def get_endpoint_pnr(filename):
    paragraph=""
    i=0
    start=0
    file_lines=read_txt_file(filename)
    for line in file_lines:
        i=i+1
        #print(i)
        if 'Endpoint' in line:
            start=i-1
            break
    for line in file_lines[start:-1]:
        paragraph=paragraph+line
    return paragraph
def convert_table_dataframe(filename):
    txtt=get_endpoint_pnr(filename)
    lines = []
    for line in txtt.split('\n'):
        if "No paths" in line:
            pass
        else :
            if line.startswith('Endpoint '): continue 
            if line.startswith('-'): continue 
            if line == '': continue #skip the curent line 
            data = [i.strip() for i in line.split() ] 
            #separate each line of the data  into  columns 
            data = [data[0],data[1],''.join(data[2:4]),data[4],data[5],data[6],data[7],data[8],data[9]] #ecraser avec une seule
            lines.append(data)
            #build a dataframe with the columns specified and insert each part of the line in a column so all the lines of the table will be splitted as previously and be stored as rows in the dataframe
    df = pd.DataFrame(lines, columns=['Endpoint',"parenthse",'Path Delay', 'Path Required','CRP','Slack','Group',' Levels','Scenario'])
    #return the endpoints table as dataframe to simplify the rows processing 
    return df
def get_setup_metrics_per_path(filename_qor,filename_endpoints):
    paragraphs=split_paragraphs(filename_qor,r'Scenario (.*?) (Hold Violations|Violating Paths):\s+\d+')
    setupmetrics=get_setup_metrics_per_paragraph(paragraphs) 
    setup_metrics={}
    df=convert_table_dataframe(filename_endpoints)
    df['Slack'] = df['Slack'].apply(pd.to_numeric)
    for pathgroup in set(df['Group'].tolist()) :
        metrics_list=[]
        path_list=[]
        wns=[]
        tns=[]
        for scenario in setupmetrics[pathgroup].keys():
            path_list.append(int(setupmetrics[pathgroup][scenario][0])) #store the number of violating path for each scenario pf each pathgroup we can apply the sum to get the number violating path of the pathgroup inclusing all the scenarios 
            wns.append(float(setupmetrics[pathgroup][scenario][1])) #the same thing here but we'll get the min value of all of the elements to get the min wns value of the pathgrouo 
            tns.append(float(setupmetrics[pathgroup][scenario][2])) #same thing here we'll store the tns and then apply the sum to get the tns  of the pathgroup 
        #get based on the dataframe stored previously and build 3 other dataframes filtered based on the pathgroup and the range of values of the slack
        greater_than0=df[(df['Group']== pathgroup) & (df['Slack']<=float(-0.000)) & (df['Slack']>float(-0.050))] #dataframe contains just the rows with a specific pathgroup and the slack between -50 pico and 0 pico
        greater_than50=df[(df['Group']== pathgroup) &(df['Slack']>float(-0.100)) & (df['Slack']<=float(-0.050))]
        greater_than100=df[(df['Group']== pathgroup) & (df['Slack']<=float(-0.100))]
        #by getting the length of each dataframe we can get the information about the number of violating paths of each range of slack values 
        metrics_list.extend([float('%.3f' %(min(wns))),float('%.3f' %(sum(tns))),sum(path_list),len(greater_than100.index),len(greater_than50.index),len(greater_than0.index)])       
        #for each pathgroup vioated in the endpoints file extract and store the wns calculated ,tns,number of violating path....
        setup_metrics[pathgroup]=metrics_list
    return setup_metrics
#the following function store the hold metrics of each path group and follows the same logic as the previous one of the setup 
def get_hold_metrics_per_path(filename_qor,filename_endpoints):
    paragraphs=split_paragraphs(filename_qor,r'Scenario (.*?) Hold Violations:\s+\d+')
    holdmetrics=get_hold_metrics_per_paragraph(paragraphs) 
    df=convert_table_dataframe(filename_endpoints)
    df['Slack'] = df['Slack'].apply(pd.to_numeric)
    hold_metrics={}
    #for pathgroup in setup_metrics.keys():
    for pathgroup in set(df['Group'].tolist()) :
        metrics_list=[]
        path_list=[]
        wns=[]
        tns=[]
        for scenario in holdmetrics[pathgroup].keys():
            path_list.append(int(holdmetrics[pathgroup][scenario][0]))
            wns.append(float(holdmetrics[pathgroup][scenario][1]))
            tns.append(float(holdmetrics[pathgroup][scenario][2]))
        greater_than0=df[(df['Group']== pathgroup) & (df['Slack']<=float(-0.000)) & (df['Slack']>float(-0.050))]
        greater_than50=df[(df['Group']== pathgroup) &(df['Slack']>float(-0.100)) & (df['Slack']<=float(-0.050))]
        greater_than100=df[(df['Group']== pathgroup) & (df['Slack']<=float(-0.100))]
        metrics_list.extend([float('%.3f' %(min(wns))),float('%.3f' %(sum(tns))),sum(path_list),len(greater_than100.index),len(greater_than50.index),len(greater_than0.index)])         
        hold_metrics[pathgroup]=metrics_list
    return hold_metrics
#the following function will add a total key to the dictionary specified and add values based on the total of each values from the previous keys the first value of the the total jey will be the sum of the first value of the previous keys 
def total_key(dict):
    listt=[]
    for key in dict.keys():
        listt.append(dict[key][0])
    if bool(dict)==True:
        dict["TOTAL"]=['','','','','','']
        for i in range(0,6):
            sum=0
            for key in dict.keys():
                if key=="TOTAL": #we'll add just the pathgroups keys 
                    break
                if i==0:
                    
                    sum=min(listt) #an exception for the first value of the wns the stored value will be the min balues of the previous values 
                    dict["TOTAL"][0]=float('%.3f' %(sum))
                
                else:
                    sum+=dict[key][i]
                    dict["TOTAL"][i]=float('%.3f' %(sum))
        return dict
#store the setup metrcis of each path group in a json file 
def store_setup_metrics(filename_qor,filename_endpoints,jsonFile_name):
    metrics=get_setup_metrics_per_path(filename_qor,filename_endpoints)
    #print(metrics)
    metrics=total_key(metrics)
    if metrics is not None : #this test is made to not store a json file that contains only total as key 
        with open(jsonFile_name, 'w') as json_file:
            json.dump(metrics, json_file)
#store the hold metrcis of each path group in a json file
def store_hold_metrics(filename_qor,filename_endpoints,jsonFile_name):
    
    metrics=get_hold_metrics_per_path(filename_qor,filename_endpoints)
    #update the metrics dictionary to add the total key 
    metrics=total_key(metrics)
    if metrics is not None :
        with open(jsonFile_name, 'w') as json_file:
            json.dump(metrics, json_file)
#build a new dataframe from the one built before by filtering based on the pathgroup specified and let just the 3 concerned columns before store it in a csv 
def get_violated_endpoints_based_path(filename,pathgroup):
    framess=[]
    df=convert_table_dataframe(filename)
    # selecting rows based on group condition 
    rslt_df = df[df['Group'] == pathgroup]
    rslt_df=rslt_df[['Slack','Scenario','Endpoint']]
    
    return rslt_df  
#the following function will store the list of violated endpoints in a csv file   
def convert_violated_endpoints_to_csv(endpoints_filename,pathgroup,csvFile):
    df=get_violated_endpoints_based_path(endpoints_filename,pathgroup)
    gfg_csv_data = df.to_csv(csvFile, index = False)

def ifword_exist_in_file(filename):
    fd = open(filename,"r")    # open the file in read mode
    file_contents = fd.read()
    if "delay_type max" in file_contents:
        return True
    else :
        return False
#the following function will tell if the endpoint file  contains setup infromation or hold information since the name of files may be similar and this information is needed to extract information from the right one based on the delay type
def get_setup_and_hold_endpoints_file(endpoints_path):
    if len(endpoints_path)==2:
        for endpoint in endpoints_path:
            boolean=ifword_exist_in_file(endpoint)
            if boolean==True:
                setup=endpoint
                
            else :
                hold=endpoint
    else :
        #test if max or min word exists in the file 
        boolean=ifword_exist_in_file(endpoints_path[0])
        if boolean==True: #if the file concerns setup info the path will be saved in the varibale setup and the hold variale will set to none  
            setup=endpoints_path[0]
            hold=None
        else : #the same logic if the file concerns the hold information we'll set the setup varibale to none
            hold=endpoints_path[0]
            setup=None
    return list([setup,hold]) #the function return a list that contains the endpoints file path of the setup and the hold one will be none 

