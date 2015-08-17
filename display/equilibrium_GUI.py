#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import matplotlib
import Tkinter
matplotlib.use('TkAgg')
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg#, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from Tkinter import Tk, Button
from ttk import Frame
import tkFileDialog
from matplotlib import pyplot as plt
from matplotlib import animation
import ConfigParser

# Intervalle entre deux instants de mesures (en ms)
INTERVAL = 50
# def openFile():

class Equilibrium_manager():

    def __init__(self):
        self.conf_map = {}
        self.sensor_values = []
        self.sensor_centers = []
        self.sensor_centers_x = []
        self.sensor_centers_y = []

                # Cette fonction retourne les coordonnées du centre du carré (i,j) de la grille
    def get_square_center(self, i, j):
        return [self.conf_map.get("square_side")*(i+0.5), self.conf_map.get("square_side")*(j+0.5)]

    def read_config_file(self, input_path):
        # le fichier de config se présente comme suit :
        # - nombre de cases en largeur
        # - nombre de cases en hauteur
        # - nombre de capteurs
        # - ligne par ligne, les coordonnées en [x,y] de chaque capteur -> on utilise eval
        config = ConfigParser.ConfigParser()
        config.read(input_path)
        largeur = int(config.get("GRID_GEOMETRY", "grid_length"))
        hauteur = int(config.get("GRID_GEOMETRY", "grid_heigth"))
        nbr_capteurs = int(config.get("GRID_GEOMETRY", "sensors_number"))
        sensor_layout = eval(config.get("SENSOR_LAYOUT", "layout"))
        square_side = float(config.get("GRID_GEOMETRY", "square_side"))
#         config = open(input_path, "r")
#         largeur = int(config.readline())
#         hauteur = int(config.readline())
#         nbr_capteurs = int(config.readline())
#         sensors_layout = []
#         for i in range(nbr_capteurs):
#             sensors_layout.append(eval(config.readline()))
        self.conf_map =  {"largeur":largeur,
                          "hauteur":hauteur,
                          "nbr_capteurs":nbr_capteurs,
                          "sensors_layout":sensor_layout,
                          "square_side":square_side,
                          "center":[float(largeur*square_side)/2.0, float(hauteur*square_side)/2.0]}

    def read_data_file(self, input_path):
        # chaque ligne comporte une série de valeurs, chacune liée à un capteur.
        # La première valeur correspond au premier capteur, la seconde au second etc
        # les valeurs sont séparées par des virgules
        data_file = open(input_path, "r")
        data = data_file.readlines()
        sensor_values = []
        for line in data:
            sensor_values.append(line.split(","))
            # on converti la dernière ligne de valeurs mesurées en integer
            for i in range(len(sensor_values[len(sensor_values)-1])):
                # 250 est un choix arbitraire de mesure minimale, et sert donc de 0 : pour une valeur de résistance de 250, le carré sera blanc
                # plus la valeur de résistance est élevée, plus le carré sera noir
                sensor_values[len(sensor_values)-1][i] = 250.0/float(sensor_values[len(sensor_values)-1][i])
                # UNCOMMENT ME for test files
                # sensor_values[len(sensor_values)-1][i] = float(sensor_values[len(sensor_values)-1][i])
        self.sensor_values = sensor_values

#     def compute_center_mass(self):
#         for i in range(len(self.sensor_values)):
#             center = (0,0)
#             sum = 0
#             for j in range(len(self.sensor_values[i])):
#                 center
    def export_chart(self, dest_path):
        dest_file = open(dest_path, "w")
        dest_file.write("Temps (ms), Centre gravité horizontal (cm), Centre gravité vertical (cm)")
        for i in range(len(self.sensor_values)-1):
            mass_center_x = 0
            mass_center_y = 0
            sum_x = 0
            sum_y = 0
            for j in range(self.conf_map.get("largeur")):
                for k in range(self.conf_map.get("hauteur")):

                    # le placement des capteurs est stocké dans l'ordre dans la map de configuration
                    # donc cconfig_map.get("sensors_layout").index([j,k]) retourne l'index du capteur situé en j,k
                    if([j, k] in self.conf_map.get("sensors_layout")):
                        center = self.get_square_center(j, k)
                        color = self.sensor_values[i%len(self.sensor_values)][self.conf_map.get("sensors_layout").index([j,k])]
                        mass_center_x += color*center[0]
                        sum_x += color
                        mass_center_y += color*center[1]
                        sum_y += color
                    else:
                        # Dans ce cas, pas de capteur aux coordonnées demandées
                        color = 1
            if(sum_x > 0):
                mass_center_x = float(float(mass_center_x)/float(sum_x))
            if(sum_y > 0):
                mass_center_y = float(float(mass_center_y)/float(sum_y))
            if(sum_x > 0 or sum_y > 0):
                dest_file.write(str(i*50)+","+str(mass_center_x)+","+str(mass_center_y)+"\n")



    def render_animation(self):
        #config_map = self.read_config_file("/home/seydoux/Programmation/Scripts_python/liclipse_workspace/Equilibrium_GUI/config")
        #print self.conf_map
        #data = self.read_data_file("/home/seydoux/Programmation/Scripts_python/liclipse_workspace/Equilibrium_GUI/values")
        #print self.sensor_values

        # Définition de la colormap
        cdict ={
        'red':   [(0.0,  0.0, 0.0),
                   (0.5,  1.0, 1.0),
                   (1.0,  1.0, 1.0)],

         'green': [(0.0,  0.0, 0.0),
                   (0.25, 0.0, 0.0),
                   (0.75, 1.0, 1.0),
                   (1.0,  1.0, 1.0)],

         'blue':  [(0.0,  0.0, 0.0),
                   (0.5,  0.0, 0.0),
                   (1.0,  1.0, 1.0)]
        }

        #color_map = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 1024)
        #color_converter = matplotlib.cm.ScalarMappable(cmap=color_map)
        #color_converter.autoscale()
        #plt.colorbar(mappable=color_converter)
        #plt.pcolor(cm)
        #plt.colorbar()

        fig = plt.figure()
        fig.set_dpi(100)
        ax = plt.axes(xlim=(0, self.conf_map.get("largeur")*self.conf_map.get("square_side")), ylim=(0, self.conf_map.get("hauteur")*self.conf_map.get("square_side")+5))
        time_text = ax.text(0, 0, '',horizontalalignment='left',verticalalignment='top', transform=ax.transAxes)
        # values = []
        # for i in range(10):
        #     values.append([i*j for j in range(10)])
        #print values

        patches = []
        for i in range(self.conf_map.get("largeur")):
            patches.append([])
            for j in range(self.conf_map.get("hauteur")):
                patches[i].append(plt.Rectangle((i*self.conf_map.get("square_side"), j*self.conf_map.get("square_side")), self.conf_map.get("square_side"), self.conf_map.get("square_side"), 0.0))
                # Le centre de gravité se trouve à la moitié du rectangle en x et en y
                self.sensor_centers.append([i*self.conf_map.get("square_side")+self.conf_map.get("square_side")/2, j*self.conf_map.get("square_side")+self.conf_map.get("square_side")/2])
                self.sensor_centers_x.append(i*self.conf_map.get("square_side")+self.conf_map.get("square_side")/2)
                self.sensor_centers_y.append(j*self.conf_map.get("square_side")+self.conf_map.get("square_side")/2)

        def init():
            for i in range(self.conf_map.get("largeur")):
                for j in range(self.conf_map.get("hauteur")):
                    ax.add_patch(patches[i][j])
            return [val for sublist in patches for val in sublist]

        def animate(i):
        #     x, y = patch.center
        #     x = 5 + 3 * np.sin(np.radians(i))
        #     y = 5 + 3 * np.cos(np.radians(i))
        #     patch.center = (x, y)
        #     patch.set_color(str(float((i%99))/100.0))
        #     print float((i%99))/100.0
        #     return patch
            mass_center_x = 0
            mass_center_y = 0
            sum_x = 0
            sum_y = 0
            #time_text.set_text("test")
            plt.title("Time : "+str((i*INTERVAL)/1000)+"s")
            for j in range(self.conf_map.get("largeur")):
                for k in range(self.conf_map.get("hauteur")):
                    #patches[j][k].set_color((str(float(((j*k+i)%100))/100.0)))
                    #color = float(values[(j+i)%10][(k+i)%10])/81.0
                    #print(config_map.get("largeur")*j+k)
                    #color = data[i][config_map.get("largeur")*j+k]

                    # le placement des capteurs est stocké dans l'ordre dans la map de configuration
                    # donc cconfig_map.get("sensors_layout").index([j,k]) retourne l'index du capteur situé en j,k
                    if([j, k] in self.conf_map.get("sensors_layout")):
                        center = self.get_square_center(j, k)
                        color = self.sensor_values[i%len(self.sensor_values)][self.conf_map.get("sensors_layout").index([j,k])]
                        mass_center_x += color*center[0]
                        sum_x += color
                        mass_center_y += color*center[1]
                        sum_y += color
                    else:
                        # Dans ce cas, pas de capteur aux coordonnées demandées
                        color = 1
                    patches[j][k].set_color((str(color)))
                    # FIXME : Comment marche une colormap ?
                    #print color_converter.to_rgba([color])
                    #print color_converter.to_rgba(str(color))
                    #print "-----------"
                    #patches[j][k].set_color(color_converter.to_rgba(color))
            if(sum_x > 0):
                mass_center_x = float(float(mass_center_x)/float(sum_x))
            if(sum_y > 0):
                mass_center_y = float(float(mass_center_y)/float(sum_y))
            if(sum_x > 0 or sum_y > 0):
                plt.plot([mass_center_x],[mass_center_y], '+b')

            return [val for sublist in patches for val in sublist]
            #return [val for sublist in patches for val in sublist] + [time_text]

        anim = animation.FuncAnimation(fig, animate,
                                       init_func=init,
                                       #frames=360,
                                       interval=INTERVAL,
                                       blit=False)

        plt.plot(self.sensor_centers_x, self.sensor_centers_y, 'xr')
        plt.plot([self.conf_map.get("center")[0]], [self.conf_map.get("center")[1]], 'ob')
        plt.show()
        #return plt

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
        b_pause = Button(master=frame, text='Pause')
        b_pause.grid(row=1, column=3)
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
    ex = Equilibrium_GUI(root)
    Tkinter.mainloop()

if __name__ == '__main__':
    main()