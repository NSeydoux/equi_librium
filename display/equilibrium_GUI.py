#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import matplotlib
import Tkinter
from Tkconstants import HORIZONTAL, DISABLED
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg#, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from Tkinter import Tk, Button, Scale, Label, Checkbutton, IntVar, Toplevel, Entry
import tkMessageBox
from ttk import Frame
import tkFileDialog
from data_manager import Equilibrium_manager
from os import listdir
from os.path import isfile, join

class Equilibrium_GUI(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self.manager = Equilibrium_manager()
        # Slider setting the animation pace, in ms/frame
        self.slider = None
        self.diameter = None
        # Variables making sure data is properly set before rendering
        # associated with checkboxes to give user feedback
        self.configured = IntVar()
        self.configured.set(0)
        self.configured_box = None
        self.loaded = IntVar()
        self.configured.set(0)
        self.loaded_box = None
        self.init_UI(self.parent)
        self.test_auto_conf()
        #self.plot_figure(self.parent)

    def init_UI(self, frame):
        frame.title("Pegasus system")

        b_import = Button(master=frame, text='Importer', command=self.open_data_file)
        b_import.grid(row=1, column=0)
        b_export = Button(master=frame, text='Exporter', command=self.export_data)
        b_export.grid(row=1, column=1)
        b_play = Button(master=frame, text='Play', command=self.render)
        b_play.grid(row=1, column=2)
        b_display = Button(master=frame, text='Afficher', command=self.display)
        b_display.grid(row=1, column=3)
        b_import = Button(master=frame, text='Séparer pas/trot', command=self.open_split_file_popup)
        b_import.grid(row=1, column=5)
        b_config = Button(master=frame, text='Configurer', command=self.open_conf_file)
        b_config.grid(row=1, column=6)
        b_quit = Button(master=frame, text='Quitter', command=self._quit)
        b_quit.grid(row=1, column=7)

        slider_label_fast=Label(master=frame, text="Rapide")
        slider_label_fast.grid(row=2, column=2)
        slider_label_slow=Label(master=frame, text="Lent")
        slider_label_slow.grid(row=2, column=0)
        self.slider = Scale(master=frame, from_=150, to=15, orient=HORIZONTAL, length=100)
        self.slider.set(25)
        self.slider.grid(row=2, column=1)

        slider_label_large=Label(master=frame, text="Large")
        slider_label_large.grid(row=2, column=6)
        slider_label_tiny=Label(master=frame, text="Réduit")
        slider_label_tiny.grid(row=2, column=4)
        self.diameter = Scale(master=frame, from_=1, to=35, resolution=0.1, orient=HORIZONTAL, length=100)
        self.diameter.set(35)
        self.diameter.grid(row=2, column=5)

        self.configured_box = Checkbutton(master=frame, text="Configuré", variable=self.configured, state=DISABLED)
        self.configured_box.grid(row=3, column=0)

        self.loaded_box = Checkbutton(master=frame, text="Données chargées", variable=self.loaded,state=DISABLED)
        self.loaded_box.grid(row=3, column=1)

    def test_auto_conf(self):
        onlyfiles = [ f for f in listdir(".") if isfile(join(".",f)) ]
        if("equi_librium.conf" in onlyfiles):
            self.manager.read_config_file("equi_librium.conf")
            self.configured.set(1)

    def open_data_file(self):
        if(self.configured.get() == 1):
            ftypes = [('All files', '*')]
            dlg = tkFileDialog.Open(self, filetypes = ftypes)
            fl = dlg.show()
            if fl != '':
                self.manager.read_data_file(fl)
                self.loaded.set(1)
        else:
            tkMessageBox.showwarning("Configuration non effectuee", "Il faut configurer avant d'importer les données")

    def open_split_file_popup(self):
        w= popupWindow(self.master, self.manager)
        self.master.wait_window(w.top)

    def open_conf_file(self):
        ftypes = [('conf files', '*.conf'), ('All files', '*')]
        dlg = tkFileDialog.Open(self, filetypes = ftypes)
        fl = dlg.show()
        if fl != '':
            self.manager.read_config_file(fl)
            self.configured.set(1)

    def export_data(self):
        ftypes = [('All files', '*')]
        dlg = tkFileDialog.SaveAs(self, filetypes = ftypes)
        fl = dlg.show()
        if fl != '':
            self.manager.set_diameter(self.diameter.get())
            self.manager.export_chart(fl+".csv")

    def display(self):
        self.manager.set_diameter(self.diameter.get())
        self.manager.display_data()

    def render(self):
        self.manager.render_animation(self.slider.get())
        #self.plot_figure(self.parent)

    def plot_figure(self, frame):
        f = Figure(figsize=(5,4), dpi=100)
        #f = self.manager.render_animation()
        #a = f.add_subplot(111)
        #t = arange(0.0,3.0,0.01)
        #s = sin(2*pi*t)

        #a.plot(t,s)
        canvas = FigureCanvasTkAgg(f, master=frame)
        canvas.show()
        canvas.get_tk_widget().grid(row=0, columnspan=5)
        # canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        # toolbar = NavigationToolbar2TkAgg( canvas, root )
        # toolbar.update()
        # canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        canvas._tkcanvas.grid(row=0, columnspan=5)

        def on_key_event(event):
            print('you pressed %s'%event.key)
            key_press_handler(event, canvas)#, toolbar)
        canvas.mpl_connect('key_press_event', on_key_event)

    def _quit(self):
        self.quit()     # stops mainloop
        self.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstat

class popupWindow(object):
    def __init__(self,master,manager):
        self.master = master
        self.manager=manager
        top=self.top=Toplevel(master)
        Label(top,text="Début du pas (min:sec)").pack()
        self.pas_d=Entry(top)
        self.pas_d.pack()
        Label(top,text="Fin du pas (min:sec)").pack()
        self.pas_f=Entry(top)
        self.pas_f.pack()
        Label(top,text="Début du trot (min:sec)").pack()
        self.trot_d=Entry(top)
        self.trot_d.pack()
        Label(top,text="Fin du trot (min:sec)").pack()
        self.trot_f=Entry(top)
        self.trot_f.pack()
        b1=Button(top,text='Séparer',command=self.split_data_file)
        b1.pack()

    def split_data_file(self):
        ftypes = [('All files', '*')]
        dlg = tkFileDialog.Open(self.master, filetypes = ftypes)
        fl = dlg.show()
        if fl != '':
            self.manager.split_data_file(fl, self.pas_d.get(), self.pas_f.get(), self.trot_d.get(), self.trot_f.get())
        self.top.destroy()

def main():
    root = Tk()
    Equilibrium_GUI(root)
    Tkinter.mainloop()

if __name__ == '__main__':
    main()