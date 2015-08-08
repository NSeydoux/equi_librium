#!/usr/bin/env python
# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt
from matplotlib import animation
import math

def read_config_file(input_path):
    # le fichier de config se présente comme suit :
    # - nombre de cases en largeur
    # - nombre de cases en hauteur
    # - nombre de capteurs
    # - ligne par ligne, les coordonnées en [x,y] de chaque capteur -> on utilise eval
    config = open(input_path, "r")
    largeur = int(config.readline())
    hauteur = int(config.readline())
    nbr_capteurs = int(config.readline())
    sensors_layout = []
    for i in range(nbr_capteurs):
        sensors_layout.append(eval(config.readline()))
    return {"largeur":largeur, "hauteur":hauteur, "nbr_capteurs":nbr_capteurs, "sensors_layout":sensors_layout}

def read_data_file(input_path):
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
            sensor_values[len(sensor_values)-1][i] = float(sensor_values[len(sensor_values)-1][i])
    return sensor_values

config_map = read_config_file("/home/seydoux/Programmation/Scripts_python/liclipse_workspace/Equilibrium_GUI/config")
print config_map
data = read_data_file("/home/seydoux/Programmation/Scripts_python/liclipse_workspace/Equilibrium_GUI/values")
print data

fig = plt.figure()
fig.set_dpi(100)

ax = plt.axes(xlim=(0, config_map.get("largeur")), ylim=(0, config_map.get("hauteur")))
# values = []
# for i in range(10):
#     values.append([i*j for j in range(10)])

#print values

patches = []
for i in range(config_map.get("largeur")):
    patches.append([])
    for j in range(config_map.get("hauteur")):
        patches[i].append(plt.Rectangle((i, j), 1, 1, 0.0))

def init():
    for i in range(config_map.get("largeur")):
        for j in range(config_map.get("hauteur")):
            ax.add_patch(patches[i][j])
    return [val for sublist in patches for val in sublist]

def animate(i):
#     x, y = patch.center
#     x = 5 + 3 * np.sin(np.radians(i))
#     y = 5 + 3 * np.cos(np.radians(i))
#     patch.center = (x, y)
#     patch.set_color(str(float((i%99))/100.0))
#     print float((i%99))/100.0
#     return patch,
    for j in range(config_map.get("largeur")):
        for k in range(config_map.get("hauteur")):
            #patches[j][k].set_color((str(float(((j*k+i)%100))/100.0)))
            #color = float(values[(j+i)%10][(k+i)%10])/81.0
            #print(config_map.get("largeur")*j+k)
            #color = data[i][config_map.get("largeur")*j+k]

            # le placement des capteurs est stocké dans l'ordre dans la map de configuration
            # donc cconfig_map.get("sensors_layout").index([j,k]) retourne l'index du capteur situé en j,k
            if([j, k] in config_map.get("sensors_layout")):
                color = data[i%81][config_map.get("sensors_layout").index([j,k])]
            else:
                color = 1
            patches[j][k].set_color((str(color)))
            #patches[j][k].set_color((str(color)))
    return [val for sublist in patches for val in sublist]

anim = animation.FuncAnimation(fig, animate,
                               init_func=init,
                               frames=360,
                               interval=200,
                               blit=True)
plt.show()