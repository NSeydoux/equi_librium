#!/usr/bin/env python
# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import ConfigParser
import math

# Intervalle entre deux instants de mesures (en ms)
INTERVAL = 25
# Valeur du blanc : à partir de cette valeur, la couleur associée à la résistance sera blanc
MIN_SENSOR = 500.0 # Original : 250.0
MAX_SENSOR = 40000.0

# Caractéristiques de la fonction de transformation des valeurs en couleurs
# coeff directeur
COEF_DIR = -1.0/(math.log(MAX_SENSOR)-math.log(MIN_SENSOR))
# ordonnéeà l'origine
ORD_A_O = 1.0 - COEF_DIR*math.log(MIN_SENSOR)

class Equilibrium_manager():

    def __init__(self):
        self.conf_map = {}
        self.raw_measures = []
        self.sensor_values = []
        self.color_level = []
        self.sensor_centers = []
        self.sensor_centers_x = []
        self.sensor_centers_y = []
        # Default values
        self.INTERVAL = INTERVAL
        self.MAX_SENSOR = MAX_SENSOR
        self.MIN_SENSOR = MIN_SENSOR

    # Cette fonction retourne les coordonnées du centre du carré (i,j) de la grille
    def get_square_center(self, i, j):
        return [self.conf_map.get("square_side")*(i+0.5), self.conf_map.get("square_side")*(j+0.5)]

    def read_config_file(self, input_path):
        # le fichier de config se présente comme suit :
        # - nombre de cases en largeur
        # - nombre de cases en hauteur
        # - nombre de capteurs
        # - ligne par ligne, les coordonnées en [x,y] de chaque capteur -> on utilise eval
        print "Lecture de la configuration ..."
        config = ConfigParser.ConfigParser()
        config.read(input_path)
        largeur = int(config.get("GRID_GEOMETRY", "grid_length"))
        hauteur = int(config.get("GRID_GEOMETRY", "grid_heigth"))
        nbr_capteurs = int(config.get("GRID_GEOMETRY", "sensors_number"))
        sensor_layout = eval(config.get("SENSOR_LAYOUT", "layout"))
        # On permute les valeurs de x et y du layout
        for i in range(len(sensor_layout)):
            tmp = sensor_layout[i][0]
            sensor_layout[i][0] = sensor_layout[i][1]
            sensor_layout[i][1] = tmp
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
        print "Lecture de la configuration : OK"

    def convert_sensor_value_to_color(self, value):
        # MIN_SENSOR est un choix arbitraire de mesure minimale, et sert donc de 0 : pour une valeur de résistance de 250, le carré sera blanc
        # plus la valeur de résistance est élevée, plus le carré sera noir
        #sensor_values[len(sensor_values)-1][i] = MIN_SENSOR/float(sensor_values[len(sensor_values)-1][i])
        #return math.exp(-1.0/float(value))
        # La fonction permettant de définir la valeur du niveau de gris est une fonction définie par morceaux.
        # Entre self.MIN_SENSOR et self.MAX_SENSOR, on définit une fonction linéaire sur une échelle logarithmique, allant de 1 à 0
        color = 0.0
        if(value < self.MIN_SENSOR):
            color = 1.0
        elif(value < self.MAX_SENSOR):
            color = COEF_DIR*math.log(value)+ORD_A_O
        else:
            color = 0.0
#        return self.MIN_SENSOR/float(value)
        return color

    def normalize_sensor_value(self, value):
        return self.MIN_SENSOR/float(value)

    def read_data_file(self, input_path):
        # chaque ligne comporte une série de valeurs, chacune liée à un capteur.
        # La première valeur correspond au premier capteur, la seconde au second etc
        # les valeurs sont séparées par des virgules
        print "Lecture d'un fichier de donnees..."
        data_file = open(input_path, "r")
        data = data_file.readlines()
        raw_measures = []
        sensor_values = []
        color_values = []
        for line in data:
            line = line.rstrip()
            if(len(line) > 32):
                raw_measures.append(map(float, line.split(",")))
                sensor_values.append(map(self.normalize_sensor_value, raw_measures[-1]))
                color_values.append(map(self.convert_sensor_value_to_color, raw_measures[-1]))
            self.sensor_values = sensor_values
            self.color_level = color_values
        print "Loaded : "+str(len(sensor_values))+" values\n"

    # Helper function, transforms a time in min:sec format to a sec format
    def convert_min_to_sec(self, time):
        (min_, sec) = time.split(":")
        min_ = int(min_)
        sec = 60*min_+int(sec)
        return sec

    # Sépare le trot du pas facilement à partir des mesures de temps faites sur le terrain, au format min:sec
    def split_data_file(self, input_path, start1, fin1, start2, fin2):
        source_file = open(input_path, "r")
        pas = []
        trot = []
        # INTERVAL is in ms, so let's convert everythong to ms
        start_pas = self.convert_min_to_sec(start1)*1000
        fin_pas = self.convert_min_to_sec(fin1)*1000
        start_trot= self.convert_min_to_sec(start2)*1000
        fin_trot = self.convert_min_to_sec(fin2)*1000
        data = source_file.readlines()
        elapsed_time = 0
        for line in data:
            #line = line.rstrip()
            if(len(line) > 32):
                elapsed_time += self.INTERVAL
                if (elapsed_time > start_pas and elapsed_time < fin_pas):
                    pas.append(line)
                elif(elapsed_time > start_trot and elapsed_time < fin_trot):
                    trot.append(line)
        open(input_path+"_PAS", "w").writelines(pas)
        open(input_path+"_TROT", "w").writelines(trot)

    def export_chart(self, dest_path):
        # Les deux listes suivantes vont accueillir les séries de données
        # On les utilisera pour calculer moyenne et écart-type
        x_axis = []
        y_axis = []
        for i in range(len(self.sensor_values)-1):
            mass_center_x = 0
            mass_center_y = 0
            sum_x = 0
            sum_y = 0
            for j in range(self.conf_map.get("largeur")):
                for k in range(self.conf_map.get("hauteur")):
                    # le placement des capteurs est stocké dans l'ordre dans la map de configuration
                    # donc config_map.get("sensors_layout").index([j,k]) retourne l'index du capteur situé en j,k
                    if([j, k] in self.conf_map.get("sensors_layout")):
                        center = self.get_square_center(j, k)
                        #color = self.sensor_values[i%len(self.sensor_values)][self.conf_map.get("sensors_layout").index([j,k])]
                        value = self.sensor_values[i%len(self.sensor_values)][self.conf_map.get("sensors_layout").index([j,k])]
                        mass_center_x += value*center[0]
                        sum_x += value
                        mass_center_y += value*center[1]
                        sum_y += value
            if(sum_x > 0):
                mass_center_x = float(float(mass_center_x)/float(sum_x))
            if(sum_y > 0):
                mass_center_y = float(float(mass_center_y)/float(sum_y))
            if(sum_x > 0 or sum_y > 0):
                x_axis.append(mass_center_x)
                y_axis.append(mass_center_y)
        dest_file = open(dest_path, "w")
        np_x = np.array(x_axis)
        average_x = np.mean(np_x)
        variance_x = np.var(np_x)
        ecart_type_x = np.std(np_x)
        np_y = np.array(y_axis)
        average_y = np.mean(np_y)
        variance_y = np.var(np_y)
        ecart_type_y = np.std(np_y)
        # On écrit sur les premières lignes du fichier les statistiques intéressantes
        dest_file.write(";Moyenne;Variance;Écart-type\n")
        dest_file.write("Axe x;"+str(average_x).replace(".", ",")+";"+str(variance_x).replace(".",",")+";"+str(ecart_type_x).replace(".", ",")+"\n")
        dest_file.write("Axe y;"+str(average_y).replace(".", ",")+";"+str(variance_y).replace(".",",")+";"+str(ecart_type_y).replace(".", ",")+"\n")
        # On donne ensuite l'ensemble des données, qui permettent de tracer les graphiques si nécessaire
        dest_file.write("Temps (ms); Centre gravité horizontal (cm); Centre gravité vertical (cm)\n")
        for i in range(len(x_axis)):
            dest_file.write(str(i*self.INTERVAL)+";"+str(x_axis[i]).replace(".", ",")+";"+str(y_axis[i]).replace(".", ",")+"\n")

    def render_animation(self, interval=-1):
        if(interval==-1):
            interval=self.INTERVAL
        fig = plt.figure()
        fig.set_dpi(100)
        ax = plt.axes(xlim=(0, self.conf_map.get("largeur")*self.conf_map.get("square_side")), ylim=(0, self.conf_map.get("hauteur")*self.conf_map.get("square_side")+5))
        time_text = ax.text(0, 0, '',horizontalalignment='left',verticalalignment='top', transform=ax.transAxes)

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
            plt.title("Time : "+str((i*interval)/1000)+"s")
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
                        color = self.color_level[i%len(self.sensor_values)][self.conf_map.get("sensors_layout").index([j,k])]
                        value = self.sensor_values[i%len(self.sensor_values)][self.conf_map.get("sensors_layout").index([j,k])]
                        mass_center_x += value*center[0]
                        sum_x += value
                        mass_center_y += value*center[1]
                        sum_y += value
                    else:
                        # Dans ce cas, pas de capteur aux coordonnées demandées
                        color = 1
                    if(color > 1):
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
        #anim=
        #print "Interval : "+str(INTERVAL)
        anim=animation.FuncAnimation(fig, animate, frames=None, #frames=360,
                                       init_func=init, fargs=None,
                                       save_count=None, interval=interval,
                                       #blit=False)
                                       repeat=False)

        plt.plot(self.sensor_centers_x, self.sensor_centers_y, 'xr')
        plt.plot([self.conf_map.get("center")[0]], [self.conf_map.get("center")[1]], 'ob')
        plt.show()

    def online_animation(self):
        fig = plt.figure()
        fig.set_dpi(100)
        ax = plt.axes(xlim=(0, self.conf_map.get("largeur")*self.conf_map.get("square_side")), ylim=(0, self.conf_map.get("hauteur")*self.conf_map.get("square_side")+5))
        time_text = ax.text(0, 0, '',horizontalalignment='left',verticalalignment='top', transform=ax.transAxes)

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
            import serial
            ser=serial.Serial("/dev/ttyACM0")
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
            plt.title("Time : "+str((i*self.INTERVAL)/1000)+"s")
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
                        color = self.color_level[i%len(self.sensor_values)][self.conf_map.get("sensors_layout").index([j,k])]
                        value = self.sensor_values[i%len(self.sensor_values)][self.conf_map.get("sensors_layout").index([j,k])]
                        mass_center_x += value*center[0]
                        sum_x += value
                        mass_center_y += value*center[1]
                        sum_y += value
                    else:
                        # Dans ce cas, pas de capteur aux coordonnées demandées
                        color = 1
                    if(color > 1):
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
        #anim=
        #print "Interval : "+str(INTERVAL)
        anim=animation.FuncAnimation(fig, animate, frames=None, #frames=360,
                                       init_func=init, fargs=None,
                                       save_count=None, interval=self.INTERVAL,
                                       #blit=False)
                                       repeat=False)

        plt.plot(self.sensor_centers_x, self.sensor_centers_y, 'xr')
        plt.plot([self.conf_map.get("center")[0]], [self.conf_map.get("center")[1]], 'ob')
        plt.show()
