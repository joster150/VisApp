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
from tkinter.filedialog import askopenfilename,askdirectory,asksaveasfilename
from tkinter import simpledialog
from tkinter import messagebox as mb
from itertools import combinations
from itertools import repeat
import datetime as dt
from multiprocessing import Pool
import multiprocessing
import random
import copy
import seaborn as sns
import math
cores=multiprocessing.cpu_count()-1 or 1
NOTHING=object()
def read_file_into_df(address,head,sheet_identifier=0):
	file=pd.DataFrame()
	if address.endswith('.csv'):#		Decide what file type is being read and read it in different ways
		file=pd.read_csv(address,header=head,encoding='latin1')#	set the file variable to contain a Dataframe of the read data, where the header is chosen as row number head- where head is 0 by default (when first visulaised), then user selects which row the actual column headers are in
	elif address.endswith('.xlsx') or self.filename.endswith('xls'):#	If an excel file then
		try:
			file=pd.ExcelFile(address).parse(sheet_identifier,header=head,encoding='latin1')#	set the file variable to contain a Dataframe of the read data, where the header is chosen as row number head- where head is 0 by default (when first visulaised), then user selects which row the actual column headers are in
		except:
			file=pd.ExcelFile(address).parse(int(sheet_identifier),header=head,encoding='latin1')#	set the file variable to contain a Dataframe of the read data, where the header is chosen as row number head- where head is 0 by default (when first visulaised), then user selects which row the actual column headers are in
	else:#	Incase a different file type makes it way in
		print("Not a recognised file type")#	Tell the user that they can't read this file
		file='Re-choose a file'#	And that they should choose another
	return file

def assign_head_and_sheet(excel=False):
	head=simpledialog.askinteger('Input','Enter row number for header:')
	if excel:
		sheet=simpledialog.askstring('Input','Enter sheet name or number:')
	else:
		sheet=''
	return head,sheet
	
def get_on_select_values(event):
	sender=event.widget
	if len(sender.curselection())>1:
		return [sender.get(idx) for idx in sender.curselection()]#	set a variable to store the string values selected from the Listbox
	else:
		return sender.get(sender.curselection())
def get_selected_vals(config,dict,names):
	return_dict={}
	for widget_name,row in config['widgets'].loc[names].iterrows():
		if row.loc['widget_type']=='listbox':
			curselection=dict[row.loc['parent_frame']][row.loc['widget_type']][widget_name].curselection()
			curselection=[i for i in curselection if isinstance(i,int)]
			if len(curselection)>1:
				return_dict[widget_name]=[dict[row.loc['parent_frame']][row.loc['widget_type']][widget_name].get(i) for i in curselection]
			elif len(curselection)==1:
				return_dict[widget_name]=dict[row.loc['parent_frame']][row.loc['widget_type']][widget_name].get(curselection[0])
			else:
				return_dict[widget_name]=''
		elif row.loc['widget_type'] in ['optionmenu','checkbutton','spinbox','entry']:
			return_dict[widget_name]=dict[row.loc['parent_frame']][row.loc['widget_type']][widget_name].get()
	#print(return_dict)
	if len([*return_dict.keys()])>1:
		return return_dict
	else:
		return return_dict[names[0]]
def delete_and_insert_text(text,to_insert):
	text.delete(1.0,tk.END)
	width=int(round(float(text.winfo_width())/8.5))
	if isinstance(to_insert,pd.DataFrame) or isinstance(to_insert,pd.Series):
		pd.set_option('display.width',width)
		pd.set_option('display.expand_frame_repr',True)
	text.insert(tk.END,to_insert)
def delete_and_insert_listbox(listbox,to_insert):
	listbox.delete(0,tk.END)
	if isinstance(to_insert,list):
		listbox.insert(tk.END,*to_insert)
	else:
		listbox.insert(tk.END,to_insert)
def detect_only_common_cols(dict_of_dfs):
	common_cols=[*[*dict_of_dfs.values()][0].columns]
	for df in [*dict_of_dfs.values()]:
		common_cols=[i for i in common_cols if i in df.columns]
	return common_cols
def get_column_from_df(df,message):
	column=tk.StringVar()
	top=tk.Toplevel()
	top.grid_rowconfigure(0,weight=1)
	top.title("Select Column Pop-Up")
	lab=tk.Label(top,text=message)
	lab.grid(row=0,column=0)
	scroll=tk.Scrollbar(top)
	list=tk.Listbox(top,selectmode=tk.SINGLE,yscrollcommand=scroll.set,exportselection=False)
	list.bind('<<ListboxSelect>>',lambda val:return_and_destroy(column,val,top))
	scroll.config(command=list.yview)#		Configure the scroll bar to control the listbox
	list.grid(row=1,column=0,padx=10,pady=10)
	scroll.grid(row=1,column=1)
	list.insert(tk.END,*df.columns)
	top.wait_window()
	return column.get()
def return_and_destroy(var,val,toplev):
	sender=val.widget
	cur=sender.curselection()
	var.set(sender.get(cur))
	toplev.destroy()
def return_two_split_by_date(df,merge_col):
	date_col=get_column_from_df(df,'Choose the date column')
	df[date_col]=pd.to_datetime(df[date_col])
	df=df.sort_values(by=date_col)
	first=df.drop_duplicates(subset=merge_col,keep='first')
	second=df.drop_duplicates(subset=merge_col,keep='last')
	pre1=simpledialog.askstring('Prefix Naming','Enter prefix for first values:')
	pre2=simpledialog.askstring('Prefix Naming','Enter prefix for second values:')
	df=pd.merge(first,second,on=merge_col,how='inner',suffixes=('_'+pre1,'_'+pre2))
	return df
def assign_new_names_merge(cols,which):
	columns=[]
	cols=([cols] if not isinstance(cols,list) else cols)
	rename=mb.askyesno("Rename Question","Do you wish to rename the columns to be merged?")
	for x in cols:
		if x in which and rename:
			columns.append(simpledialog.askstring('Column re-naming','Enter a new name for column '+x))
		else:
			columns.append(x)
	return columns
def filter_condition(file,col,opt,value):
	condition=''
	if opt=='Is equal to':
			if file.dtypes.loc[col]=='int64':
				condition=file[col]==int(value)
			elif file.dtypes.loc[col]=='float':
				condition=file[col]==float(value)
			else:
				condition=file[col]==value
	elif opt=='Isnt equal to':
		if file.dtypes.loc[col]=='int64':
			condition=file[col]!=int(value)
		elif file.dtypes.loc[col]=='float':
			condition=file[col]!=float(value)
		else:
			condition=file[col]!=value
	elif opt=='Greater than(inc)':
		condition=file[col]>=float(value)
	elif opt=='Less than(inc)':
		condition=file[col]<=float(value)
	elif opt=='In list':
		if file.dtypes.loc[col]=='int64':
			condition=file[col].isin([int(i) for i in value.split(',')])
		elif file.dtypes.loc[col]=='float':
			condition=file[col].isin([float(i) for i in value.split(',')])
		else:
			condition=file[col].isin(value.split(','))
	elif opt=='Not In list':
		if file.dtypes.loc[col]=='int64':
			condition=~file[col].isin([int(i) for i in value.split(',')])
		elif file.dtypes.loc[col]=='float':
			condition=~file[col].isin([float(i) for i in value.split(',')])
		else:
			condition=~file[col].isin(value.split(','))		
	if not isinstance(condition,str):
		return condition
	else:
		print('Error')
def convert_standard_column_type(file,columns,chosen_type):
	df=file.copy()
	if chosen_type in ['Integer','Float']:
		for x in columns:
			df[x]=pd.to_numeric(df[x],downcast=chosen_type.lower(),errors='coerce')
	elif chosen_type in ['Object']:
		for x in columns:
			df[x]=df[x].astype(chosen_type.lower())
	return df
def convert_date_column_type(file,columns,format_given):
	with Pool(cores) as pool:
		results=pool.starmap(convert_date_column_type_pool,zip((np.array_split(file,cores)),repeat(columns),repeat(format_given)))
	return pd.concat(results)
def convert_date_column_type_pool(file,columns,format_given):
	df=file.copy()
	for x in columns:
		if df[x].dtype!='datetime64[ns]':
			if format_given=='%H%M%S':
				df[x]=df[x].apply(lambda t:time_convert(t,format_given))
			else:
				df[x]=pd.to_datetime(df[x],format=format_given,errors='coerce')
	return df
def time_convert(x,form):
	if len(str(x))==5:
		x='0'+str(x)
	elif len(str(x))==4:
		x='00'+str(x)
	elif len(str(x))==3:
		x='000'+str(x)
	elif len(str(x))==2:
		x='000'+str(x)
	elif len(str(x))==1:
		x='000'+str(x)
	try: 
		time=dt.datetime.time(pd.to_datetime(x,format=form))
	except:
		time=np.nan
	return time
def add_and_subtract(file,add_cols,sub_cols,date):
	with Pool(cores) as pool:
		results=pool.starmap(add_and_subtract_pool,zip((np.array_split(file,cores)),repeat(add_cols),repeat(sub_cols),repeat(date)))
	return pd.concat(results)
def add_and_subtract_pool(file,add_cols,sub_cols,date):
	df=file.copy()
	if add_cols!=['']:
		df['add_new']=df[add_cols].apply(lambda df:add_apply(df,date),axis=1)
	else:
		df['add_new']=('' if date else 0)
	if sub_cols!=['']:
		df['sub_new']=df[sub_cols].apply(lambda df:add_apply(df,date),axis=1)
	else:
		df['sub_new']=('' if date else 0)
	df['to_return']=df[['add_new','sub_new']].apply(lambda df:final_add_sub(df,date),axis=1)
	return df['to_return']
def add_apply(df,date):
	total=(''if date else 0)
	try:
		for x in df.index:
			if date:
				total=(dt.datetime.combine(dt.date.min, df[x]) if total=='' else total+dt.datetime.combine(dt.date.min, df[x]))	
			else:
				total+=float(df[x])
	except:
		total=np.nan
	return total
	
def final_add_sub(df,date):
	try:
		total= df['add_new']-df['sub_new']
		if date:
			total=total.total_seconds()/3600.0
			if total<0:
				total+=24
			return total
	except:
		return np.nan
def multiply_and_divide(file,mult_cols,div_cols):
	with Pool(cores) as pool:
		results=pool.starmap(multiply_and_divide_pool,zip((np.array_split(file,cores)),repeat(mult_cols),repeat(div_cols)))
	return pd.concat(results)
def multiply_and_divide_pool(file,mult_cols,div_cols):
	df=file.copy()
	df['mult_new']=(df[mult_cols].apply(mult_apply,axis=1) if mult_cols!=[''] else 1)
	df['div_new']=(df[div_cols].apply(mult_apply,axis=1) if div_cols!=[''] else 1)
	df['to_return']=df[['mult_new','div_new']].apply(final_mult_div,axis=1)
	return df['to_return']
def mult_apply(df):
	total=1
	try:
		for x in df.index:
			total*=float(df[x])
	except:
		total=np.nan
	return total
def final_mult_div(df):
	try:
		return df['mult_new']/df['div_new']
	except:
		return np.nan
def generate_random_color_dict(vals):
	dict={}
	for i in vals:
		dict[i]='#%02X%02X%02X' % (random.randint(0,255),random.randint(0,255),random.randint(0,255))
	return dict
class pump():#	Create a class for the pump object
	def __init__(self,type):#	Create the method which will run first when an object is made
		
		file_address=source+'/EHM_Config.xlsx'
		
		xls=pd.ExcelFile(file_address) # create a pandas exel object from this address
		
		fields=['Properties\Pump_Type',type]#	List of columns of interest
		
		df=xls.parse('Engine',header=0,usecols=fields) # create a pandas dataframe from the excel object by calling the relevent sheet, skipping non-important rows, setting the header to the first relevent row and ignoring rows starting with #
		
		df=df.set_index('Properties\Pump_Type')
		
		self.properties={}
		for x in df.index:
			self.properties[x]=df.loc[x][0]#	Create a pump attributes dict
		#print(self.properties)
		
		self.MuC=[77.5078, 0.0330, -1.9272, 3.4074e-11, 4.9707e-9]#	Create a list for storing the HMU viscosity coefficients
		
		self.Mu_ref = ((20 + self.MuC[0])/self.MuC[1])**self.MuC[2] + (20*self.MuC[3]+self.MuC[4])#		Store a reference (fuel at 20degc) viscosity 
		
		self.leakages=''#	Create a leakages attribute and initialise as 0
		
		self.pressure_rise=''#	Create a pressure rise attribute and initialise as 0
		
		self.delivered_flow=''#	Create a delivered flow attribute and initialise as 0
		
		self.art_flow=''
		
		self.unit_conv=99.7764#	Create an attribute that is the constant to facilitate the conversion from lb/h to ukgal/h by using a density term in kg/m^3
		
	def estimate_pressure_rise(self,volumetric_flow,P30):#	Create a function for estimateing the pressure rise across the pump. This takes flow numbers and pressure parameters.
		#print(P30.describe())
		#print(volumetric_flow.describe())
		self.pressure_rise=(((volumetric_flow/self.properties['Line_Losses_fn'])**2)+((volumetric_flow/(self.properties['NO.Burners']*self.properties['Single_Burner_fn']))**2)+((volumetric_flow/(self.properties['PRSOV_fn']))**2)+self.properties['MV_Pressure_Drop']+P30-self.properties['HP_Inlet'])#Sum the pressure drops between the pump outlet and where P30 is
		#measured and add p30. This estimates the HP pressure and then by taking away the pump inlet pressure we get the pressure rise. Store this in the previously created attribute.
		#print(self.pressure_rise.describe())
		try:
			self.pressure_rise.loc[self.pressure_rise<self.properties['Min_System_Pressure']]=self.properties['Min_System_Pressure']
		except:
			self.pressure_rise = (self.properties['Min_System_Pressure'] if self.pressure_rise<self.properties['Min_System_Pressure'] else self.pressure_rise)
		#print(self.pressure_rise.describe())
		return self.pressure_rise#	Return this value(s) to where the method was called.
		
		
	def calculate_TO_leaks(self,temps,density):#		Create a leakage estimation function by taking in
		# relevant HMU flow numbers, mass flows and volumetric flows. Some parasmeters have a default variable as there are two methods for passing in the leakages or flow numbers for these components.
		
		if not isinstance(self.pressure_rise,str): #If the pressure rise has been estimated (not still at initialised value) then
		
			Mu = ((temps + self.MuC[0])/self.MuC[1])**self.MuC[2] + (temps*self.MuC[3]+self.MuC[4])# 	Determine the viscosity of the fuel in the HMU at the given temp
			
			HMU_turb_IGPH=self.properties['HMU_Turbulent_fn']*((((self.pressure_rise**0.5)**2)/(density/1000))**0.5)#	Determine the turbulent leakages 
			
			HMU_lam_IGPH_fn1=self.properties['HMU_Laminar_fn']*(self.pressure_rise**0.5)*(self.Mu_ref/Mu)#	Determine the laminar HMU leakages based on using a normal flow number
			
			HMU_lam_IGPH_fn2=self.properties['HMU_Laminar_orig_fn']*self.pressure_rise*(self.Mu_ref/Mu)#	Determine the laminar HMU leakages based on a laminar specific flow number
			
			HMU_leakage=HMU_turb_IGPH + HMU_lam_IGPH_fn1+HMU_lam_IGPH_fn2#	Sum up the turbulent and laminar leakages
			
			TCC_static_IGPH=self.properties['TCC_fn']*(self.pressure_rise**0.5)#	Calculate the volumetric leakages from the TCCA using a flow number
			
			VSVA_max_IGPH=self.properties['VSVA_fn']*(self.pressure_rise**0.5)#	Calculate he volumetric leakages from the VSVA using a flow number 
			
			ACV_vol_flow=(self.properties['ACV_mass_flow']*self.unit_conv)/density#	Calculate the ACV volumetric flow by converting the given mass flow leakage
			
			TCC_vol_flow=(self.properties['TCC_mass_flow']*self.unit_conv)/density#	Calculate the volumetric leakages from the TCCA static mass leakages given
			
			self.leakages=HMU_leakage+TCC_static_IGPH+VSVA_max_IGPH+ACV_vol_flow+TCC_vol_flow+self.properties['VSVA_volumetric_flow']#	Sum up all the leakages to give the total leakages between the Pump and the metering point
			
		else:
		
			print('calculate pressure rise first')	#If the  pressure rise hasn't been estimated prompt this
			
			
	def calculate_delivered_flow(self,flows):#	Method for determining what flow was delivered by the pump
	
		if not isinstance(self.leakages,str) and not isinstance(self.pressure_rise,str):#		If the prerequisites to this calculation have already been calculated then
		
			self.delivered_flow=self.leakages+flows#	Sum the passed flows with the estimated leakages to get back to the delivered pump flow (excluding spill)
			
		else:
			print('require leakage and pressure estimations')#	Prompt user that the leakages and pressure rise must be calculated before this can
			
			
	def calculate_art_flow(self,speeds,temps,ART_speed=NOTHING,ART_temp=NOTHING,ART_deltap=NOTHING,temp_sensitivity=0.00008,pprv_fn=NOTHING):#	Method for estimating what flow we could expect if the pump was seen in an ART 
		
		if ART_speed is NOTHING:
			ART_speed=self.properties['PAT_MTO_speed']/1000
		if ART_temp is NOTHING:
			ART_temp=self.properties['PAT_MTO_temp']
		if ART_deltap is NOTHING:
			ART_deltap=self.properties['PAT_MTO_pressure_rise']
		if pprv_fn is NOTHING:
			pprv_fn=self.properties['PPRV_fn']
		
		if not isinstance(self.delivered_flow,str):#		Check if the delivered flow attribute has been calculated yet. If so then...
			current_speeds=((speeds/100)*self.properties['Pump_max_speed'])/1000#		Determine the pump speed based on the parsed percentage and the known 100% speed
			f_art=((current_speeds-(self.delivered_flow/self.properties['Pump_size']))/(self.pressure_rise**0.5))#	Determine the flow number seen at the current condition. to be assumed same in ART
			self.art_flow=self.properties['Pump_size']*(ART_speed-(f_art+temp_sensitivity*(ART_temp-temps))*(ART_deltap**0.5))-pprv_fn*(ART_deltap**0.5)#		Determine the ART flows by adjusting for speed and temperature differences and
			#by adding an assumption for the leakage through the pressure raising valve which is assumed open on ART (but not in service)
		else:
			print('requires delivered flow')#	If the delivered flow has not already been calculated prompt for it to be
	def set_pressure_rise(self,pressure_rise):#		Method for setting the pressure rise if already known.
		self.pressure_rise=pressure_rise#		set attribute to parsed parameter
	def set_delivered_flow(self,flow):#		Method for setting the delivered flow attribute if its already known
		self.delivered_flow=flow#	
class fuel_calcs():#	Create a class for making fuel objects
	def __init__(self,fuel_used):#	Method to initialise the fuel oject based on a mix of pump and fuel properties
	#Note that a density can be provided at either 0 or 15 degrees and one only the provided one will be used
		
		file_address=source+'/EHM_Config.xlsx'
		
		xls=pd.ExcelFile(file_address) # create a pandas exel object from this address
		
		fields=['Properties\Fuel_Used',fuel_used]#	List of columns of interest
		
		df=xls.parse('Fuel',header=0,usecols=fields) # create a pandas dataframe from the excel object by calling the relevent sheet, skipping non-important rows, setting the header to the first relevent row and ignoring rows starting with #
		
		df=df.set_index('Properties\Fuel_Used')
		
		properties={}
		
		for x in df.index:
			properties[x]=df.loc[x][0]#	Create a pump attributes dict

		if properties['0_degC_density']!='N/A':#	If the reference density was provided at 0 degc then
		
			self.fuel_density=properties['0_degC_density']# initialise the attribute to the parsed parameter
			
			self.stand_temp=0# initialise the attribute to the parsed parameter
			
		else:
			self.fuel_density=properties['15_degC_density']# initialise the attribute to the parsed parameter
			
			self.stand_temp=15# initialise the attribute to the parsed parameter
			
		self.temp_sensitivity=properties['temp_sensitivity']
			
		self.fuel_dRho_dt=properties['dRho_dt']# initialise the attribute to the parsed parameter
		
		self.unit_conv=99.7764#	Create an attribute that is the constant to facilitate the conversion from lb/h to ukgal/h by using a density term in kg/m^3
		
		
	def mass_to_volumetric(self,mass_flows,temps):#	Method for converting mass flows to volumetric flows
	
		return (mass_flows/self.current_density(temps))*self.unit_conv#	Return the calculated volumetric flows using the method for calculating current_density
		
	def volumetric_to_mass(self,vol_flows,temps):#	Method for converting mass flows to volumetric flows
	
		return (vol_flows/self.unit_conv)*self.current_density(temps)#	Return the calculated volumetric flows using the method for calculating current_density
	
	def current_density(self,temps):# Method for calculating the density of the fuel at the parsed remperature
	
		return self.fuel_density+self.fuel_dRho_dt*(temps-self.stand_temp)	#	Return the current density
def set_legend_from_dict(axes,ncol=4,fs=7,location='upper right'):
	for k,a in axes.items():
		current_handles,current_labels=a.get_legend_handles_labels()
		a.legend(handles=current_handles,loc=location,ncol=ncol,fontsize=fs,framealpha=0.5)
		a.set_title(k)
def update_fig_ax(canvas,toolbar,fig,axes):
	set_legend_from_dict(axes)
	fig.tight_layout()
	canvas.draw()#	Update the GUI plotting area
	toolbar.update()#	Update the GUI plotting toolbar
def get_axes_and_data_if_condition(option,axes,slice,subplot,fig):
	data=None
	if 'Specific Subplot' in option:
		if subplot==None:
			sub_pos=simpledialog.askinteger('Subplot Position Entry','Enter the subplot position between 1 and '+str(len([*axes.keys()])))
			try:
				if 'Replace' in option:
					axes[int(sub_pos)].clear()
				axes,data=[axes,{int(sub_pos):slice}]
			except:
				mb.showerror('Error','Either you have entered an invalid position or you are using a figure with a specially created subplot.')
		else:
			mb.showerror('Error','You can not subplot on a specific subplot position.')
	else:
		axes,data=get_axes_and_data(subplot,slice,fig)
	return (axes,data)

def get_axes_and_data(subplot,slice,fig):
	data={}
	axes={}
	if subplot!=None:
		subplots_num=len([*slice[subplot].unique()])
		rows=math.ceil(subplots_num**0.5)
		cols=math.ceil(subplots_num**0.5)
		for i,val in enumerate([*slice[subplot].unique()]):
			data[val]=slice.loc[slice[subplot]==val]
			axes[val]=fig.add_subplot(rows,cols,i+1)
	else:
		data['']=slice
		axes['']=fig.add_subplot(111)
	return [axes,data]
def hist(data,axes,X,Y,group,colour,fig):
	if len(X)>1 or len(Y)>1:
		mb.showerror('Error','You cannot select multiple columns for x or y')
	else:
		X=X[0]
		Y=Y[0]
		hist_orient=('horizontal' if Y!=None and X==None else 'vertical')
		X=(Y if Y!=None and X==None else X)
		for key,df in data.items():
			df[[v for v in [X,Y] if v!=None]]=df[[v for v in [X,Y] if v!=None]].apply(pd.to_numeric,errors='coerce')
			df=df.dropna()
			if not df.empty:
				for x in df[group].unique():
					df2=df.loc[df[group]==x]
					col=(df2[colour].iloc[0] if colour!=None else '#%02X%02X%02X' % (random.randint(0,255),random.randint(0,255),random.randint(0,255)))
					if Y==None or X==Y:
						axes[key].hist(x=X,color=col,orientation=hist_orient,bins=100,alpha=0.5,data=df2,label=str(x))
					else:
						hb=axes[key].hexbin(df2[X],df2[Y],gridsize=(100,20),cmap='Blues')
						fig.colorbar(hb)
					axes[key].set_xlabel((X if hist_orient=='veritical' else ''))
					axes[key].set_ylabel((Y if Y!=None else ''))
def cdf_plot(data,axes,X,Y,group,colour,fig):
	if X!=[None]:
		X=X[0]
		for key,df in data.items():
			df[[X]]=df[[X]].apply(pd.to_numeric,errors='coerce')
			df=df.dropna()
			if not df.empty:
				for x in df[group].unique():
					df2=df.loc[df[group]==x]
					col=(df2[colour].iloc[0] if colour!=None else '#%02X%02X%02X' % (random.randint(0,255),random.randint(0,255),random.randint(0,255)))
					sns.distplot(df2[X],hist_kws={'cumulative':True,'normed':True,'histtype':'step','alpha':0.8},kde_kws={'cumulative':True,'alpha':0.8,'label':str(x)},ax=axes[key])
				axes[key].set_xlabel(X)
def bar(data,axes,X,Y,group,colour,fig):
	if (not (X!=[None] and Y!=[None])) and (not (len(X)>1 or len(Y)>1)):
		X=X[0]
		Y=Y[0]
		for key,df in data.items():
			df=df.dropna()
			if not df.empty:
				for_palette=(df.set_index(group)[colour].drop_duplicates() if colour!=None and group!=None else None)
				pal=(for_palette.to_dict() if isinstance(for_palette,pd.Series) else None)
				sns.countplot(ax=axes[key],x=X,y=Y,hue=group,data=df,palette=pal)
				axes[key].set_xlabel((X if X!=None else ''))
				axes[key].set_ylabel((Y if Y!=None else ''))
	else:
		mb.showerror('Error','Select only one data column.')
def scatter(data,axes,X,Y,group,colour,fig,scatter=True):
	if X!=[None] and Y!=[None] and (not (len(X)>1 or len(Y)>1)):
		X=X[0]
		Y=Y[0]
		for key,df in data.items():
			to_num=[X,Y]
			if df[X].dtype=='datetime64[ns]':
				to_num=[Y]
			df[[v for v in to_num if v!=None]]=df[[v for v in to_num if v!=None]].apply(pd.to_numeric,errors='coerce')
			df=df.dropna()
			if not df.empty:
				for x in df[group].unique():
					df2=df.loc[df[group]==x]
					col=(df2[colour].iloc[0] if colour!=None else '#%02X%02X%02X' % (random.randint(0,255),random.randint(0,255),random.randint(0,255)))
					mark=('.' if scatter else 'None')
					lnstyle=('None' if scatter else '-')
					if df2[X].dtype=='datetime64[ns]':
						axes[key].plot_date(X,Y,color=col,marker=mark,linestyle=lnstyle,data=df2,label=str(x))
					else:
						axes[key].plot(X,Y,color=col,marker=mark,linestyle=lnstyle,data=df2,label=str(x))
					axes[key].set_xlabel(X)
					axes[key].set_ylabel(Y)
	else:
		mb.showerror('Error','Select one column for x and y.')
def line(data,axes,X,Y,group,colour,fig):
	scatter(data,axes,X,Y,group,colour,fig,scatter=False)
def reg_comp(data,axes,X,Y,group,colour,fig):
	if X!=[None] and Y!=[None] and (not (len(X)>1 or len(Y)>1)):
		scatter(data,axes,X,Y,group,colour,fig,scatter=True)
		X=X[0]
		Y=Y[0]
		contin=True
		orders=simpledialog.askstring('Polynomial Orders','Enter up to 4 polynomail orders to plot (seperated by commas no spaces):')
		try:
			orders=[int(i) for i in orders.split(',')] if ',' in orders else [int(orders)]
		except:
			contin=False
			mb.showerror('Error','Enter integers seperated by commas and no spaces')
		if contin:
			for key,df in data.items():
				df[[X,Y]]=df[[X,Y]].apply(pd.to_numeric,errors='coerce')
				df=df.dropna()
				if not df.empty:
					for x in df[group].unique():
						df2=df.loc[df[group]==x]
						col=(df2[colour].iloc[0] if colour!=None else '#%02X%02X%02X' % (random.randint(0,255),random.randint(0,255),random.randint(0,255)))
						models=[np.polyfit(df2[X].values,df2[Y].values,i) for i in orders]
						xx=np.linspace(df2[X].min(),df2[X].max(),100)
						styles=['-','--','-.',':']
						labels=['Order '+str(i)+': ' for i in orders]
						for p,poly in enumerate(models):
							yy=poly[-1]
							lab_string=''
							for i in range(len(poly)-1):
								yy+=(xx**(len(poly)-i-1))*poly[i]
								lab_string+=' + '+str(poly[i])+'x^'+str(len(poly)-i-1)
							lab_string+=' + '+str(poly[-1])
							axes[key].plot(xx,yy,color=col,marker='None',linestyle=styles[p],label=labels[p]+lab_string)
	
def swarm(data,axes,X,Y,group,colour,fig):
	box(data,axes,X,Y,group,colour,fig,box=False)
def box(data,axes,X,Y,group,colour,fig,box=True):
	if (X!=[None] or Y!=[None]) and (not (len(X)>1 or len(Y)>1)):
		X=X[0]
		Y=Y[0]
		for key,df in data.items():
			df=df.dropna()
			if not df.empty:
				if Y==None:
					df[X]=df[X].apply(pd.to_numeric,errors='coerce')
				else:
					df[Y]=df[Y].apply(pd.to_numeric,errors='coerce')
				df=df.dropna()
				for_palette=(df.set_index(group)[colour].drop_duplicates() if colour!=None and group!=None else None)
				pal=(for_palette.to_dict() if isinstance(for_palette,pd.Series) else None)
				if box:
					sns.boxplot(ax=axes[key],x=X,y=Y,hue=group,data=df,palette=pal)
				else:
					sns.swarmplot(ax=axes[key],x=X,y=Y,hue=group,data=df,palette=pal)
	else:
		mb.showerror('Error','Select one column for x and (or) y.')
def joint(data,axes,X,Y,group,colour,fig,canvas_frames):
	if X!=[None] and Y!=[None] and (not (len(X)>1 or len(Y)>1)):
		X=X[0]
		Y=Y[0]
		for key,df in data.items():
			df[X,Y]=df[X,Y].apply(pd.to_numeric,errors='coerce')
			df=df.dropna()
			for x in df[group].unique():
				df2=df.loc[df[group]==x]
				canvas_frames.add_seaborn_canvas(sns.jointplot(X,Y,data=df2,kind='reg'))
def pairplot(data,axes,X,Y,group,colour,fig,canvas_frames):
	if len(X+Y)>=2:
		for key,df in data.items():
			df[X+Y]=df[X+Y].apply(pd.to_numeric,errors='coerce')
			df=df.dropna()
			for_palette=(df.set_index(group)[colour].drop_duplicates() if colour!=None and group!=None else None)
			pal=(for_palette.to_dict() if isinstance(for_palette,pd.Series) else None)
			canvas_frames.add_seaborn_canvas(sns.pairplot(df,kind='reg',hue=group,palette=pal))
def stat_scatter(data,axes,X,Y,stat_chosen,group,colour,fig):
	for key,df in data.items():
			for x in df[group].unique():
				df[[v for v in [X,Y] if v!=None]]=df[[v for v in [X,Y] if v!=None]].apply(pd.to_numeric,errors='coerce')
				df=df.dropna()
				if not df.empty:
					df2=df.loc[df[group]==x]
					col=(df2[colour].iloc[0] if colour!=None else '#%02X%02X%02X' % (random.randint(0,255),random.randint(0,255),random.randint(0,255)))
					df2=df2.describe(include='all')
					axes[key].scatter(df2[X].loc[stat_chosen],df2[Y].loc[stat_chosen],color=col,label=str(x))
					axes[key].set_xlabel(stat_chosen+'_'+X)
					axes[key].set_ylabel(stat_chosen+'_'+Y)
def contour(data,axes,X,Y,group,colour,fig):
	if (X!=[None] or Y!=[None]) and (not (len(X)>1 or len(Y)>1)):
		X=X[0]
		Y=Y[0]
		single=(True if (Y!=None and X==None) or (X!=None and Y==None) else False)
		X=(Y if Y!=None and X==None else X)
		#cmaps=['Reds','Blues','Greens']
		i=0
		for key,df in data.items():
			df[[v for v in [X,Y] if v!=None]]=df[[v for v in [X,Y] if v!=None]].apply(pd.to_numeric,errors='coerce')
			df=df.dropna()
			if not df.empty:
				for x in df[group].unique():
					df2=df.loc[df[group]==x]
					if single:
						sns.kdeplot(df2[X],ax=axes[key],shade=True,shade_lowest=False,label=str(x))
					else:
						sns.kdeplot(df2[X],df2[Y],ax=axes[key],label=str(x))
					i+=1
	else:
		mb.showerror('Error','Select one column for x and (or) y.')
def convert_to_normal(df):
	mean=df.mean()
	std=df.std()
	return np.random.normal(mean,std,df.size),mean,std
def text_list_to_float_list(text):
	list=text.split('],[')
	for i,x in enumerate(list):
		remove_brackets=x.replace('[','').replace(']','')
		string_list=remove_brackets.split(',')
		list[i]=[float(val) for val in string_list]
	return list
def text_colour_label_to_tuple(text):
	list = text.split(',')
	colours=[]
	labels=[]
	for x in list:
		colours.append(x[:x.index(':')])
		labels.append(x[x.index(':')+1:])
	return colours,labels
def date_to_num(d):
	try:
		x=matplotlib.dates.datestr2num(d)
	except:
		x=matplotlib.dates.date2num(d)
	return x