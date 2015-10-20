#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import matplotlib
import Tkinter
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg#, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from Tkinter import Tk, Button
from ttk import Frame
import tkFileDialog
from data_manager import Equilibrium_manager

class Equilibrium_GUI(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self.manager = Equilibrium_manager()
        self.init_UI(self.parent)
        #self.plot_figure(self.parent)

    def init_UI(self, frame):
        #self.wm_title("Equi-librium")
        frame.title("Pegasus system")
        frame.columnconfigure(0, pad=3)
        frame.columnconfigure(1, pad=3)
        frame.columnconfigure(2, pad=3)
        frame.columnconfigure(3, pad=3)
        frame.columnconfigure(4, pad=3)
        frame.columnconfigure(5, pad=3)

        frame.rowconfigure(0, pad=3)
        frame.rowconfigure(1, pad=3)

        b_import = Button(master=frame, text='Importer', command=self.open_data_file)
        b_import.grid(row=1, column=0)
        b_export = Button(master=frame, text='Exporter', command=self.export_data)
        b_export.grid(row=1, column=1)
        b_play = Button(master=frame, text='Play', command=self.render)
        b_play.grid(row=1, column=2)
        #b_pause = Button(master=frame, text='Pause')
        #b_pause.grid(row=1, column=3)
        b_config = Button(master=frame, text='Configurer', command=self.open_conf_file)
        b_config.grid(row=1, column=4)
        b_quit = Button(master=frame, text='Quitter', command=self._quit)
        b_quit.grid(row=1, column=5)

    def open_data_file(self):
        ftypes = [('All files', '*')]
        dlg = tkFileDialog.Open(self, filetypes = ftypes)
        fl = dlg.show()

        if fl != '':
            self.manager.read_data_file(fl)

    def open_conf_file(self):
        ftypes = [('conf files', '*.conf'), ('All files', '*')]
        dlg = tkFileDialog.Open(self, filetypes = ftypes)
        fl = dlg.show()
        if fl != '':
            self.manager.read_config_file(fl)

    def export_data(self):
        ftypes = [('All files', '*')]
        dlg = tkFileDialog.SaveAs(self, filetypes = ftypes)
        fl = dlg.show()
        if fl != '':
            self.manager.export_chart(fl)

    def render(self):
        self.manager.render_animation()
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

def main():
    root = Tk()
    Equilibrium_GUI(root)
    Tkinter.mainloop()

if __name__ == '__main__':
    main()