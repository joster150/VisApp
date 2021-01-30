from plotting_collection import *
###This file contains the tkinter interface - the front end of the program ###

#Import required modules
import tkinter as tk
from tkinter import ttk
import pandas as pd
import openpyxl
import numpy as np
import os
from Interpretter import *
from tkinter import simpledialog
from tkinter.filedialog import askopenfilename,askopenfilenames,askdirectory,asksaveasfilename
from tkinter.colorchooser import askcolor
from tkinter import messagebox as mb
from Generic_Visualisation_additional_functions import *
import multiprocessing
import math
from itertools import chain
import random
#global variables and methods
source=os.path.dirname(os.path.realpath(__file__))
plt.switch_backend('Tkagg')
matplotlib.use('Tkagg')
#Create the Main Class that provide the framework for the interface
class Generic_Visualisation(tk.Tk):#new class inheriting from tk.Tk

	def __init__(self,*args,**kwargs):#Class initilizing method (Happens First)
		#*args - arguments, any number of viariables can be parsed through
		#**kwarks - key word arguments, parsing through dicts mostly
		tk.Tk.__init__(self,*args,**kwargs)#initialising tkinter
		tk.Tk.wm_title(self,"Generic_Visualisation")#Set title
		#self.state('zoomed')

		#initialize some essential atributes of the class
		self.active_address=''
		self.active_input_df=''
		self.active_files={}
		self.active_stack={}
		self.active_merge={}
		self.merged_master=pd.DataFrame()
		self.active_input_df=''
		self.row_begin=0
		self.row_end=20
		self.slice_row_begin=0
		self.slice_row_end=20
		self.file=pd.DataFrame()
		self.file_slice=pd.DataFrame()
		self.previous_files=[]
		self.config_df={}
		self.color_col_dict={}
		self.active_manip_df=pd.DataFrame
		for x in ('frames','widgets'):
			self.config_df[x]=pd.ExcelFile(source+'/Gen_Vis_Config.xlsx').parse(x,header=0,index_col='name').fillna('')

		#create the dictionaries that will store the widgets
		self.frame_dict={'window':{},'base':{},'embedded_changeable':{},'standard':{},'change_option':{}}
		self.widget_dict={}
		#call the interpretter to create the GUI from the Config File
		create_GUI_from_df(self,self.config_df)
		#Create the plotting interface
		self.canvas_frames=matplotlib_creations(self.frame_dict['standard']['plot_frame'])
		self.frame_dict['change_option']['manipulation']['filter'].tkraise()
		self.frame_dict['change_option']['input_change']['single'].tkraise()
		self.frame_dict['change_option']['plot_config']['axis_labels'].tkraise()

		self.state('zoomed')
	###

	###plotting control
	def add_canvas(self,val=""):
		self.canvas_frames.add_canvas()
	def add_pop_out_canvas(self,val=""):
		self.canvas_frames.add_canvas(pop_out=True)
	def remove_canvas(self,val=""):
		self.canvas_frames.remove_canvas()
	def previous_canvas(self,val=""):
		self.canvas_frames.previous_canvas()
	def next_canvas(self,val=""):
		self.canvas_frames.next_canvas()

	###Changeable frame control
	def raise_input_ops(self,val=""):
		dict={'Single':'single','Multiple_Stack':'stack','Multiple_Merge':'merge'}
		self.frame_dict['change_option']['input_change'][dict[val]].tkraise()
	def raise_manip_ops(self,val=""):
		dict={'Filter':'filter','Convert Columns':'convert_cols','Combine Columns':'combine_cols','Match Columns':'match_cols',
		'Set Column Values':'set_col_if_col','Create Colour Column':'create_colour_col','Estimate Pump Outputs':'estimate_pump'}
		self.frame_dict['change_option']['manipulation'][dict[val]].tkraise()
	def raise_plot_ops(self,val=""):
		dict={'Basic Plots':'basic_plots','Stat Scatter':'stat_plot','Vetical Lines':'vertical_line_plot','Annotate Plot':'annotate_plot',
				'Add Overlays':'overlay_plot','Create Subplot':'subplot_creation'}
		self.frame_dict['change_option']['manipulation'][dict[val]].tkraise()
	def raise_plot_contr_ops(self,val=""):
		dict={'Axis Labels':'axis_labels','Other':'other'}
		self.frame_dict['change_option']['plot_config'][dict[val]].tkraise()

	###
	def load_input(self,val=""):
		if not isinstance(self.active_input_df,str):
			self.file=self.active_input_df.copy()
			self.update_file_area(top=True)
			self.reset_inputs()
			self.frame_select.set('main')
			self.frame_dict['base'][self.frame_select.get()].tkraise()
	def reset_inputs(self):
		self.active_address=''
		self.active_files={}
		self.active_stack={}
		widgets_to_clear=['input_preview','files_to_stack_list','file_1_stack_link',
		'column_1_stack_link','file_2_stack_link','column_2_stack_link','stack_links_preview']
		for name,row in self.config_df['widgets'].loc[widgets_to_clear].iterrows():
			start=(1.0 if row.loc['widget_type']=='text' else 0)
			self.widget_dict[row.loc['parent_frame']][row.loc['widget_type']][name].delete(start,tk.END)
	def get_single_excel_or_csv(self,val=""):
		self.active_address=askopenfilename(initialdir=source,filetypes=[("Allowed Files", ["*.xlsx","*.xls","*.csv"])])
	def get_head_sheet_and_load(self,val=""):
		if self.active_address!='':
			excel_type=(False if self.active_address.endswith('.csv') else True)
			head,sheet_identifier=assign_head_and_sheet(excel=excel_type)
			self.active_input_df=read_file_into_df(self.active_address,head,sheet_identifier)
			delete_and_insert_text(self.widget_dict['input']['text']['input_preview'],self.active_input_df.head(20))
		else:
			mb.showerror('Error','You must browse for and select a file first.')
	def get_multiple_excel_or_csv(self,val=""):
		addresses=askopenfilenames(initialdir=source,filetypes=[("Allowed Files", ["*.xlsx","*.xls","*.csv"])])
		if addresses not in [[],['']]:
			self.active_files={}
			self.active_stack={}
			self.active_merge={}
			for x in addresses:
				name=x[x.rfind('/')+1:x.rfind('.')]
				self.active_files[name]=x
				self.active_stack[name]=''
				self.active_merge[name]=''
	def populate_files_for_stack(self):
		self.get_multiple_excel_or_csv()
		delete_and_insert_listbox(self.widget_dict['stack']['listbox']['files_to_stack_list'],[*self.active_files.keys()])
	def populate_files_for_merge(self):
		self.get_multiple_excel_or_csv()
		delete_and_insert_listbox(self.widget_dict['merge']['listbox']['merge_head_and_sheets'],[*self.active_files.keys()])
	def on_select_files_to_stack(self,val=""):
		file=get_on_select_values(val)
		excel_type=(False if self.active_files[file].endswith('.csv') else True)
		head,sheet_identifier=assign_head_and_sheet(excel=excel_type)
		self.active_stack[file]=read_file_into_df(self.active_files[file],head,sheet_identifier)
		if True not in [isinstance(i,str) for i in self.active_stack.values()]:
			delete_and_insert_listbox(self.widget_dict['stack']['listbox']['file_1_stack_link'],[*self.active_stack.keys()])
			delete_and_insert_listbox(self.widget_dict['stack']['listbox']['file_2_stack_link'],[*self.active_stack.keys()])
			delete_and_insert_text(self.widget_dict['stack']['text']['stack_links_preview'],detect_only_common_cols(self.active_stack))
	def on_select_file_link_1(self,val=""):
		delete_and_insert_listbox(self.widget_dict['stack']['listbox']['column_1_stack_link'],[*self.active_stack[get_on_select_values(val)].columns])
	def on_select_file_link_2(self,val=""):
		delete_and_insert_listbox(self.widget_dict['stack']['listbox']['column_2_stack_link'],[*self.active_stack[get_on_select_values(val)].columns])
	def stack_make_manual_link(self,val=""):
		try:
			cols=get_selected_vals(self.config_df,self.widget_dict,['file_1_stack_link','file_2_stack_link','column_1_stack_link','column_2_stack_link'])
			f2_cols=list(self.active_stack[cols['file_2_stack_link']].columns)
			f2_cols[f2_cols.index(cols['column_2_stack_link'])]=cols['column_1_stack_link']
			self.active_stack[cols['file_2_stack_link']].columns=f2_cols
			delete_and_insert_listbox(self.widget_dict['stack']['listbox']['column_1_stack_link'],[*self.active_stack[cols['file_1_stack_link']].columns])
			delete_and_insert_listbox(self.widget_dict['stack']['listbox']['column_2_stack_link'],[*self.active_stack[cols['file_2_stack_link']].columns])
			delete_and_insert_text(self.widget_dict['stack']['text']['stack_links_preview'],detect_only_common_cols(self.active_stack))
		except:
			mb.showerror('Error','You must select two files and 2 columns to make the links')
	def create_from_stack_links(self,val=""):
		common_cols=detect_only_common_cols(self.active_stack)
		self.active_input_df=pd.DataFrame(columns=common_cols)
		for df in self.active_stack.values():
			self.active_input_df=pd.concat([self.active_input_df,df[common_cols]])
		self.active_input_df.drop_duplicates(inplace=True)
		delete_and_insert_text(self.widget_dict['input']['text']['input_preview'],self.active_input_df.head(20))

	def on_select_files_to_merge(self,val=""):
		file=get_on_select_values(val)
		excel_type=(False if self.active_files[file].endswith('.csv') else True)
		head,sheet_identifier=assign_head_and_sheet(excel=excel_type)
		self.active_merge[file]=read_file_into_df(self.active_files[file],head,sheet_identifier)
		if True not in [isinstance(i,str) for i in self.active_merge.values()]:
			delete_and_insert_listbox(self.widget_dict['merge']['listbox']['merge_file_select'],[*self.active_merge.keys()])
	def on_select_merge_file_select(self,val=""):
		for lbox in ['merge_select_merge_col','merge_select_other_cols']:
			delete_and_insert_listbox(self.widget_dict['merge']['listbox'][lbox],[*self.active_merge[get_on_select_values(val)].columns])

	def merge_file_to_master(self,val=""):
		listboxes=['merge_file_select','merge_select_merge_col','merge_select_master_merge_col','merge_select_other_cols']
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,listboxes+['merge_options'])
		file,file_merge_col,master_merge_col,file_other_cols=[(cols_and_vals[v] if (cols_and_vals[v] not in ['',['']]) else None) for v in listboxes]
		file_other_cols=([file_other_cols] if isinstance(file_other_cols,str) else file_other_cols)
		if (not self.merged_master.empty) and cols_and_vals['merge_options']=='Just Combine Current Columns':
			#select columns to combine
			chosen_combine_1=get_column_from_df(self.merged_master,"Select the 1st column to combine")
			chosen_combine_2=get_column_from_df(self.merged_master,"Select the 2nd column to combine")
			self.merged_master[chosen_combine_1]=self.merged_master[chosen_combine_1].fillna(self.merged_master[chosen_combine_2])
			self.merged_master=self.merged_master.drop([chosen_combine_2],axis=1)
			#give name for merged column
			renamed_cols=assign_new_names_merge([*self.merged_master.columns],[chosen_combine_1])
			self.merged_master.columns=renamed_cols
		elif self.merged_master.empty and [file,file_merge_col]!=[None,None]:
			file_other_cols=([] if (file_other_cols==None or [file_merge_col]==file_other_cols) else file_other_cols)
			combined_lists=[file_merge_col]+file_other_cols
			self.merged_master=self.active_merge[file][combined_lists].copy()
			renamed_cols=assign_new_names_merge([*self.merged_master.columns],combined_lists)
			file_merge_col=renamed_cols[0]
			self.merged_master.columns=renamed_cols
			self.merged_master[file_merge_col]=self.merged_master[file_merge_col].apply(lambda val:''.join(e.upper() for e in str(val) if e.isalnum()))
			if cols_and_vals['merge_options']=='Standard':
				self.merged_master=self.merged_master.drop_duplicates(subset=file_merge_col,keep='last')
			elif cols_and_vals['merge_options']=='Split into two columns (by date)':
				self.merged_master=return_two_split_by_date(self.merged_master,file_merge_col)
			elif cols_and_vals['merge_options']=='Combine other cols':
				self.merged_master=self.merged_master.replace('N/A',np.nan)
				if len(renamed_cols)>2:
					for x in renamed_cols[2:]:
						self.merged_master[renamed_cols[1]]=self.merged_master[renamed_cols[1]].fillna(self.merged_master[x])
						self.merged_master=self.merged_master.drop([x],axis=1)
				self.merged_master=self.merged_master.drop_duplicates(subset=file_merge_col,keep='last')
			self.merged_master=self.merged_master.dropna()
		elif [file,file_merge_col,master_merge_col,file_other_cols]!=[None,None,None,None]:
			to_merge=self.active_merge[file][[file_merge_col]+file_other_cols].copy()
			renamed_cols=assign_new_names_merge([*to_merge.columns],file_other_cols)
			to_merge.columns=renamed_cols
			file_merge_col=renamed_cols[0]
			to_merge[file_merge_col]=to_merge[file_merge_col].apply(lambda val:''.join(e.upper() for e in str(val) if e.isalnum()))
			self.merged_master[master_merge_col]=self.merged_master[master_merge_col].apply(lambda val:''.join(e.upper() for e in str(val) if e.isalnum()))
			if cols_and_vals['merge_options']=='Standard':
				to_merge=to_merge.drop_duplicates(subset=file_merge_col,keep='last')
			elif cols_and_vals['merge_options']=='Split into two columns (by date)':
				to_merge=return_two_split_by_date(to_merge,file_merge_col)
			elif cols_and_vals['merge_options']=='Combine other cols':
				to_merge=to_merge.replace('N/A',np.nan)
				if len(renamed_cols)>2:
					for x in renamed_cols[2:]:
						to_merge[renamed_cols[1]]=to_merge[renamed_cols[1]].fillna(to_merge[x])
						to_merge=to_merge.drop([x],axis=1)
				to_merge=to_merge.drop_duplicates(subset=file_merge_col,keep='last')
			to_merge=to_merge.dropna()
			self.merged_master=pd.merge(self.merged_master,to_merge,left_on=master_merge_col,right_on=file_merge_col,how='outer')
			if master_merge_col!=file_merge_col:
				self.merged_master[master_merge_col]=self.merged_master[master_merge_col].fillna(self.merged_master[file_merge_col])
				self.merged_master=self.merged_master.drop(file_merge_col,axis=1)
			self.merged_master.sort_values(by=master_merge_col,inplace=True)
		else:
			mb.showerror('Error','You need to select all the necessary columns')
		delete_and_insert_text(self.widget_dict['merge']['text']['merge_links_text'],self.merged_master.head())
		delete_and_insert_listbox(self.widget_dict['merge']['listbox']['merge_select_master_merge_col'],[*self.merged_master.columns])

	def create_master(self,val=""):
		self.active_input_df=self.merged_master.copy()
		self.active_input_df.drop_duplicates(inplace=True)
		delete_and_insert_text(self.widget_dict['input']['text']['input_preview'],self.active_input_df.head(20))
		self.merged_master=pd.DataFrame()
		self.active_merge={}
		for lbox in ['merge_head_and_sheets','merge_file_select','merge_select_merge_col','merge_select_master_merge_col','merge_select_other_cols']:
			self.widget_dict['merge']['listbox'][lbox].delete(0,tk.END)
		self.widget_dict['merge']['text']['merge_links_text'].delete(1.0,tk.END)
	def save_input_as_new(self,val=""):
		filename=asksaveasfilename(filetypes=[('Comma Seperated','.csv')])
		if filename!='':
			filename=(filename+'.csv' if not filename.endswith('.csv') else filename)
			self.active_input_df.to_csv(filename,index=False)
	def resest_file(self,val=""):
		self.file=self.active_input_df.copy()
		self.update_file_area()
		self.widget_dict['data']['text']['file_slice_area'].delete(1.0,tk.END)
	def undo_file(self,val=""):
		if self.previous_files!=[]:
			self.file=self.previous_files[-1]
			del self.previous_files[-1]
			self.update_file_and_slice()
	def add_previous_file(self,val=""):
		if len(self.previous_files)>5:
			del self.previous_files[0]
		self.previous_files.append(self.file)
	def slice_to_file(self,val=""):
		display_opt=self.widget_dict['data']['optionmenu']['slice_display_option'].get()
		data=self.file_slice.dropna()
		if display_opt=='Stats':
			for x in data.dtypes.index:
				if data.dtypes.loc[x]=='object':
					data=data.groupby(x)[[i for i in data.columns if i!=x]]
					break
			data=data.describe()
			if data.index.nlevels>1:
				data=data.unstack()
		elif display_opt=='Counts':
			data['count']=''
			data=data.groupby(list(data.columns[:-1])).count()
		filename=asksaveasfilename(filetypes=[('Comma Seperated','.csv')])
		if filename!='':
			filename=(filename+'.csv' if not filename.endswith('.csv') else filename)
			data.to_csv(filename)
	def do_nothing(self,val=""):
		pass
	def create_slice(self,val=""):
		try:
			cols=get_selected_vals(self.config_df,self.widget_dict,['slice_cols_list'])
			cols=([cols] if not isinstance(cols,list) else cols)
			self.file_slice=self.file[cols]
		except:
			mb.showerror('Error','You must select at least one column from the file.')
		self.update_file_slice_area()
	def update_file_area(self,top=False,bot=False,up=False,down=False):
		max_rows=self.file.iloc[:,0].size
		len=10
		if bot:
			self.row_begin=max_rows-len
			self.row_end=max_rows
		elif up and self.row_begin>len-1:
			self.row_begin-=len
			self.row_end-=len
		elif down and (max_rows-self.row_end)>len-1:
			self.row_begin+=len
			self.row_end+=len
		elif top:
			self.row_begin=0
			self.row_end=len
		delete_and_insert_text(self.widget_dict['data']['text']['file_area'],self.file.iloc[self.row_begin:self.row_end,:])
		self.update_file_listboxes()
	def update_file_listboxes(self):
		listbox_names=[
		'slice_cols_list','filter_col_list','convert_col_list','add_col_list','subtract_col_list','multiply_col_list',
		'divide_col_list','match_col_list','change_col_list','if_col_list','colour_col_list','mass_col_list',
		'p30_col_list','temp_col_list','speed_col_list']
		for name,row in self.config_df['widgets'].loc[listbox_names].iterrows():
			delete_and_insert_listbox(self.widget_dict[row.loc['parent_frame']][row.loc['widget_type']][name],[*self.file.columns])
	def update_file_slice_listboxes(self):
		listbox_names=['x_vals_list','y_vals_list','group_col_list','colour_col_plot_list',
		'subplot_col_list','vert_x_list','vert_y1_list','vert_y2_list','vert_group_list','vert_colour_list','vert_subplot_list',
		'label_col_list','annot_x_list','annot_y_list','annot_colour_list','annot_subplot_list','annot_cond_list',
		'over_subplot_list','x_vals_stat_list','y_vals_stat_list','group_col_stat_list','colour_col_stat_list','subplot_col_stat_list']
		for name,row in self.config_df['widgets'].loc[listbox_names].iterrows():
			delete_and_insert_listbox(self.widget_dict[row.loc['parent_frame']][row.loc['widget_type']][name],[*self.file_slice.columns]+['Ignore'])
	def top_file_area(self,val=""):
		self.update_file_area(top=True)
	def up_file_area(self,val=""):
		self.update_file_area(up=True)
	def down_file_area(self,val=""):
		self.update_file_area(down=True)
	def bot_file_area(self,val=""):
		self.update_file_area(bot=True)
	def update_file_and_slice(self,val=""):
		if not self.file_slice.empty:
			self.file_slice=self.file[list(self.file_slice.columns)]
			self.up_file_slice_area()
		self.update_file_area()
	def update_file_slice_area(self,top=False,bot=False,up=False,down=False):
		display_opt=self.widget_dict['data']['optionmenu']['slice_display_option'].get()
		data=self.file_slice.dropna()
		if display_opt=='Stats':
			for x in data.dtypes.index:
				if data.dtypes.loc[x]=='object':
					data=data.groupby(x)[[i for i in data.columns if i!=x]]
					break
			data=data.describe()
			if data.index.nlevels>1:
				data=data.unstack()
		elif display_opt=='Counts':
			data['count']=''
			data=data.groupby(list(data.columns[:-1])).count()# if len(list(data.columns))>1 else data.apply(pd.value_counts))

		max_rows=len(data.index)
		rows=10
		if self.row_end>max_rows and top!=True and bot!=True:
			top=True
		if top:
			self.slice_row_begin=0
			self.slice_row_end=rows
		elif bot:
			self.slice_row_begin=max_rows-rows
			self.slice_row_end=max_rows
		elif up and self.slice_row_begin>rows-1:
			self.slice_row_begin-=rows
			self.slice_row_end-=rows
		elif down and (max_rows-self.slice_row_end)>rows-1:
			self.slice_row_begin+=rows
			self.slice_row_end+=rows
		delete_and_insert_text(self.widget_dict['data']['text']['file_slice_area'],data.iloc[self.slice_row_begin:self.slice_row_end,:])
		self.update_file_slice_listboxes()
	def top_file_slice_area(self,top=False,bot=False,up=False,down=False):
		self.update_file_slice_area(top=True)
	def up_file_slice_area(self,val=""):
		self.update_file_slice_area(up=True)
	def down_slice_file_area(self,val=""):
		self.update_file_slice_area(down=True)
	def bot_slice_file_area(self,val=""):
		self.update_file_slice_area(bot=True)
	def filter_file(self,val=""):
		try:
			col_and_vals=get_selected_vals(self.config_df,self.widget_dict,['filter_col_list','filter_condition_opt','filter_entry'])
			condition=filter_condition(self.file,col_and_vals['filter_col_list'],col_and_vals['filter_condition_opt'],col_and_vals['filter_entry'])
			self.add_previous_file()
			self.file=self.file.loc[condition]
			self.update_file_and_slice()
		except:
			mb.showerror('Error','Invalid combination of col, option and value(s)')
	def convert_column(self,val=""):
		#try:
		col_and_vals=get_selected_vals(self.config_df,self.widget_dict,['convert_col_list','convert_condition_opt','date_format_opt','date_format_entry'])
		col_and_vals['convert_col_list']=([col_and_vals['convert_col_list']] if isinstance(col_and_vals['convert_col_list'],str) else col_and_vals['convert_col_list'])

		if col_and_vals['convert_condition_opt']!='Date':
			temp=convert_standard_column_type(self.file,col_and_vals['convert_col_list'],col_and_vals['convert_condition_opt'])
		else:
			format =(col_and_vals['date_format_entry'] if col_and_vals['date_format_opt']=='Custom' else col_and_vals['date_format_opt'])
			temp=convert_date_column_type(self.file,col_and_vals['convert_col_list'],format)
		self.add_previous_file()
		self.file=temp.copy()
		temp=''
		self.update_file_and_slice()
		#except:
		#	mb.showerror('Error','Failed Conversion')
	def combine_column_1(self,val=""):
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,['add_col_list','subtract_col_list','date_combine_check'])
		date=bool(cols_and_vals['date_combine_check'])
		add_cols=([cols_and_vals['add_col_list']] if not isinstance(cols_and_vals['add_col_list'],list) else cols_and_vals['add_col_list'])
		sub_cols=([cols_and_vals['subtract_col_list']] if not isinstance(cols_and_vals['subtract_col_list'],list) else cols_and_vals['subtract_col_list'])
		temp=add_and_subtract(self.file,add_cols,sub_cols,date)
		self.add_previous_file()
		title=''
		for i in add_cols+sub_cols:
			if i!='':
				title+=' '+i
		self.file['AddSub_'+title]=temp.copy()
		temp=''
		self.update_file_and_slice()

	def combine_column_2(self,val=""):
		cols=get_selected_vals(self.config_df,self.widget_dict,['multiply_col_list','divide_col_list'])
		mult_cols=([cols['multiply_col_list']] if not isinstance(cols['multiply_col_list'],list) else cols['multiply_col_list'])
		div_cols=([cols['divide_col_list']] if not isinstance(cols['divide_col_list'],list) else cols['divide_col_list'])
		temp=multiply_and_divide(self.file,mult_cols,div_cols)
		self.add_previous_file()
		title=''
		for i in mult_cols+div_cols:
			if i!='':
				title+=' '+i
		self.file['MultDiv_'+title]=temp.copy()
		temp=''
		self.update_file_and_slice()
	def on_select_match_col(self,val=''):
		col=get_on_select_values(val)
		linking_filepath=askopenfilename(initialdir=source,title='Select File containing: '+col+' link.',filetypes=[("Allowed Files", ["*.xlsx","*.xls","*.csv"])])
		excel_type=(False if linking_filepath.endswith('.csv') else True)
		head,sheet=assign_head_and_sheet(excel=excel_type)
		self.active_manip_df=read_file_into_df(linking_filepath,head,sheet)
		delete_and_insert_listbox(self.widget_dict['match_cols']['listbox']['match_col_from_file_1'],[*self.active_manip_df.columns])
		delete_and_insert_listbox(self.widget_dict['match_cols']['listbox']['match_col_from_file_2'],[*self.active_manip_df.columns])
	def match_column(self,val=""):
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,['match_col_list','match_col_from_file_1','match_col_from_file_2','new_match_col_check'])
		df=self.active_manip_df[[cols_and_vals['match_col_from_file_1'],cols_and_vals['match_col_from_file_2']]].dropna().drop_duplicates(subset=cols_and_vals['match_col_from_file_1']).drop_duplicates(subset=cols_and_vals['match_col_from_file_2']).set_index(cols_and_vals['match_col_from_file_1'])
		df=df[cols_and_vals['match_col_from_file_2']]
		self.add_previous_file()
		col=self.file[cols_and_vals['match_col_list']].map(df).fillna(self.file[cols_and_vals['match_col_list']])
		if bool(cols_and_vals['new_match_col_check']):
			self.file[cols_and_vals['match_col_from_file_2']]=col
		else:
			self.file[cols_and_vals['match_col_list']]=col
		self.update_file_and_slice()
		self.widget_dict['match_cols']['listbox']['match_col_from_file_1'].delete(0,tk.END)
		self.widget_dict['match_cols']['listbox']['match_col_from_file_2'].delete(0,tk.END)
	def add_blank_column(self,val=""):
		value=get_selected_vals(self.config_df,self.widget_dict,['blank_col_name'])
		if value!='':
			self.file[value]=''
			self.update_file_area()
		else:
			mb.showerror('Error','Enter a name for the column first.')
	def set_column_values(self,val=""):
		try:
			cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,['change_col_list','set_values_to','if_col_list','if_col_condition_opt','if_col_value'])
			self.add_previous_file()
			condition=filter_condition(self.file,cols_and_vals['if_col_list'],cols_and_vals['if_col_condition_opt'],cols_and_vals['if_col_value'])
			self.file[cols_and_vals['change_col_list']].loc[condition]=cols_and_vals['set_values_to']
			self.update_file_and_slice()
		except:
			mb.showerror('Error','Select the column to change and the column to determine what to change from the first column.')

	def pop_unique_colours(self,val=""):
		col=get_on_select_values(val)
		unique_vals=self.file[col].unique()
		delete_and_insert_listbox(self.widget_dict['create_colour_col']['listbox']['unique_colour_list'],[*unique_vals])
		self.color_col_dict=generate_random_color_dict(unique_vals)
		delete_and_insert_text(self.widget_dict['create_colour_col']['text']['colour_mapping_area'],self.color_col_dict)
	def assign_unique_colour(self,val=""):
		val=get_on_select_values(val)
		self.color_col_dict[val]=askcolor(parent=self)[1]
		delete_and_insert_text(self.widget_dict['create_colour_col']['text']['colour_mapping_area'],self.color_col_dict)
	def create_colour_column(self,val=""):
		col=get_selected_vals(self.config_df,self.widget_dict,['colour_col_list'])
		self.add_previous_file()
		self.file['Colour_'+col]=self.file[col].map(self.color_col_dict)
		self.update_file_and_slice()
	def estimate_and_create_pump(self,val=""):
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,['mass_col_list','p30_col_list','temp_col_list','speed_col_list','pump_type_opt','flight_cond_opt',
				'fuel_type_opt','art_flow_check','delivered_flow_check','pressure_rise_check','pump_leakage_check','volumetric_flow_check','submit_esimate_create'])
		pump_used=pump(cols_and_vals['pump_type_opt']+' '+cols_and_vals['flight_cond_opt'])
		fuel=fuel_calcs(fuel_used=cols_and_vals['fuel_type_opt'])
		volumetric_flow=''
		if cols_and_vals['mass_col_list']!='' and cols_and_vals['temp_col_list']!='':
			volumetric_flow=fuel.mass_to_volumetric(self.file[cols_and_vals['mass_col_list']],self.file[cols_and_vals['temp_col_list']])*1.0376#
			if cols_and_vals['p30_col_list']!='':
				pump_used.estimate_pressure_rise(volumetric_flow=volumetric_flow,P30=self.file[cols_and_vals['p30_col_list']])
				pump_used.calculate_TO_leaks(temps=self.file[cols_and_vals['temp_col_list']],density=fuel.current_density(self.file[cols_and_vals['temp_col_list']]))#	Estimate the leakages betweeen pump and metering
				pump_used.calculate_delivered_flow(volumetric_flow)#	Calculate the flow out of the pump (-Spill)
				if cols_and_vals['speed_col_list']!='':
					pump_used.calculate_art_flow(speeds=self.file[cols_and_vals['speed_col_list']],temps=self.file[cols_and_vals['temp_col_list']])
		created_series={'art_flow':pump_used.art_flow,'delivered_flow':pump_used.delivered_flow,
								'pressure_rise':pump_used.pressure_rise,'pump_leakage':pump_used.leakages,'volumetric_flow':volumetric_flow}
		self.add_previous_file()
		for key,val in cols_and_vals.items():
			if 'check' in key and bool(val):
				name=key[:key.rfind('_')]
				if not isinstance(created_series[name],str):
					self.file[name]=created_series[name]
		self.update_file_area()
	def plot_basic(self,val=""):
		listboxes=['x_vals_list','y_vals_list','group_col_list','colour_col_plot_list','subplot_col_list']
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,listboxes+['plot_type_opt','basics_plot_by_opt'])
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		#print(axes)
		if cols_and_vals['basics_plot_by_opt']=='Replace Current Plot':
			axes={}
			fig.clf()
		data={}
		X,Y,group,colour,subplot=[(cols_and_vals[v] if (cols_and_vals[v] not in [[''],['Ignore'],'','Ignore']) else [None]) for v in listboxes]
		X,Y,group,colour,subplot=[v if isinstance(v,list) else [v] for v in [X,Y,group,colour,subplot]]
		not_none=[v for v in [X,Y,group,colour,subplot] if v!=[None]]
		slice=self.file_slice[[*set(chain.from_iterable(not_none))]]
		axes,data=get_axes_and_data_if_condition(cols_and_vals['basics_plot_by_opt'],axes,slice,subplot[0],fig)
		#axes,data=get_axes_and_data(subplot[0],slice,fig)
		group=(group[0] if group[0]!=None else 'Entire_Grouping')
		if group=='Entire_Grouping':
			for val in data.values():
				val[group]='Whole_Population'
		if X!=None or Y!=None:
			plotting={'Histogram':'hist','CDF':'cdf_plot','Bar':'bar','Scatter':'scatter','Line':'line','Regression Comparison':'reg_comp'
			,'Swarm Plot':'swarm','Box Plot':'box','Joint Plot':'joint','Pair Plot':'pairplot','Heatmap':'heat','Contour Plot':'contour','Stat Plot':'stat_scatter'}
			eval(plotting[cols_and_vals['plot_type_opt']]+('(data,axes,X,Y,group,colour[0],fig)'
				if plotting[cols_and_vals['plot_type_opt']] not in ['joint','pairplot'] else '(data,axes,X,Y,group,colour[0],fig,self.canvas_frames)'))
			update_fig_ax(canvas,toolbar,fig,axes)
			self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
		else:
			mb.showerror('Error','You need to choose a data column to plot')
	def stat_scatter_plot(self,val=''):
		listboxes=['x_vals_stat_list','y_vals_stat_list','group_col_stat_list','colour_col_stat_list','subplot_col_stat_list']
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,listboxes+['stat_opt_chosen','stat_plot_by_opt'])
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		if cols_and_vals['stat_plot_by_opt']=='Replace Current Plot':
			axes={}
			fig.clf()
		data={}
		stat_chosen=cols_and_vals['stat_opt_chosen']
		X,Y,group,colour,subplot=[(cols_and_vals[v] if (cols_and_vals[v] not in ['','Ignore']) else None) for v in listboxes]
		not_none=[v for v in [X,Y,group,colour,subplot] if v!=None]
		slice=self.file_slice[not_none]
		axes,data=get_axes_and_data_if_condition(cols_and_vals['stat_plot_by_opt'],axes,slice,subplot,fig)
		group=(group if group!=None else 'Entire_Grouping')
		if group=='Entire_Grouping':
			for val in data.values():
				val[group]='Whole_Population'
		if X!=None and Y!=None:
			stat_scatter(data,axes,X,Y,stat_chosen,group,colour,fig)
			self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
			update_fig_ax(canvas,toolbar,fig,axes)
	def plot_vertical(self,val=""):
		listboxes=['vert_x_list','vert_y1_list','vert_y2_list','vert_group_list','vert_colour_list','vert_subplot_list']
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,listboxes+['vert_plot_by_opt'])
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		if cols_and_vals['vert_plot_by_opt']=='Replace Current Plot':
			axes={}
			fig.clf()

		data={}
		X,Y1,Y2,group,colour,subplot=[(cols_and_vals[v] if (cols_and_vals[v] not in ['','Ignore']) else None) for v in listboxes]
		if X!=None and Y1!=None and Y2!=None:
			not_none=[v for v in [X,Y1,Y2,group,colour,subplot] if v!=None]
			slice=self.file_slice[[*set(not_none)]]
			slice[[X,Y1,Y2]]=slice[[X,Y1,Y2]].apply(pd.to_numeric,errors='coerce')
			slice=slice.dropna()
			axes,data=get_axes_and_data_if_condition(cols_and_vals['vert_plot_by_opt'],axes,slice,subplot,fig)
			group=(group if group!=None else 'Entire_Grouping')
			if group=='Entire_Grouping':
				for val in data.values():
					val[group]='Whole_Population'
			for key,df in data.items():
				for x in df[group].unique():
					df2=df.loc[df[group]==x].dropna()
					col=(df2[colour].iloc[0] if colour!=None else '#%02X%02X%02X' % (random.randint(0,255),random.randint(0,255),random.randint(0,255)))
					axes[key].vlines(x=X,ymax=Y1,ymin=Y2,color=col,data=df2,linewidth=2,label=str(x))
				axes[key].set_xlabel(X)
				axes[key].set_ylabel(Y1)
			update_fig_ax(canvas,toolbar,fig,axes)
			self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
		else:
			mb.showerror('Error','You must select at least a column for x, y1 and y2')
	def add_annotations(self,val=""):
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		listboxes=['label_col_list','annot_x_list','annot_y_list','annot_colour_list','annot_subplot_list','annot_cond_list']
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,listboxes+['annot_cond_opt','annot_size_spin','annot_cond_entry','annotate_subplot_option'])
		lab,X,Y,colour,subplot,cond=[(cols_and_vals[v] if (cols_and_vals[v] not in ['','Ignore']) else None) for v in listboxes]
		if X!=None and Y!=None and lab!=None:
			not_none=[v for v in [lab,X,Y,colour,subplot,cond] if v!=None]
			slice=self.file_slice[[*set(not_none)]]
			slice=slice.dropna()
			if slice[X].dtype=='datetime64[ns]':
				slice[X]=slice[X].apply(date_to_num)

			slice[[X,Y]]=slice[[X,Y]].apply(pd.to_numeric,errors='coerce')
			slice=slice.dropna()
			if colour==None:
				colour='Ran_Col_Col'
				slice[colour]='blue'
			axes2,data2=get_axes_and_data_if_condition(cols_and_vals['annotate_subplot_option'],axes,slice,subplot,fig)
			for key,df in data2.items():
				df2=(df.loc[filter_condition(df,cond,cols_and_vals['annot_cond_opt'],cols_and_vals['annot_cond_entry'])] if not (cols_and_vals['annot_cond_opt'] in ['','Ignore'] or cols_and_vals['annot_cond_entry']=='') else df)
				for i,row in df2.iterrows():
					label,xx,yy,col=[row.loc[lab],row.loc[X],row.loc[Y],row.loc[colour]]
					artists.append(axes2[key].annotate(label,(xx,yy-(yy/75)),fontsize=cols_and_vals['annot_size_spin'],rotation='vertical',color=col))
			update_fig_ax(canvas,toolbar,fig,axes)
			self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
		else:
			mb.showerror('Error','You need to select at least columns for x,y and label.')
	def clear_annotations_and_overlays(self,val=""):
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		for ax in axes.values():
			current_handles,current_labels=ax.get_legend_handles_labels()
			for a in artists:
				if a in current_handles:
					current_handles.remove(a)
				a.remove()
			artists[:]=[]
		update_fig_ax(canvas,toolbar,fig,axes)
		self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
	def pop_overlay_list(self,val=""):
		if val in ['Custom_Line_Overlays','Custom_limit_line_overlays']:
			xls=pd.ExcelFile(source+'/Generic_Overlays.xlsx')
			self.active_overlay_file=xls.parse(val,head=0)
			self.active_overlay_file.set_index('Name',inplace=True)
			delete_and_insert_listbox(self.widget_dict['overlay_plot']['listbox']['overlay_list'],[*self.active_overlay_file.index])
		else:
			self.active_overlay_file=self.file_slice.copy()
			delete_and_insert_listbox(self.widget_dict['overlay_plot']['listbox']['overlay_list'],[*self.active_overlay_file.columns])
	def add_overlay(self,val=""):
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		listboxes=['overlay_list','over_subplot_list']
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,listboxes+['overlay_group_opt','overlay_subplot_option'])
		over_choice,subplot=[(cols_and_vals[v] if (cols_and_vals[v] not in ['','Ignore']) else None) for v in listboxes]
		if over_choice!=None:
			slice=(self.file_slice[[v for v in [over_choice,subplot] if v!=None]] if cols_and_vals['overlay_group_opt']=='Normal_Distribution' else None)
			if subplot!=None:
				slice=(slice if isinstance(slice,pd.DataFrame) else self.file_slice[[subplot]])
			axes2,data2=get_axes_and_data_if_condition(cols_and_vals['overlay_subplot_option'],axes,slice,subplot,fig)
			for key,df in data2.items():
				if cols_and_vals['overlay_group_opt']=='Normal_Distribution':
					normal,mean,std=convert_to_normal(df[over_choice])
					hand=axes2[key].hist(normal,histtype='step',bins=200,label='Normal Dist:\nMean: '+str(round(mean))+'Std: '+str(round(std,2)),color='green')
					artists.append(*hand[2])
				elif cols_and_vals['overlay_group_opt']=='Custom_Line_Overlays':
					row=self.active_overlay_file.loc[over_choice]
					x_list,y_list,col_lab_list,ref=[row.iloc[i] for i in range(len([*row.index]))]
					x_pre_zip=text_list_to_float_list(x_list)
					y_pre_zip=text_list_to_float_list(y_list)
					cols_pre_zip,labs_pre_zip=text_colour_label_to_tuple(col_lab_list)
					for xx,yy,col,lab in zip(x_pre_zip,y_pre_zip,cols_pre_zip,labs_pre_zip):
						hand, =axes2[key].plot(xx,yy,color=col,label=lab,linestyle='--',linewidth=1)
						artists.append(hand)
				elif cols_and_vals['overlay_group_opt']=='Custom_limit_line_overlays':
					row=self.active_overlay_file.loc[over_choice]
					v_list,h_list,v_col_lab,h_col_lab,ref=[row.iloc[i] for i in range(len([*row.index]))]
					for list_type,labs in zip([v_list,h_list],[v_col_lab,h_col_lab]):
						if not pd.isnull(list_type):
							v=list_type.replace('[','').replace(']','').split(',')
							v=[float(i) for i in v]
							v_col_lab_list=labs.split(',')
							v_col=[i[:i.index(':')] for i in v_col_lab_list]
							v_lab=[i[i.index(':')+1:] for i in v_col_lab_list]
							for x_y,col,lab in zip(v,v_col,v_lab):
								if list_type==v_list:
									hand = axes2[key].axvline(x_y,color=col,label=lab,linestyle=':',linewidth=1)
								else:
									hand = axes2[key].axhline(x_y,color=col,label=lab,linestyle=':',linewidth=1)
								artists.append(hand)
			update_fig_ax(canvas,toolbar,fig,axes)
			self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
	def add_axis_label_or_title(self,val=""):
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,['axis_label_title_entry','axis_title_opt'])
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		for ax in axes.values():
			if cols_and_vals['axis_title_opt']=='X-Axis':
				ax.set_xlabel(cols_and_vals['axis_label_title_entry'])
			elif cols_and_vals['axis_title_opt']=='Y-Axis':
				ax.set_ylabel(cols_and_vals['axis_label_title_entry'])
			else:
				ax.set_title(cols_and_vals['axis_label_title_entry'])
		canvas.draw()#	Update the GUI plotting area
		toolbar.update()
		self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
	def rotate_axis_labels(self,val=""):
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,['axis_tick_entry','axis_tick_opt'])
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		for ax in axes.values():
			if cols_and_vals['axis_tick_opt']=='X-Axis':
				plt.setp(ax.get_xticklabels(), rotation=int(cols_and_vals['axis_tick_entry']))
			elif cols_and_vals['axis_tick_opt']=='Y-Axis':
				plt.setp(ax.get_yticklabels(), rotation=int(cols_and_vals['axis_tick_entry']))
		fig.tight_layout()
		canvas.draw()#	Update the GUI plotting area
		toolbar.update()
		self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
	def limit_axis(self,val=""):
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,['axis_lim_entry','axis_lim_opt'])
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		dict_={'X_Min':'ax.set_xlim(left=float(','X_Max':'ax.set_xlim(right=float(','Y_Min':'ax.set_ylim(bottom=float(','Y_Max':'ax.set_ylim(top=float('}
		for ax in axes.values():
			eval(dict_[cols_and_vals['axis_lim_opt']]+cols_and_vals['axis_lim_entry']+'))')
		fig.tight_layout()
		canvas.draw()#	Update the GUI plotting area
		toolbar.update()
		self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
	def config_legend(self,val=""):
		cols_and_vals=get_selected_vals(self.config_df,self.widget_dict,['lege_tsize','lege_ncols','lege_opt'])
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		dict_={'NW':'upper left','NE':'upper right','SW':'lower left','SE':'lower right'}
		for ax in axes.values():
			if cols_and_vals['lege_opt']=='None':
				ax.get_legend().remove()
			else:
				current_handles,current_labels=ax.get_legend_handles_labels()
				ax.legend(handles=current_handles,loc=dict_[cols_and_vals['lege_opt']],ncol=int(cols_and_vals['lege_ncols']),fontsize=int(cols_and_vals['lege_tsize']),framealpha=0.5)
		fig.tight_layout()
		canvas.draw()#	Update the GUI plotting area
		toolbar.update()
		self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)

	def create_blank_subplot(self,val=""):
		vals=get_selected_vals(self.config_df,self.widget_dict,['subcre_num_row','subcre_num_cols'])
		vals['subcre_num_row'],vals['subcre_num_cols']=[int(vals['subcre_num_row']),int(vals['subcre_num_cols'])]
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		axes={}
		fig.clf()
		for i in range(vals['subcre_num_row']*vals['subcre_num_cols']):
			axes[i+1]=fig.add_subplot(vals['subcre_num_row'],vals['subcre_num_cols'],i+1)
			axes[i+1].set_title('Position_'+str(i+1))
		update_fig_ax(canvas,toolbar,fig,axes)
		self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
	def add_subplot_specific_label(self,val=""):
		fig,axes,canvas,toolbar,artists=self.canvas_frames.return_figure_info()
		vals=get_selected_vals(self.config_df,self.widget_dict,['subcre_num_row','subcre_num_cols','subcre_select_pos','subcre_select_axis','subcre_enter_label'])
		rows,cols,pos,axis,lab=[int(vals['subcre_num_row']),int(vals['subcre_num_cols']),int(vals['subcre_select_pos'])
								,vals['subcre_select_axis'],vals['subcre_enter_label']]
		if pos>0 and pos<=(rows*cols):
			if axis=='X-Axis':
				axes[pos].set_xlabel(lab)
			elif axis=='Y-Axis':
				axes[pos].set_ylabel(lab)
			else:
				axes[pos].set_title(lab)

			canvas.draw()#	Update the GUI plotting area
			toolbar.update()
			self.canvas_frames.set_figure_info(fig,axes,canvas,toolbar,artists)
		else:
			mb.showerror('Error','Enter a position between 0 and '+str(rows*cols))

#create an object out of the tkinter class and initiate its continuos checking and updating features
if __name__=="__main__":
	multiprocessing.freeze_support()
	app=Generic_Visualisation()
	app.mainloop()
