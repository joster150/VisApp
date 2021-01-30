import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt#	Import matplotlib for data visualisation
from matplotlib.figure import Figure#	Import matplotlib's figure directly as part of plot embedding in GUI
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)#	import two matplotlib backends for using plots in Tkinter GUIs
matplotlib.use('TkAgg')#can use backend
plt.switch_backend('Tkagg')
class matplotlib_creations():
	def __init__(self,parent_frame):
		self.current_frame=0
		self.add_canvas_count=0
		self.parent=parent_frame
		self.frame_dict={}
		self.frame_dict[0]=tk.Frame(self.parent)
		self.frame_dict[0].grid(row=0,column=0,sticky='NSEW')
		self.fig_dict={}
		self.fig_dict[0]=Figure(figsize=(5,4.5),dpi=100)
		self.artist_dict={}
		self.artist_dict[0]=[]

		self.canvas_dict={}
		self.canvas_dict[0]=FigureCanvasTkAgg(self.fig_dict[0],self.frame_dict[0])
		self.canvas_dict[0].get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=True)
		self.axes_dict={}
		self.axes_dict[0] ={'':self.fig_dict[0].add_subplot(111)}
		self.axes_dict[0][''].plot([1,2,3,4,5,6,7,8],[5,6,7,8,7,8,9,2])
		self.fig_dict[0].tight_layout()
		self.canvas_dict[0].draw()
		toolbar_frame=tk.Frame(self.frame_dict[0])
		self.toolbar_dict={}
		self.toolbar_dict[0]=NavigationToolbar2Tk(self.canvas_dict[0],toolbar_frame)
		self.toolbar_dict[0].update()
		toolbar_frame.pack(side=tk.BOTTOM,fill=tk.X,expand=tk.FALSE)
	def add_canvas(self,pop_out=False):
		self.current_frame+=1
		name=self.current_frame
		self.artist_dict[name]=[]
		if not pop_out:
			self.frame_dict[name]=tk.Frame(self.parent)
			self.frame_dict[name].grid(row=0,column=0,sticky='NSEW')
		else:
			self.frame_dict[name]=tk.Toplevel(self.parent)
		self.fig_dict[name]=Figure(figsize=(5,2.5),dpi=100)
		self.canvas_dict[name]=FigureCanvasTkAgg(self.fig_dict[name],self.frame_dict[name])
		self.canvas_dict[name].get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=True)
		self.axes_dict[name] = {'':self.fig_dict[name].add_subplot(111)}
		self.canvas_dict[name].draw()
		toolbar_frame=tk.Frame(self.frame_dict[name])
		self.toolbar_dict[name]=NavigationToolbar2Tk(self.canvas_dict[name],toolbar_frame)
		self.toolbar_dict[name].update()
		toolbar_frame.pack(side=tk.BOTTOM,fill=tk.X,expand=tk.FALSE)
		if not pop_out:
			self.raise_canvas(name)
		#print(self.frame_dict.keys())
	def add_seaborn_canvas(self,fig):
		self.current_frame+=1
		name=self.current_frame
		self.artist_dict[name]=[]
		self.frame_dict[name]=tk.Toplevel(self.parent)
		self.fig_dict[name]=fig.fig
		self.canvas_dict[name]=FigureCanvasTkAgg(self.fig_dict[name],self.frame_dict[name])
		self.canvas_dict[name].get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=True)
		try:
			self.axes_dict[name] = {'':fig.axes[0,0]}
		except:
			self.axes_dict[name]={'':fig.ax_joint}
		self.canvas_dict[name].draw()
		toolbar_frame=tk.Frame(self.frame_dict[name])
		self.toolbar_dict[name]=NavigationToolbar2Tk(self.canvas_dict[name],toolbar_frame)
		self.toolbar_dict[name].update()
		toolbar_frame.pack(side=tk.BOTTOM,fill=tk.X,expand=tk.FALSE)
		#print(self.frame_dict.keys())
	def raise_canvas(self,name):
		frame = self.frame_dict[name] #retrieve the frame from dictionary using the parsed key
		frame.tkraise()# raise the frame to the front
	def previous_canvas(self):
		if self.current_frame!=0:
			self.current_frame-=1
			while True:
				try:
					self.raise_canvas(self.current_frame)
					break
				except:
					self.current_frame-=1
	def next_canvas(self):
		if self.current_frame!=max(self.frame_dict):
			self.current_frame+=1
			while True:
				try:
					self.raise_canvas(self.current_frame)
					break
				except:
					self.current_frame+=1
	def remove_canvas(self):
		if self.current_frame!=0:
			self.frame_dict[self.current_frame].destroy()
			del self.toolbar_dict[self.current_frame]
			del self.axes_dict[self.current_frame]
			del self.canvas_dict[self.current_frame]
			del self.fig_dict[self.current_frame]
			del self.frame_dict[self.current_frame]
			self.previous_canvas()
			#print(self.frame_dict.keys())
	def return_figure_info(self):
		return self.fig_dict[self.current_frame],self.axes_dict[self.current_frame],self.canvas_dict[self.current_frame],self.toolbar_dict[self.current_frame],self.artist_dict[self.current_frame]
	def set_figure_info(self,fig,axes,canvas,toolbar,artists):
		self.fig_dict[self.current_frame]=fig
		self.axes_dict[self.current_frame]=axes
		self.canvas_dict[self.current_frame]=canvas
		self.toolbar_dict[self.current_frame]=toolbar
		self.artist_dict[self.current_frame]=artists
