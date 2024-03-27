#!/usr/bin/python3.6
import sys
#the next line makes the import of the parser scripts from another folser
sys.path.insert(1,"/vols/sondrel_training/users/Ilham.Elyoubi/timing_tracker/lib")
import pnr_functions
import sta_functions
import tkinter as tk
from tkinter import *
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
import json
import glob
import pandas as pd
import csv
import os

import timeit
from pathlib import Path
from PIL import Image, ImageTk

class VerticalScrolledFrame(Canvas):
    def __init__(self, parent):
        Canvas.__init__(self, parent)
        self.frame = Frame(self)
        self.frame.pack(side="bottom", fill="both", expand=True)
        vscrollbar = Scrollbar(parent, orient="vertical", command=self.yview)
        self.configure(yscrollcommand=vscrollbar.set)

        vscrollbar.pack(side="right", fill="y")
        # Canvas stretch
        self.pack(fill="both", expand=True)  # ,side="left"

        # Keep trace of the window ID
        self.canvas_window = self.create_window((0, 0), window=self.frame,  # anchor="n",
                                                tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)
        # Set a binding on the canvas <Configure> event
        self.bind('<Configure>', self.FrameWidth)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.configure(scrollregion=self.bbox("all"))

    def FrameWidth(self, event):
        # resize the frame with the event.width
        self.itemconfig(self.canvas_window, width=event.width)
class App(Tk):
    def __init__(self):
        super().__init__()
        self.i=0
        def get_timestamp_primetime():
            sta_directory = glob.glob(
                os.getcwd()+"/"+"sgnoff/sta/primetime_signoff*")
            for index, i in enumerate(sta_directory):
                for j in sta_directory[index:]:
                    if re.findall(r"\d+", i) > re.findall(r"\d+", j):
                        sta_directory = i
                    else:
                        sta_directory = j
            return sta_directory
        if len(get_timestamp_primetime()) != 0:
            self.STA_reports_directory = get_timestamp_primetime()
            summary_file = os.path.join(self.STA_reports_directory,"PT_SUMMARY.func.18:04:2022:16:43:45.rpt")
                    
            self.endpoints_files = glob.glob(os.path.join(
                self.STA_reports_directory, "reports")+"/*all_violators_all_paths.pba.rpt")

            if os.path.exists(summary_file) and len(self.endpoints_files) != 0:
                sta_functions.store_metrics(summary_file,self.endpoints_files, "sta_setup.json", "sta_hold.json")
        self.title("T-Tracker")
        icon = PhotoImage(file = '/vols/sondrel_training/users/Ilham.Elyoubi/timing_tracker/lib/icons/logo.gif') # update the path
        # Setting icon of root window
        self.iconphoto(True, icon)
        self.geometry("1000x600")
        self.minsize(600, 600)
        #self.current_directory=os.getcwd()
        Grid.rowconfigure(self, 0, weight=1) #mention that we have one row 
        Grid.columnconfigure(self, 1, weight=1)
        #Grid.columnconfigure(self, 1, weight=3)
        #393e46
        Side_Menu = Frame(self, bg="#49A")
        Grid.rowconfigure(Side_Menu, (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15), weight=1)
        Side_Menu.grid(row=0,column=0,sticky="NSEW")
        self.pnr_icon = ImageTk.PhotoImage(Image.open(r'/vols/sondrel_training/users/Ilham.Elyoubi/timing_tracker/lib/icons/pnr.png').resize((80,80)).convert('RGBA')) #Change : define PNR icon
        self.sta_icon = ImageTk.PhotoImage(Image.open(r'/vols/sondrel_training/users/Ilham.Elyoubi/timing_tracker/lib/icons/sta.png').resize((80,80)).convert('RGBA')) #Change : define STA icon

        # B_PNR = self.create_button(Side_Menu,'PNR', self.pnr, self.pnr_icon)
        # B_STA = self.create_button(Side_Menu,'STA', self.sta, self.sta_icon)
        self.B_PNR = self.create_button_icon(Side_Menu, self.switch_pnr_button,"PNR")
        self.B_STA = self.create_button_icon(Side_Menu, self.switch_sta_button,"STA")
        #49A
        
        
        self.main_frame = Frame(self, bg="white")
        self.main_frame.grid(row=0,column=1,sticky="NSWE")
        Title_Lab = Label(self.main_frame, text='Timing Tracker Tool',font=('Verdana', 25, 'bold'),bg="white",fg="#49A",padx=4,pady=10)
        Title_Lab.grid(row=0, column=0, sticky=tk.N+tk.E+tk.S+tk.W)
        # self.main_frame.grid(row=0,column=1,rowspan=2,sticky=NW+SW+NE) #NW will be considered from the end of the first one
        # Grid.rowconfigure(self.main_frame, 0, weight=1)
        Grid.rowconfigure(self.main_frame, 0, weight=1) #we indicate that the label should take the whole space in the grid vertically 
        Grid.columnconfigure(self.main_frame, 0, weight=1) #so the frame in the first row could fit the width of the frame main_frame
        self.frame1 = Frame(self.main_frame,relief=SUNKEN)
        # Grid.columnconfigure(self.frame1, (0,1), weight=1)
        # self.blockInfo_frame()
        #insert_frame(dict1)
        #create the pnr_frame containing the tabs of pnr
        self.frame2 = Frame(self.main_frame, relief=SUNKEN)
        #self.frame2.grid(row=1,column=0,sticky="nsew")
        # create the  notebook
        self.notebook = ttk.Notebook(self.frame2)
        self.tab1_created = False
        self.tab2_created = False
        self.tab3_created = False
        self.treeview_filled = False
        
        # where we haveinserted the scrollbar that scroll all the treeviews (canvas scroll)
        # create the  frame container and tree of the second and third tab
        self.frame4 = ttk.Labelframe(self.notebook, relief=SUNKEN, text=' ',height=110)
        self.empty_tv=self.create_violated_treeview(self.frame4)
        # tab 3 that display the detailed report
        self.frame5 = ttk.Frame(self.notebook, relief=SUNKEN)
        # Add a Scrollbar(horizontal) to the text widget displqying the detailed report 
        self.hscroll=Scrollbar(self.frame5, orient='horizontal')
        self.hscroll.pack(side=BOTTOM, fill='x')

        # Add a Scrollbar(vertical) to the text widget displqying the detailed report 
        self.vscroll=Scrollbar(self.frame5, orient='vertical')
        self.vscroll.pack(side=RIGHT, fill='y')
        
        #create  a text widget where the detailed report will be displayed
        self.report = Text(self.frame5,height=110, wrap=NONE,xscrollcommand=self.hscroll.set,yscrollcommand=self.vscroll.set)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_selected)

    
    def pnr(self):
    
        self.main_frame.grid(row=0,column=1,rowspan=2,sticky=NW+SW+NE) #NW will be considered from the end of the first one
        Grid.rowconfigure(self.main_frame, 0, weight=1)
        Grid.rowconfigure(self.main_frame, 1, weight=7)
        Grid.columnconfigure(self.main_frame, 0, weight=1)
        Grid.columnconfigure(self.frame1,(0,1,2,3,4,5,6,7), weight=1)
        self.blockInfo_frame()
        self.frame2.grid(row=1,column=0,sticky="nsew")
        #self.notebook = ttk.Notebook(self.frame2)
        self.notebook.pack(expand=1, fill=BOTH,pady=0)
        summary_frame = self.create_tab1()  # the frame of the summary tab
        # where we haveinserted the scrollbar that scroll all the treeviews
        self.canvas_scroll = VerticalScrolledFrame(summary_frame)
        if self.tab2_created == True : #Change : remove tab2 before creating a new one
            # for i in self.empty_tv.get_children():
            #     self.empty_tv.delete(i)
            self.notebook.forget(self.frame4)
            self.tab2_created = False
        if self.tab3_created == True : #Change : remove tab2 before creating a new one
            self.notebook.forget(self.frame5)
            self.report.delete('1.0', END)
            self.tab3_created = False
        #self.clear_win_pack(self.notebook)
        #self.clear_win(self.main_frame)
        
        self.get_pnr_violations()
        
    def sta(self):
        
        # print(self.tab2_created)
        # print(self.tab3_created)
        self.main_frame.grid(row=0,column=1,rowspan=2,sticky=NW+SW+NE) #NW will be considered from the end of the first one
        #
        Grid.rowconfigure(self.main_frame, 0, weight=1)
        Grid.rowconfigure(self.main_frame, 1, weight=7)
        Grid.columnconfigure(self.main_frame, 0, weight=1)
        Grid.columnconfigure(self.frame1, (0,1,2,3,4,5,6,7), weight=1)
        self.blockInfo_frame()
        self.frame2.grid(row=1,column=0,sticky="nsew")
        #self.notebook = ttk.Notebook(self.frame2)
        self.notebook.pack(expand=1, fill=BOTH,pady=0)
        summary_frame = self.create_tab1()  # the frame of the summary tab
        # where we haveinserted the scrollbar that scroll all the treeviews
        self.canvas_scroll = VerticalScrolledFrame(summary_frame)
        if self.tab2_created == True : #Change : remove tab2 before creating a new one
            # for i in self.empty_tv.get_children():
            #     self.empty_tv.delete(i)
            self.notebook.forget(self.frame4)
            self.tab2_created = False
        if self.tab3_created == True : #Change : remove tab3 before creating a new one
            self.notebook.forget(self.frame5)
            self.report.delete('1.0', END)
            self.tab3_created = False
        self.get_sta_violations()

    def create_treeview_tab1( self,frame_tree, jdata):
        # print(jdata)
        #df = pd.DataFrame(jdata,index=['clk', 'REGOUT', 'REGIN','Total'])
        df = pd.DataFrame.from_dict(jdata, orient="index")
        # create a vertical treeview scrollbar
        yscroll = ttk.Scrollbar(frame_tree, orient=VERTICAL)
        yscroll.pack(side="right", fill=Y)
        # create a tree view
        tree_view = ttk.Treeview(
            frame_tree,height=4,yscrollcommand=yscroll.set,style="mystyle.Treeview")
        # tree_view.pack_forget()
        tree_view.pack(pady=5, expand=True, fill="both")
        # configure the vertical scrollbar
        yscroll.config(command=tree_view.yview)
        #cols = list(df.columns)
        cols = ['WNS(ns)', 'TNS(ns)', '#PATHS', '#NVP >100ps', '#NVP >50ps', '#NVP >0ps']
        tree_view["columns"] = cols
        # print(cols[1])
        for i in cols:
            # print(i)
            tree_view.column(i, anchor="center")
            tree_view.heading(i, text=i, anchor='center')
        for index, row in df.iterrows():
            # print(index)
            # print(list(row))
            tree_view.insert("", 'end', text=index, values=list(row))
        return tree_view
    def blockInfo_frame(self):
        #self.frame1.grid(row=0,column=0,rowspan=3,columnspan=2,sticky=tk.N,padx=10,pady=5,ipady=10)
        self.frame1.grid(row=0,column=0,sticky=tk.N,padx=10,pady=5,ipady=10)
        dict1 = self.get_block_info()
        self.insert_frame(dict1)
    
    def select1(self):
        if 'Violated endpoint ' in [self.notebook.tab(i, option="text") for i in self.notebook.tabs()]:
            # self.clear_win(self.frame4)
            self.clear_win_pack(self.frame4)
            self.notebook.forget(self.frame4)
            #self.notebook.forget(self.frame5)
            self.notebook.select(1)
        self.create_tab2()
    def create_violated_treeview(self, frame_tree):
        
        # create a vertical treeview scrollbar
        yscroll = ttk.Scrollbar(frame_tree, orient=VERTICAL)
        yscroll.pack(side="right", fill=Y)

        # create Horizontal treeview scrollbar
        xscroll = ttk.Scrollbar(frame_tree, orient=HORIZONTAL)
        xscroll.pack(side="bottom",fill=X)
        # create a tree view
        tree_view = ttk.Treeview(frame_tree,height=110, columns=(
            'Slack', 'Scenario', 'endpoint'),#show='headings', 
            yscrollcommand=yscroll.set,xscrollcommand=xscroll.set,style="mystyle.Treeview")
        
        tree_view.heading('#1', text="Slack",anchor="center")
        tree_view.heading('#2', text="Scenario",anchor="center")
        tree_view.heading('#3', text="endpoint")
        tree_view.column('#0', stretch=NO, minwidth=0, width=0)
        tree_view.column('#1', minwidth=0, stretch=NO,width=70)  # width=200
        tree_view.column('#2', minwidth=0, stretch=NO,width=240)  # width=200
        tree_view.column('#3', minwidth=0)  # width=300
        # configure the vertical scrollbar
        yscroll.config(command=tree_view.yview)
        # configure the Horizontal scrollbar
        xscroll.config(command=tree_view.xview)
        return tree_view

    def violated_points_table(self,tree_view, csvFile):
        
        with open(csvFile) as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                Slack = row['Slack']
                Scenario = row['Scenario']
                Endpoint = row['Endpoint']
                tree_view.insert("", 'end', values=(Slack, Scenario, Endpoint))
            
        
        # path=self.get_record(treeview)
        # handle the click in a record
        #self.frame4 = ttk.LabelFrame(self.notebook,relief=SUNKEN,text=path)
    def get_block_info(self):
        filename = os.getcwd()+"/"+"helium_config.tcl"
        # initializing dictionary
        Block_name = {'Block_name': '', 'Rtl_release': '', 'Tracker_date': ''}
        with open(filename) as f:
            lines = f.read()
            design_name = [x.group(1) for x in re.finditer(
                r'.*design_name (.*)', lines)][0]
            release = [x.group(1) for x in re.finditer(
                r'.*rtl_release "(.*)"', lines)][0]
            values = [design_name, release,
                      '-'.join(str(datetime.now()).split(' ')).split('.')[0]]
        return (dict(zip(Block_name, values)))
    def insert_frame(self,dict1):
        # frame1,frame2=self.create_frames()
        for i, key, value in zip(range(len(dict1)), dict1.keys(), dict1.values()):
            # rowspan attribute let us print one thing in 2,3.. rows
            Label(self.frame1, text=key,bg="white",fg="black",font=('Verdana', 12, 'bold')).grid(
                row=i, column=3,pady=6)
            Label(self.frame1, text=value,bg="white",fg="black",font=('Verdana', 12,'bold')).grid(
                row=i, column=4,pady=6,sticky=N)
    def create_tab1(self):
        if self.tab1_created == True : #Change : remove tab1 before creating a new one
            self.notebook.forget(self.tab1)
            self.tab1_created = False
        
        self.tab1 = ttk.Frame(self.notebook, relief=SUNKEN)  # '''width=700, height=500''')
        self.notebook.add(self.tab1, text='Summary')
        self.tab1_created = True
        return self.tab1

    def create_tab2(self):
        if self.tab2_created == True : #Change : remove tab2 before creating a new one
            self.notebook.forget(self.frame4)
            self.clear_win_pack(self.frame4)
            #self.notebook.forget(self.frame5)
            for i in self.empty_tv.get_children():
                self.empty_tv.delete(i)
            self.tab2_created = False
        
        #self.frame4 = ttk.Labelframe(self.notebook, relief=SUNKEN, text=' ') # '''width=700, height=500''')
        self.notebook.add(self.frame4, text='Violated endpoint ')
        self.notebook.select(1)
        self.tab2_created = True
        #return self.frame4
    def create_tab3(self):
        if self.tab3_created == True : #Change : remove tab1 before creating a new one
            self.notebook.forget(self.frame5)
            #self.report.delete('1.0', END)
            self.tab3_created = False
        
        #self.frame4 = ttk.Labelframe(self.notebook, relief=SUNKEN, text=' ') # '''width=700, height=500''')
        self.notebook.add(self.frame5, text='Origin report')
        self.notebook.select(2)
        self.tab3_created = True
    def clean_notebook(self):
        # if self.tab1_created == True : #Change : remove tab1 before creating a new one
        #     self.notebook.forget(self.tab1)
        #     self.tab1_created = False 
        if self.tab2_created == True : #Change : remove tab1 before creating a new one
            self.notebook.forget(self.frame4)
            self.tab_created = False 
        if self.tab3_created == True : #Change : remove tab1 before creating a new one
            self.notebook.forget(self.frame5)
            self.tab3_created = False
    def set_style(self):
        # define the style of the tab for example (doesn't work at the moment
        style = ttk.Style()
        style .theme_use("default")  # set the theme
        style.map('TNotebook.Tab', background=[('selected', "#ADD8E6")])
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Arial', 11)) # Modify the font of the body
        style.configure("Treeview.Heading", foreground="white",background="#4682B4",font=('Arial',13,'bold'))
    def clear_win(self,frame):
        for wid in frame.winfo_children():
            wid.grid_forget()
    def clear_win_pack(self,frame):
        for wid in frame.winfo_children():
            #print(wid)
            wid.pack_forget()
    #the function below doesn't work
    def forget_notebook_tabs(self):
        self.notebook.forget(self.summary_frame)
        self.notebook.forget(self.frame4)
        self.notebook.forget(self.frame5)
    def destroy_widgets(self,frame):
        for wid in frame.winfo_children():
            #print(wid)
            wid.destroy()
    def show_frame(self):
        self.frame2.grid_forget()
        self.frame1.grid(row=0,column=0,rowspan=3,columnspan=2,sticky="nsew", padx=15, pady=20)
        self.frame2.grid(row=1,column=0,sticky="nsew")
    def hide_frame(self,frame):
        # This will remove the widget from toplevel
        frame.grid_forget()
        self.frame2.grid(row=0,column=0,sticky="nsew")
    def on_tab_selected(self,event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        # print(tab_text)
        if tab_text == "Summary":
            self.show_frame()
        else:
            self.hide_frame(self.frame1)
    def create_button(self,cont, txt, cmd):
        
        def ButtonEffect(b, el):
            if el == 0:
                b['background'] = "white"
            else:
                b['background'] = "lightblue"
        #49A
        Bt = Button(cont,text=txt, bg="lightblue", font=(
            'Verdana', 13, 'bold'), fg='black', relief='sunken',height=8,command=cmd)#height=6,compound=TOP
        #Bt.config(image=logo, compound=LEFT)
        # image=photoimage,compound="top"
        Bt.pack(fill='x',pady=20,anchor=tk.CENTER)
        # if bd:
        #     Frame(cont, relief=GROOVE, bd=2, width=150).pack(fill='x', padx=10)
        Bt.bind("<Enter>", lambda event: ButtonEffect(Bt, 0))
        Bt.bind("<Leave>", lambda event: ButtonEffect(Bt, 1))
        return Bt
    global is_PNR_ON
    global is_STA_ON
    is_PNR_ON=False
    is_STA_ON=False
    
    def create_button_icon(self,cont, cmd,txt):
        
        self.i=self.i+1
        # def ButtonEffect(b, el):
        #     if el == 0:
        #         b['background'] = "white"
        #     else:
        #         b['background'] = "lightblue"
        #49A
        Bt = Button(cont,text=txt, bg="lightblue", font=(
            'Verdana', 13, 'bold'), fg='black', relief='sunken',command=cmd)#,image=logo)
        #Bt.config(image=logo, compound=LEFT)
        # image=photoimage,compound="top"
        #Bt.pack(fill=Y,pady=10,anchor=tk.CENTER) #changing the pady here changes the space between the buttons created 
        Bt.grid(column=0,row=(self.i)+4)
        return Bt
    def switch_pnr_button(self):
        global is_PNR_ON
        if is_PNR_ON :
            self.B_PNR.config(bg="lightblue")
            self.B_STA.config(bg="white") #lightblue is the color by default
            is_PNR_ON=False
        else:
            self.B_STA.config(bg="lightblue")
            self.B_PNR.config(bg="white")
            is_PNR_ON=False
        self.pnr()

    def switch_sta_button(self):
        global is_STA_ON
        if is_STA_ON :
            self.B_STA.config(bg="lightblue")
            self.B_PNR.config(bg="white") #lightblue is the color by default
            is_STA_ON=False
        else:
            self.B_PNR.config(bg="lightblue")
            self.B_STA.config(bg="white")
            is_STA_ON=False
        self.sta()
    def get_pnr_violations(self):
        all_steps_list =["chip_finish.report_qor","route_opt.report_qor","route_auto.report_qor","clock_opt_opto.report_qor",
        "clock_opt_cts.report_qor","place_opt.report_qor","insert_dft.report_qor","compile.report_qor"]
        
        PNR_reports_directory= os.getcwd()+"/"+"report"
        pnr_reports=[]
        for extension in ("*.report_qor", "*endpoint*"):
            pnr_reports.extend(glob.glob(PNR_reports_directory+"/"+extension))
        pnr_reports_ordered = []
        for report in all_steps_list :
            
            if (PNR_reports_directory+"/"+report) in pnr_reports:
                pnr_reports_ordered.append((PNR_reports_directory+"/"+report))

        def create_treeview_tab(canvas_scroll, fct, qor_file, endpoints_file, jsonFile, label):
            # create the frames for the trees :the number of the trees that will be created should be set automatically depending on the number of steps and metrics
            # text must be filled automatically
            tree = ttk.LabelFrame(canvas_scroll.frame,
                                  relief=SUNKEN, text=label)
            tree.pack(fill=BOTH, expand=True)
            # print(jsonFile)

            fct(qor_file, endpoints_file, jsonFile)
            if os.path.exists(os.getcwd()+"/"+jsonFile):
            # print("hello")
                jsonfile = open(jsonFile, "r")
                jsonContent = jsonfile.read()
                # convert the json object to a dict
                jdata = json.loads(jsonContent)
                treeview = self.create_treeview_tab1(tree, jdata)
            # treeview.pack(pady=5,expand=True,fill="both")
                def on_tree_select(event):
                    #print("selected items:")
                    selected = treeview.focus()
                    # get record values
                    values = list(treeview.item(selected, 'values'))
                    valuess = []
                    #valuess.append([float(value) for value in values])
                    for value in values:
                        #value = float(value)
                        valuess.append(float(value))
                    # get the pathgroup based on the values
                    self.pathgroup = list(jdata.keys())[
                        list(jdata.values()).index(valuess)]
                    #self.select1()
                    self.frame4.configure(
                        text=tree.cget("text")+":"+self.pathgroup)
                    self.step = [x.group(1) for x in re.finditer(
                        r'(.*):(.*)', tree.cget("text"))][0]
                    # print(step)
                    # if self.treeview_filled==True:
                    for i in self.empty_tv.get_children():
                        self.empty_tv.delete(i)
                     
                # self.empty_tv=self.create_violated_treeview(self.frame4)
                # self.treeview_filled==True

                    #endpoint_file = f"{PNR_reports_directory}/{self.step}.report_endpoint.rpt"
                    csvfile = self.step+'Violating_endpoint'+'_'+self.pathgroup+'.csv'
                    pnr_functions.convert_violated_endpoints_to_csv(
                        endpoints_file, self.pathgroup, csvfile)
                    
                    
                    if 'Violated endpoint ' in [self.notebook.tab(i, option="text") for i in self.notebook.tabs()]:
                        # self.clear_win(self.frame4)
                        #self.notebook.forget(self.frame4)
                        self.clear_win_pack(self.frame4)
                        #self.notebook.forget(self.frame5)
                        for i in self.empty_tv.get_children():
                            self.empty_tv.delete(i)

                        self.violated_points_table(self.empty_tv, csvfile)
                        # create a vertical treeview scrollbar
                        yscroll = ttk.Scrollbar(self.frame4, orient=VERTICAL)
                        yscroll.pack(side="right", fill=Y)
                        # create Horizontal treeview scrollbar
                        xscroll = ttk.Scrollbar(self.frame4, orient=HORIZONTAL)
                        xscroll.pack(side="bottom",fill=X)

                        self.empty_tv.pack(expand=1,fill="both")
                        # configure the vertical scrollbar
                        yscroll.config(command=self.empty_tv.yview)
                        # configure the Horizontal scrollbar
                        xscroll.config(command=self.empty_tv.xview)
                        
                        self.notebook.select(1)
                    else :
                        self.create_tab2()
                        self.violated_points_table(self.empty_tv, csvfile)
                        self.empty_tv.pack(expand=1,fill="both")

                    def on_tree_select1(step):
        
                        #self.report.delete('1.0', END)
                        #print("selected items:")
                        selected = self.empty_tv.focus()
                        # get record values
                        values = list(self.empty_tv.item(selected, 'values'))
                        if 'Origin report' in [self.notebook.tab(i, option="text") for i in self.notebook.tabs()]:
                            self.notebook.forget(self.frame5)
                            self.report.delete('1.0', END)
                            #self.notebook.select(2)
                        # handle the click in a record
                        #self.create_tab3()
                        self.notebook.add(self.frame5, text='Origin report')
                        
                        self.notebook.select(2)
                        self.tab3_created = True
                        
                        #self.report = Text(self.frame5,height=160,xscrollcommand=self.hscroll.set)
                        
                        #step=[x.group(1) for x in re.finditer(r'(.*):(.*):(.*)',self.frame4.cget("text"))][0]
                        path_delay = self.frame4.cget("text")

                        if path_delay .__contains__("setup"):

                            #detailed_self.report_file = f"{PNR_reports_directory}/{self.step}.report_timing.max"
                            detailed_report_file = f"{PNR_reports_directory}/{self.step}.report_timing.max"

                        else:

                            detailed_report_file = f"{PNR_reports_directory}/{self.step}.report_timing.min"

                        if os.path.exists(detailed_report_file)==True:
                            detailed_report =pnr_functions.get_start_and_stop_index_basedon_endpoint_index(detailed_report_file,values[2])

                            if detailed_report is None :
                                #print("hello None")
                                self.notebook.forget(self.frame5)
                                self.notebook.select(1)
                                self.tab3_created=False
                                messagebox.showinfo("Message", "No detailed report")

                            else :
                                #print("hello report")
                                self.report.insert(INSERT, detailed_report)
                                self.report.pack(fill="both", expand=TRUE)
                                self.hscroll.config(command=self.report.xview)
                                self.vscroll.config(command=self.report.yview)
                        else :
                            self.notebook.forget(self.frame5)
                            self.tab3_created=False
                            messagebox.showinfo("Message", "No detailed report_generated for pnr")
                            self.notebook.forget(self.frame4)
                            self.tab2_created=False
                            self.notebook.select(0)


                    self.empty_tv.bind("<<TreeviewSelect>>", lambda event,
                                    a=self.step, : on_tree_select1(a))
                treeview.bind("<<TreeviewSelect>>", on_tree_select)
            
        if len(pnr_reports_ordered) == 0:
            #print("hello")
            messagebox.showerror("Error", "No pnr_reports_yet")
            self.destroy()
        else:
            for file in pnr_reports_ordered:
                #print("Hello I'm in the for loop of pnr reports")
                if file.endswith(".report_qor"):
                    qor_file = file
                    # print(qor_file)
                    # Get just the file name without the .report_qor extension
                    fname = Path(qor_file).stem
                    endpoints_filenames= glob.glob(PNR_reports_directory+"/"+fname+"*endpoint*") 
                    if len(endpoints_filenames)!=0:
                        setup_endpoints_file = pnr_functions.get_setup_and_hold_endpoints_file(endpoints_filenames)[0] #either I'll get1 or 2 (hold and setup endpoints have the same name)
                        hold_endpoints_file=pnr_functions.get_setup_and_hold_endpoints_file(endpoints_filenames)[1]
                        if (os.path.exists(qor_file) == True) and (setup_endpoints_file!=None):
                            
                            #print("the files are existing")
                            create_treeview_tab(self.canvas_scroll, pnr_functions.store_setup_metrics,
                                                    qor_file, setup_endpoints_file, fname+"_setup_metrics.json", fname+":setup")
                        else:
                            continue
                        if (os.path.exists(qor_file) == True) and (hold_endpoints_file!=None):  
                            create_treeview_tab(self.canvas_scroll,pnr_functions.store_hold_metrics,qor_file,hold_endpoints_file,fname+"_hold_metrics.json",fname+":hold")
                        else:
                            continue
    def get_sta_violations(self):
        

        def create_sta_treeviews(canvas_scroll,endpoints_file):
            
            # create the frames for the trees :the number of the trees that will be created should be set automatically depending on the number of steps and metrics
            # text must be filled automatically
            tree_setup = ttk.LabelFrame(
                self.canvas_scroll.frame, relief=SUNKEN, text="sta:setup")
            tree_setup.pack(fill=BOTH, expand=True)
            jdata_setup = json.loads(open("sta_setup.json", "r").read())
            jdata_hold = json.loads(open("sta_hold.json", "r").read())
            tv_setup = self.create_treeview_tab1(tree_setup, jdata_setup)

            # text must be filled automatically
            tree_hold = ttk.LabelFrame(
                self.canvas_scroll.frame, relief=SUNKEN, text="sta:hold")
            tree_hold.pack(fill=BOTH, expand=True)
            tv_hold = self.create_treeview_tab1(tree_hold, jdata_hold)

            def on_tree_select(tree_view, jdata, frame_tree):
    
                #print("selected items:")
                selected = tree_view.focus()
                # get record values
                values = list(tree_view.item(selected, 'values'))
                valuess = []
                for value in values:
                    #value = float(value)
                    valuess.append(float(value))
                #print(valuess)
                # get the pathgroup based on the values
                self.pathgroup = list(jdata.keys())[
                    list(jdata.values()).index(valuess)]
                #self.select1()
                self.frame4.configure(
                    text=frame_tree.cget("text")+":"+self.pathgroup)
                delay_type = [x.group(2) for x in re.finditer(
                    r'(.*):(.*)', frame_tree.cget("text"))][0]
                for i in self.empty_tv.get_children():
                    self.empty_tv.delete(i)
                csvfile = 'sta_Violating_endpoint'+'_'+delay_type+'_'+self.pathgroup+'.csv'
                # self.empty_tv=self.create_violated_treeview(self.frame4)
                sta_functions.convert_violated_endpoints_to_csv(
                    self.endpoints_files,delay_type, self.pathgroup, csvfile)
                
                if 'Violated endpoint ' in [self.notebook.tab(i, option="text") for i in self.notebook.tabs()]:
                    self.clear_win_pack(self.frame4)
                    #self.notebook.forget(self.frame5)
                    for i in self.empty_tv.get_children():
                        self.empty_tv.delete(i)
                    self.violated_points_table(self.empty_tv, csvfile)
                    
                    
                    xscroll = ttk.Scrollbar(self.frame4, orient=HORIZONTAL)# create a vertical treeview scrollbar
                    xscroll.pack(side="bottom",fill=X)

                    yscroll = ttk.Scrollbar(self.frame4, orient=VERTICAL)# create a horizontal treeview scrollbar
                    yscroll.pack(side="right", fill=Y)
                    self.empty_tv.pack(expand=1,fill="both")
                    self.notebook.select(1)
                    # configure the vertical scrollbar
                    yscroll.config(command=self.empty_tv.yview)
                    # configure the Horizontal scrollbar
                    xscroll.config(command=self.empty_tv.xview)
                    
                else :
                    
                    self.create_tab2()
                    self.violated_points_table(self.empty_tv, csvfile)
                    
                    self.empty_tv.pack(expand=True, fill="both")
                    
                  
                    
                    # self.notebook.add(self.frame4, text='Violated endpoint ')
                    # self.notebook.select(1)
                    # self.tab2_created == True
                    
                #self.self.violated_tv = self.violated_points_table(self.frame4, csvfile)

                def on_tree_select1(event):
                    selected = self.empty_tv.focus()
                    # get record values
                    values = list(self.empty_tv.item(selected, 'values'))
                    if 'Origin report' in [self.notebook.tab(i, option="text") for i in self.notebook.tabs()]:
                        self.notebook.forget(self.frame5)
                        self.report.delete('1.0', END)
                    # handle the click in a record
                    #self.create_tab3()
                    self.notebook.add(self.frame5, text='Origin report')
                    self.notebook.select(2)
                    self.tab3_created = True
                
                    #self.report = Text(self.frame5, wrap=WORD,xscrollcommand=self.hscroll.set)
                    #step=[x.group(1) for x in re.finditer(r'(.*):(.*):(.*)',self.frame4.cget("text"))][0]
                    path_delay = self.frame4.cget("text")

                    if path_delay .__contains__("setup"):
                        detailed_report_file = self.STA_reports_directory + \
                            "/reports/sta_si_merged_dpmax_all_paths.rpt"

                    else:
                        detailed_report_file = self.STA_reports_directory + \
                            "/reports/sta_si_merged_dpmin_all_paths.rpt"

                    if os.path.exists(detailed_report_file) == True :
                        detailed_report =pnr_functions.get_start_and_stop_index_basedon_endpoint_index(detailed_report_file,values[2])
                        
                    
                        if detailed_report is None:
                            #print("hello None")
                            self.notebook.forget(self.frame5)
                            self.notebook.select(1)
                            self.tab3_created=False
                            messagebox.showinfo("Message", "No detailed report")

                        else :
                            #print("hello report")
                            self.report.insert(INSERT, detailed_report)
                            self.report.pack(fill="both", expand=TRUE)
                            self.hscroll.config(command=self.report.xview)
                            self.vscroll.config(command=self.report.yview)

                    else :
                        self.notebook.forget(self.frame5)
                        self.tab3_created=False
                        messagebox.showinfo("Message", "No detailed report_generated for this step")
                        self.notebook.forget(self.frame4)
                        self.tab2_created=False
                        self.notebook.select(0)
                        

                self.empty_tv.bind("<<TreeviewSelect>>", on_tree_select1)
            
            tv_setup.bind("<<TreeviewSelect>>", lambda event, a=tv_setup,b=jdata_setup, c=tree_setup: on_tree_select(a, b, c))
            tv_hold.bind("<<TreeviewSelect>>", lambda event, a=tv_hold,b=jdata_hold, c=tree_hold: on_tree_select(a, b, c))
        
        if os.path.exists(os.getcwd()+"/sta_setup.json") and os.path.exists(os.getcwd()+"/sta_hold.json"):

            create_sta_treeviews(self.canvas_scroll, self.endpoints_files)

        else:

            messagebox.showinfo("Message", "No sta report")
def main():
    app = App()
    app.set_style()
    app.mainloop()

if __name__ == '__main__':
    main()
