###This file contains the tkinter interface - the front end of the program ###

#Import required modules
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import os
from tkinter.filedialog import askopenfilename,askdirectory,asksaveasfilename
#global variables and methods
source=os.path.dirname(os.path.realpath(__file__))

#Create the Main Class that provide the framework for the interface
class create_GUI_from_df():#new class inheriting from tk.Tk

	def __init__(self,master,config,in_progress_df=''):#Class initilizing method (Happens First)	
		self.command_real=False
		config['frames']=config['frames'].fillna('')
		config['widgets']=config['widgets'].fillna('')
		if isinstance(in_progress_df,str):
			self.command_real=True
			in_progress_df=config
		else:
			in_progress_df['frames']=in_progress_df['frames'].fillna('')
			in_progress_df['widgets']=in_progress_df['widgets'].fillna('')
		self.master=master
		#print(config['frames'])
		#Create the frames
		for name,row in config['frames'].iterrows():
			if row.loc['frame_type']=='window':
				master.frame_dict['window'][name]=master
				try:
					for x in str(row.loc['adjustable_rows']).split(','):
						master.grid_rowconfigure(int(round(float(x))),weight=1)
				except:
					pass
				try:
					for x in str(row.loc['adjustable_columns']).split(','):
						master.grid_columnconfigure(int(round(float(x))),weight=1)
				except:
					pass
			elif row.loc['frame_type']=='base' or row.loc['frame_type']=='standard':
				master.frame_dict[row.loc['frame_type']][name]=tk.Frame(master.frame_dict[in_progress_df['frames'].loc[row.loc['parent_frame'],'frame_type']][row.loc['parent_frame']],highlightbackground='black',highlightthickness=1)
				master.frame_dict[row.loc['frame_type']][name].grid(row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column']))),sticky=row.loc['sticky']
				,rowspan=int(round(float(row.loc['rowspan']))),columnspan=int(round(float(row.loc['columnspan']))),padx=int(round(float(row.loc['padx']))),pady=int(round(float(row.loc['pady']))))
				try:	
					for x in str(row.loc['adjustable_rows']).split(','):
						master.frame_dict[row.loc['frame_type']][name].grid_rowconfigure(int(round(float(x))),weight=1)
				except:
					pass
				try:
					for x in str(row.loc['adjustable_columns']).split(','):
						master.frame_dict[row.loc['frame_type']][name].grid_columnconfigure(int(round(float(x))),weight=1)
				except:
					pass
			elif row.loc['frame_type']=='embedded_changeable':
				master.frame_dict['change_option'][name]={}
				master.frame_dict['embedded_changeable'][name]=tk.Frame(master.frame_dict[in_progress_df['frames'].loc[row.loc['parent_frame'],'frame_type']][row.loc['parent_frame']],highlightbackground='black',highlightthickness=1)
				master.frame_dict['embedded_changeable'][name].grid(row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column']))),sticky=row.loc['sticky']
				,rowspan=int(round(float(row.loc['rowspan']))),columnspan=int(round(float(row.loc['columnspan']))),padx=int(round(float(row.loc['padx']))),pady=int(round(float(row.loc['pady']))))
				try:
					for x in str(row.loc['adjustable_rows']).split(','):
						master.frame_dict['embedded_changeable'][name].grid_rowconfigure(int(round(float(x))),weight=1)
				except:
					pass
				try:
					for x in str(row.loc['adjustable_columns']).split(','):
						master.frame_dict['embedded_changeable'][name].grid_columnconfigure(int(round(float(x))),weight=1)
				except:
					pass
				frames_found = in_progress_df['frames'].loc[in_progress_df['frames']['parent_frame']==name]
				#print(name,frames_found)
				if not frames_found.empty:
					for change_name,change_row in frames_found.iterrows():
						master.frame_dict['change_option'][name][change_name]=tk.Frame(master.frame_dict[in_progress_df['frames'].loc[change_row.loc['parent_frame'],'frame_type']][change_row.loc['parent_frame']])
						master.frame_dict['change_option'][name][change_name].grid(row=int(round(float(change_row.loc['row']))),column=int(round(float(change_row.loc['column']))),sticky=change_row.loc['sticky']
						,rowspan=int(round(float(change_row.loc['rowspan']))),columnspan=int(round(float(change_row.loc['columnspan']))),padx=int(round(float(change_row.loc['padx']))),pady=int(round(float(change_row.loc['pady']))))
						try:
							for x in str(change_row.loc['adjustable_rows']).split(','):
								master.frame_dict['change_option'][name][change_name].grid_rowconfigure(int(round(float(x))),weight=1)
						except:
							pass
						try:
							for x in str(change_row.loc['adjustable_columns']).split(','):
								master.frame_dict['change_option'][name][change_name].grid_columnconfigure(int(round(float(x))),weight=1)
						except:
							pass
					#print(master.frame_dict['change_option'][name].items())
					list(master.frame_dict['change_option'][name].values())[0].tkraise()
		
		#create the widgets
		
		
		widget_creator={'label':'self.widget_label(parent_frame,master.widget_dict[frame_name][widget_type],name,row)',
				'button':'self.widget_button(parent_frame,master.widget_dict[frame_name][widget_type],name,row)',
				'entry':'self.widget_entry(parent_frame,master.widget_dict[frame_name][widget_type],name,row)',
				'optionmenu':'self.widget_optionmenu(parent_frame,master.widget_dict[frame_name][widget_type],name,row)',
				'text':'self.widget_text(parent_frame,master.widget_dict[frame_name][widget_type],name,row)',
				'listbox':'self.widget_listbox(parent_frame,master.widget_dict[frame_name][widget_type],name,row)',
				'spinbox':'self.widget_spinbox(parent_frame,master.widget_dict[frame_name][widget_type],name,row)',
				'checkbutton':'self.widget_checkbutton(parent_frame,master.widget_dict[frame_name][widget_type],name,row)'
						}
		for x in in_progress_df['frames'].index:
			master.widget_dict[x]={'label':{},'button':{},'entry':{},'optionmenu':{},'text':{},'listbox':{},'spinbox':{},'checkbutton':{}}
		
		
		#create a menubar
		if len(master.frame_dict['base'].keys())>1:
			master.frame_select=tk.StringVar()
			list_base_frames=list(master.frame_dict['base'].keys())
			list_base_frames.sort()
			master.widget_dict['window']['optionmenu']['menubar']=ttk.OptionMenu(master,master.frame_select,list_base_frames[0],*list_base_frames,command=lambda x:master.frame_dict['base'][x].tkraise())
			master.widget_dict['window']['optionmenu']['menubar'].grid(row=999,column=0,sticky='NE')
			master.frame_dict['base'][list_base_frames[0]].tkraise()
		
		
		
		for name,row in config['widgets'].iterrows():
			widget_type=row.loc['widget_type']
			frame_name=row.loc['parent_frame']
			if in_progress_df['frames'].loc[frame_name,'frame_type']=='change_option':
				parent_frame=master.frame_dict[in_progress_df['frames'].loc[frame_name,'frame_type']][in_progress_df['frames'].loc[frame_name,'parent_frame']][frame_name]
			else:
				parent_frame=master.frame_dict[in_progress_df['frames'].loc[frame_name,'frame_type']][frame_name]
			eval(widget_creator[widget_type])
		

	def widget_label(self,container,dict,name,row):
		if name in dict.keys():
			dict[name].destroy()
		dict[name]=tk.Label(container,text=row.loc['text'],wraplength=175,justify='center')
		dict[name].grid(row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column']))),rowspan=int(round(float(row.loc['rowspan'])))
		,columnspan=int(round(float(row.loc['columnspan']))),padx=int(round(float(row.loc['padx']))),pady=int(round(float(row.loc['pady'])))
			,sticky=row.loc['sticky'])
	def widget_button(self,container,dict,name,row):
		if name in dict.keys():
			dict[name].destroy()
		if 'lambda' not in row.loc['command']:
			command_text=('self.master.'+row.loc['command'] if self.command_real else 'self.master.do_nothing')
		else:
			command_text=(row.loc['command'].replace('self','self.master') if self.command_real else 'self.master.do_nothing')
			#print(round(float(command_text)
		dict[name]=ttk.Button(container,text=row.loc['text'],command=eval(command_text))
		dict[name].grid(row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column']))),rowspan=int(round(float(row.loc['rowspan'])))
		,columnspan=int(round(float(row.loc['columnspan']))),padx=int(round(float(row.loc['padx']))),pady=int(round(float(row.loc['pady'])))
			,sticky=row.loc['sticky'])
	def widget_entry(self,container,dict,name,row):
		if name in dict.keys():
			dict[name].destroy()
		dict[name]=tk.Entry(container)
		dict[name].grid(row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column']))),rowspan=int(round(float(row.loc['rowspan'])))
		,columnspan=int(round(float(row.loc['columnspan']))),padx=int(round(float(row.loc['padx']))),pady=int(round(float(row.loc['pady'])))
			,sticky=row.loc['sticky'])
		dict[name].insert(tk.END,row.loc['text'])
	def widget_optionmenu(self,container,dict,name,row):
		#if name in dict.keys():
		#	dict[name].destroy()
		command_text=('self.master.'+row.loc['command'] if self.command_real else 'self.master.do_nothing')
		list=row.loc['option_list'].split(',')
		dict[name]=tk.StringVar()
		opmen=ttk.OptionMenu(container,dict[name],list[0],*list,command=eval(command_text))
		opmen.grid(row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column']))),rowspan=int(round(float(row.loc['rowspan'])))
		,columnspan=int(round(float(row.loc['columnspan']))),padx=int(round(float(row.loc['padx']))),pady=int(round(float(row.loc['pady'])))
			,sticky=row.loc['sticky'])
	def widget_text(self,container,dict,name,row):
		if name in dict.keys():
			dict[name].destroy()
		dict[name]=tk.Text(container,height=int(round(float(row.loc['height']))),width=int(round(float(row.loc['width']))))
		dict[name].grid(row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column']))),rowspan=int(round(float(row.loc['rowspan'])))
		,columnspan=int(round(float(row.loc['columnspan']))),padx=int(round(float(row.loc['padx']))),pady=int(round(float(row.loc['pady'])))
			,sticky=row.loc['sticky'])
		if '|' in str(row.loc['text']):
			for r in row.loc['text'].split('|'):
				dict[name].insert(tk.END,r+'\n')
		else:	
			dict[name].insert(tk.END,row.loc['text'])
			
	def widget_listbox(self,container,dict,name,row):
		if name in dict.keys():
			dict[name].destroy()
		command_text=('self.master.'+row.loc['command'] if self.command_real else 'self.master.do_nothing')
		list=row.loc['option_list'].split(',')
		mode={'SINGLE':tk.SINGLE,'MULTIPLE':tk.MULTIPLE}
		if row.loc['scrollbar'].upper()=='YES':
			scroll=tk.Scrollbar(container)#	Create a scroll bar to be used to control a listbox
			dict[name]=tk.Listbox(container,width=int(round(float(row.loc['width']))),height=int(round(float(row.loc['height'])))
			,selectmode=mode[row.loc['listbox_type'].upper()],yscrollcommand=scroll.set,exportselection=False)# Create the listbox so that only one item can be chosen
			scroll.config(command=dict[name].yview)#		Configure the scroll bar to control the listbox
			scroll.grid(row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column'])))+int(round(float(row.loc['columnspan'])))
			,rowspan=int(round(float(row.loc['rowspan']))),sticky='NS')
		else:
			dict[name]=tk.Listbox(container,width=int(round(float(row.loc['width']))),height=int(round(float(row.loc['height'])))
			,selectmode=mode[row.loc['listbox_type']],exportselection=False)# Create the listbox so that only one item can be chosen
		dict[name].bind('<<ListboxSelect>>',eval(command_text))#	Bind a left click on the listbox to call a method
		dict[name].grid(sticky=row.loc['sticky'],row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column'])))
		,rowspan=int(round(float(row.loc['rowspan']))),columnspan=int(round(float(row.loc['columnspan']))),padx=int(round(float(row.loc['padx'])))
		,pady=int(round(float(row.loc['pady']))))
		#dict[name].insert(tk.END,*list)
	
	def widget_spinbox(self,container,dict,name,row):
		if name in dict.keys():
			dict[name].destroy()
		dict[name]=tk.Spinbox(container,increment=int(round(float(row.loc['spin_increment']))),from_=int(round(float(row.loc['spin_from'])))
		,to=int(round(float(row.loc['spin_to']))),textvariable=tk.DoubleVar(value=0))
		dict[name].grid(sticky=row.loc['sticky'],row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column'])))
		,rowspan=int(round(float(row.loc['rowspan']))),columnspan=int(round(float(row.loc['columnspan'])))
		,padx=int(round(float(row.loc['padx']))),pady=int(round(float(row.loc['pady']))))
	
	def widget_checkbutton(self,container,dict,name,row):
		if name in dict.keys():
			dict[name].destroy()
		command_text=('self.master.'+row.loc['command'] if self.command_real else 'self.master.do_nothing')
		dict[name]=tk.IntVar()
		rad=tk.Checkbutton(container,text=row.loc['text'],variable=dict[name],command=eval(command_text))
		rad.grid(sticky=row.loc['sticky'],row=int(round(float(row.loc['row']))),column=int(round(float(row.loc['column'])))
		,rowspan=int(round(float(row.loc['rowspan']))),columnspan=int(round(float(row.loc['columnspan'])))
		,padx=int(round(float(row.loc['padx']))),pady=int(round(float(row.loc['pady']))))