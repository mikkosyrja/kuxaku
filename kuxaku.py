#!/usr/bin/env python3

import sys
import math
import datetime
import dateutil.parser

import numpy
import ephem

from jplephem.spk import SPK

import matplotlib.pyplot as plot
from matplotlib.patches import Ellipse

from spktype21 import SPKType21

au = 149597870.691

numpy.set_printoptions(precision=5)

figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor('black')

axis.spines['bottom'].set_color('white')
axis.spines['top'].set_color('white') 
axis.spines['right'].set_color('white')
axis.spines['left'].set_color('white')
axis.tick_params(labelcolor='white', colors='white')

boxsize = 5		# ±au

planetcolor = [0, 0.5, 0]
colonycolor = [0.4, 0, 0.4]
asteroidcolor = [0.4, 0.4, 0.4]
mooncolor = [0.4, 0.4, 0.4]

sunsize = 0.9
planetsize = 0.6
moonsize = 0.5
asteroidsize = 0.4
gasgiantsize = 0.8
stationsize = 0.3

def distance(position):
	return math.sqrt(position[0] * position[0] + position[1] * position[1] + position[2] * position[2]) / au

def printposition(name, position, color, size):
	print(name + ":", position, distance(position))
	ellipse = Ellipse(xy=position[:2] / au, width=size / 2, height=size / 2)
	axis.add_artist(ellipse)
	ellipse.set_clip_box(axis.bbox)
	ellipse.set_facecolor(color)
	plot.text(position[0] / au, position[1] / au, name, fontsize = 5, color='white')
					   
planets = SPK.open('data/planets.bsp')
#print(planets)

datestring = '2051-06-06'
if ( len(sys.argv) > 1 ):
	datestring = sys.argv[1]

#expansedate = dateutil.parser.parse(datestring)
#print(expansedate)



date = ephem.Date(datestring)
julian = ephem.julian_date(date)
print("date:", date, "julian:", julian)

sun = planets[0,10].compute(julian)
printposition("", sun, [1, 1, 0], sunsize)

printposition("mercury", planets[1,199].compute(julian) + planets[0,1].compute(julian), planetcolor, planetsize)
printposition("venus", planets[2,299].compute(julian) + planets[0,2].compute(julian), planetcolor, planetsize)

earthbary = planets[0,3].compute(julian)

printposition("earth", planets[3,399].compute(julian) + earthbary, [0, 0, 1], planetsize)
#printposition("moon", planets[3,301].compute(julian) + earthbary, mooncolor, moonsize)

#l4 = SPK.open('../original/ephemerides/L4_de431.bsp')
#print("l4: ", l4[10,394].compute(2457061.5) - sun)

martian = SPK.open('data/martian.bsp')
#print(martian)

marsbary = martian[0,4].compute(julian)

printposition("mars", martian[4,499].compute(julian)[:3] + marsbary, [1, 0, 0], planetsize)
#printposition("phobos", martian[4,401].compute(julian)[:3] + marsbary, mooncolor, moonsize)
#printposition("deimos", martian[4,402].compute(julian)[:3] + marsbary, mooncolor, moonsize)

#asteroids = SPK.open('data/asteroids.bsp')
#asteroids = SPK.open('data/original/codes_300ast_20100725.bsp')
asteroids = SPK.open('../original/ephemerides/ast343de430.bsp')
#print(asteroids)

def printasteroid(name, id, color = asteroidcolor):
	printposition(name, asteroids[10,2000000 + id].compute(julian) + sun, color, asteroidsize)

printasteroid("ceres", 1, colonycolor)
printasteroid("pallas", 2, colonycolor)
printasteroid("juno", 3)
printasteroid("vesta", 4, colonycolor)
printasteroid("astraea", 5)
printasteroid("hebe", 6)
printasteroid("iris", 7)
printasteroid("flora", 8)
printasteroid("metis", 9)
printasteroid("hygiea", 10, colonycolor)
printasteroid("interamnia", 704)
printasteroid("europa", 52)
printasteroid("davida", 511)
printasteroid("sylvia", 87)
printasteroid("eunomia", 15)
printasteroid("euphrosyne", 31)
printasteroid("patientia", 451)
#printasteroid("hektor", 624)
printasteroid("cybele", 65)
printasteroid("bamberga", 324)
printasteroid("thisbe", 88)
printasteroid("herculina", 532)
printasteroid("doris", 48)
printasteroid("ursula", 375)
printasteroid("camilla", 107)
printasteroid("eugenia", 45)
printasteroid("psyche", 16)
printasteroid("egeria", 13)
#printasteroid("apophis", 99942)
printasteroid("melpomene", 18)
printasteroid("ganymed", 1036)
printasteroid("nausikaa", 192)
printasteroid("massalia", 20)

hungaria = SPKType21.open('data/2000434.bsp')
printposition("hungaria", hungaria.compute_type21(0, 2000434, julian)[0], asteroidcolor, asteroidsize)
#print(hungaria)

printposition("anderson", asteroids[10,2000127].compute(julian) + sun, colonycolor, stationsize)	# johanna

tycho = SPKType21.open('data/2001677.bsp')
printposition("tycho", tycho.compute_type21(0, 2001677, julian)[0], colonycolor, stationsize)
#print(tycho)

jovian = SPK.open('data/jovian.bsp')
#print(jovian)

jupiterbary = jovian[0,5].compute(julian)

printposition("jupiter", jovian[5,599].compute(julian)[:3] + jupiterbary, planetcolor, gasgiantsize)
#printposition("io", jovian[5,501].compute(julian)[:3] + jupiterbary, colonycolor, moonsize)
#printposition("europa", jovian[5,502].compute(julian)[:3] + jupiterbary, colonycolor, moonsize)
#printposition("ganymede", jovian[5,503].compute(julian)[:3] + jupiterbary, colonycolor, moonsize)
#printposition("callisto", jovian[5,504].compute(julian)[:3] + jupiterbary, colonycolor, moonsize)
#printposition("amalthea", jovian[5,505].compute(julian)[:3] + jupiterbary, mooncolor, moonsize)
#printposition("thebe", jovian[5,514].compute(julian)[:3] + jupiterbary, mooncolor, moonsize)
#printposition("adrastea", jovian[5,515].compute(julian)[:3] + jupiterbary, mooncolor, moonsize)
#printposition("metis", jovian[5,516].compute(julian)[:3] + jupiterbary, mooncolor, moonsize)

cronian = SPK.open('data/cronian.bsp')
#print(cronian)

saturnbary = cronian[0,6].compute(julian)

#printposition("saturn", cronian[6,699].compute(julian)[:3] + saturnbary, planetcolor, gasgiantsize)
#printposition("mimas", cronian[6,601].compute(julian)[:3] + saturnbary, mooncolor, moonsize)
#printposition("enceladus", cronian[6,602].compute(julian)[:3] + saturnbary, mooncolor, moonsize)
#printposition("tethys", cronian[6,603].compute(julian)[:3] + saturnbary, mooncolor, moonsize)
#printposition("dione", cronian[6,604].compute(julian)[:3] + saturnbary, mooncolor, moonsize)
#printposition("rhea", cronian[6,605].compute(julian)[:3] + saturnbary, colonycolor, moonsize)
#printposition("titan", cronian[6,606].compute(julian)[:3] + saturnbary, colonycolor, moonsize)
#printposition("hyperion", cronian[6,607].compute(julian)[:3] + saturnbary, mooncolor, moonsize)
#printposition("iapetus", cronian[6,608].compute(julian)[:3] + saturnbary, colonycolor, moonsize)
#printposition("phoebe", cronian[6,609].compute(julian)[:3] + saturnbary, mooncolor, moonsize)

axis.set_xlim(-boxsize, boxsize)
axis.set_ylim(-boxsize, boxsize)

titledate = date.datetime().replace(year=2351)
plot.title(titledate, color='white')

plot.savefig('output/kuxaku.png', dpi=300, facecolor='black', bbox_inches='tight')
