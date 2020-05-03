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

datestring = '2051-06-06'
if ( len(sys.argv) > 1 ):
	datestring = sys.argv[1]

expansedate = dateutil.parser.parse(datestring)
if ( expansedate.year < 2350 or expansedate.year >= 2355 ):
	print("illegal date:", expansedate, "Year must be between 2050 - 2054")
	sys.exit(1)

au = 149597870.691	# astronomical unit in kilometers

numpy.set_printoptions(precision=5)

plot.figure(1)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor('black')

axis.spines['bottom'].set_color('white')
axis.spines['top'].set_color('white') 
axis.spines['right'].set_color('white')
axis.spines['left'].set_color('white')
axis.tick_params(labelcolor='white', colors='white')

planetcolor = [0, 0.5, 0]
colonycolor = [0.6, 0, 0.6]
stationcolor = [0.6, 0.6, 0]
asteroidcolor = [0.4, 0.4, 0.4]
mooncolor = [0.4, 0.4, 0.4]

sunsize = 0.8
planetsize = 0.6
moonsize = 0.5
asteroidsize = 0.4
gasgiantsize = 0.8
stationsize = 0.3

orbitplosize = 0.04

def addellipse(auposition, color, size):
	ellipse = Ellipse(xy = auposition, width = size, height = size)
	axis.add_artist(ellipse)
	ellipse.set_facecolor(color)
	ellipse.set_clip_box(axis.bbox)

def distance(position):		# position in kilometers
	return math.sqrt(position[0] * position[0] + position[1] * position[1] + position[2] * position[2]) / au

def direction(position):	# direction in radians
	return math.atan2(position[1], position[0])

def printposition(name, position, color, size):
	print(name + ":", position, distance(position), direction(position) / math.pi * 180)
	auposition = position / au
	addellipse(auposition, color, size / 2)
	vertical = ('top' if position[1] < 0 else 'bottom')
	horizontal = ('right' if position[0] < 0 else 'left')
	plot.text(auposition[0], auposition[1], name, fontsize = 5, color='white', ha = horizontal, va = vertical)

def planetorbit(kernel, center, planet, months, color, size = orbitplosize):
	for index in range(0, months * 30 + 1, 30):
		pos = kernel[center, planet].compute(julian + index)[:3] + kernel[0, center].compute(julian + index)
		addellipse(pos / au, color, size)

planets = SPK.open('data/planets.bsp')
#print(planets)

date = ephem.Date(expansedate.replace(year = expansedate.year - 330))
julian = ephem.julian_date(date)
print("date:", date, "julian:", julian)

sun = planets[0,10].compute(julian)
printposition("", sun, [1, 1, 0], sunsize)

printposition("mercury", planets[1,199].compute(julian) + planets[0,1].compute(julian), mooncolor, moonsize)
printposition("venus", planets[2,299].compute(julian) + planets[0,2].compute(julian), planetcolor, moonsize)

planetorbit(planets, 1, 199, 1, mooncolor)		# mercury
planetorbit(planets, 2, 299, 3, planetcolor)	# venus

earthbary = planets[0,3].compute(julian)
planetorbit(planets, 3, 399, 6, [0, 0, 1])

printposition("earth", planets[3,399].compute(julian) + earthbary, [0, 0, 1], planetsize)
#printposition("moon", planets[3,301].compute(julian) + earthbary, mooncolor, moonsize)

#l4 = SPK.open('../original/ephemerides/L4_de431.bsp')
#print("l4: ", l4[10,394].compute(2457061.5) - sun)

martian = SPK.open('data/martian.bsp')
#print(martian)

marsbary = martian[0,4].compute(julian)
planetorbit(martian, 4, 499, 12, [1, 0, 0])

printposition("mars", martian[4,499].compute(julian)[:3] + marsbary, [1, 0, 0], planetsize)
#printposition("phobos", martian[4,401].compute(julian)[:3] + marsbary, mooncolor, moonsize)
#printposition("deimos", martian[4,402].compute(julian)[:3] + marsbary, mooncolor, moonsize)	# destroyed by earth

#asteroids = SPK.open('data/asteroids.bsp')
#asteroids = SPK.open('data/original/codes_300ast_20100725.bsp')
asteroids = SPK.open('../original/ephemerides/ast343de430.bsp')
#print(asteroids)

def printasteroid(name, id, color = asteroidcolor, size = asteroidsize):
	printposition(name, asteroids[10,2000000 + id].compute(julian) + sun, color, size)

def asteroidorbit(id, months, color):
	for index in range(0, months * 30 + 1, 30):
		pos = asteroids[10, 2000000 + id].compute(julian + index)[:3] + planets[0,10].compute(julian + index)
		addellipse(pos / au, color, orbitplosize)

asteroidorbit(1, 6, colonycolor)	# ceres
asteroidorbit(2, 6, colonycolor)	# pallas
asteroidorbit(4, 6, colonycolor)	# vesta
asteroidorbit(10, 6, colonycolor)	# hygiea

printasteroid("juno", 3)
printasteroid("astraea", 5)
printasteroid("hebe", 6)
printasteroid("iris", 7)
printasteroid("flora", 8)
printasteroid("metis", 9)
#printasteroid("eros", 433, colonycolor)	# destroyed by protomolecule
printasteroid("interamnia", 704)
printasteroid("europa", 52)
printasteroid("davida", 511)
printasteroid("sylvia", 87)
printasteroid("eunomia", 15)
printasteroid("euphrosyne", 31)
printasteroid("patientia", 451)
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
printasteroid("melpomene", 18)
printasteroid("ganymed", 1036)
printasteroid("nausikaa", 192)
printasteroid("massalia", 20)

printasteroid("ceres", 1, colonycolor)
printasteroid("pallas", 2, colonycolor)
printasteroid("vesta", 4, colonycolor)
printasteroid("hygiea", 10, colonycolor)

def printasteroid21(filename, name, id, color = asteroidcolor, size = asteroidsize):
	kernel = SPKType21.open(filename)
	printposition(name, kernel.compute_type21(0, 2000000 + id, julian)[0], color, size)

def asteroidorbit21(filename, id, months, color):
	kernel = SPKType21.open(filename)
	for index in range(0, months * 30 + 1, 30):
		pos = kernel.compute_type21(0, 2000000 + id, julian + index)[0]
		addellipse(pos / au, color, orbitplosize)

#printasteroid21('data/2000434.bsp', "hungaria", 434)
printasteroid21('data/2000588.bsp', "achilles", 588)
printasteroid21('data/2000624.bsp', "hektor", 624)
printasteroid21('data/2000617.bsp', "patroclus", 617)
printasteroid21('data/2000884.bsp', "priamus", 884)

#printasteroid("anderson", 127, stationcolor, stationsize)		# asteroid johanna, destroyed by earth

printasteroid21('data/2001677.bsp', "tycho", 1677, stationcolor, stationsize)
asteroidorbit21('data/2001677.bsp', 1677, 6, stationcolor)

jovian = SPK.open('data/jovian.bsp')
#print(jovian)

jupiterbary = jovian[0,5].compute(julian)
planetorbit(jovian, 5, 599, 24, planetcolor)

printposition("jupiter", jovian[5,599].compute(julian)[:3] + jupiterbary, planetcolor, gasgiantsize)

innersize = 5		# ±au
axis.set_xlim(-innersize, innersize)
axis.set_ylim(-innersize, innersize)

plot.title('Inner System ' + str(expansedate.date()), color='white')
plot.savefig('output/inner.png', dpi=300, facecolor='black', bbox_inches='tight')

#
#	outer planets
#
outerscale = 3		# size multiplier

plot.figure(2)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor('black')

axis.spines['bottom'].set_color('white')
axis.spines['top'].set_color('white') 
axis.spines['right'].set_color('white')
axis.spines['left'].set_color('white')
axis.tick_params(labelcolor='white', colors='white')

printposition("", sun, [1, 1, 0], sunsize * outerscale)

printposition("earth", planets[3,399].compute(julian) + earthbary, [0, 0, 1], planetsize * outerscale)
printposition("mars", martian[4,499].compute(julian)[:3] + marsbary, [1, 0, 0], planetsize * outerscale)

printasteroid("ceres", 1, colonycolor, asteroidsize * outerscale)
printasteroid21('data/2001677.bsp', "tycho", 1677, stationcolor, stationsize * outerscale)

planetorbit(jovian, 5, 599, 24, planetcolor, orbitplosize * outerscale)

printposition("jupiter", jovian[5,599].compute(julian)[:3] + jupiterbary, planetcolor, gasgiantsize * outerscale)

cronian = SPK.open('data/cronian.bsp')
#print(cronian)

saturnbary = cronian[0,6].compute(julian)
planetorbit(cronian, 6, 699, 24, planetcolor, orbitplosize * outerscale)

printposition("saturn", cronian[6,699].compute(julian)[:3] + saturnbary, planetcolor, gasgiantsize * outerscale)
#printposition("saturn", cronian[6,699].compute(julian)[:3] + saturnbary, planetcolor, gasgiantsize)
#printposition("mimas", cronian[6,601].compute(julian)[:3] + saturnbary, mooncolor, moonsize)
#printposition("enceladus", cronian[6,602].compute(julian)[:3] + saturnbary, mooncolor, moonsize)
#printposition("tethys", cronian[6,603].compute(julian)[:3] + saturnbary, mooncolor, moonsize)
#printposition("dione", cronian[6,604].compute(julian)[:3] + saturnbary, mooncolor, moonsize)
#printposition("rhea", cronian[6,605].compute(julian)[:3] + saturnbary, colonycolor, moonsize)
#printposition("titan", cronian[6,606].compute(julian)[:3] + saturnbary, colonycolor, moonsize)
#printposition("hyperion", cronian[6,607].compute(julian)[:3] + saturnbary, mooncolor, moonsize)
#printposition("iapetus", cronian[6,608].compute(julian)[:3] + saturnbary, colonycolor, moonsize)
#printposition("phoebe", cronian[6,609].compute(julian)[:3] + saturnbary, mooncolor, moonsize)		# destroyed by mars

uranian = SPK.open('data/uranian.bsp')
#print(uranian)

uranusbary = uranian[0,7].compute(julian)
planetorbit(uranian, 7, 799, 24, planetcolor, orbitplosize * outerscale)

printposition("uranus", uranian[7, 799].compute(julian)[:3] + uranusbary, planetcolor, gasgiantsize * outerscale)
planetorbit(uranian, 7, 799, 24, planetcolor)

neptunian = SPK.open('data/neptunian.bsp')
#print(neptunian)

neptunebary = neptunian[0,8].compute(julian)
planetorbit(neptunian, 8, 899, 24, planetcolor)

printposition("neptune", neptunian[8, 899].compute(julian)[:3] + neptunebary, planetcolor, gasgiantsize * outerscale)
planetorbit(neptunian, 8, 899, 24, planetcolor, orbitplosize * outerscale)

outersize = 32		# ±au
axis.set_xlim(-outersize, outersize)
axis.set_ylim(-outersize, outersize)

plot.title('Outer System ' + str(expansedate.date()), color='white')
plot.savefig('output/outer.png', dpi=300, facecolor='black', bbox_inches='tight')

#
#	jovian system
#
jovianscale = 0.001		# size multiplier

plot.figure(3)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor('black')

axis.spines['bottom'].set_color('white')
axis.spines['top'].set_color('white') 
axis.spines['right'].set_color('white')
axis.spines['left'].set_color('white')
axis.tick_params(labelcolor='white', colors='white')

printposition("jupiter", jovian[5,599].compute(julian)[:3], planetcolor, gasgiantsize * jovianscale)
printposition("io", jovian[5,501].compute(julian)[:3], colonycolor, moonsize * jovianscale)
printposition("europa", jovian[5,502].compute(julian)[:3], colonycolor, moonsize * jovianscale)
printposition("ganymede", jovian[5,503].compute(julian)[:3], colonycolor, moonsize * jovianscale)
printposition("callisto", jovian[5,504].compute(julian)[:3], colonycolor, moonsize * jovianscale)
printposition("amalthea", jovian[5,505].compute(julian)[:3], mooncolor, moonsize * jovianscale)
printposition("thebe", jovian[5,514].compute(julian)[:3], mooncolor, moonsize * jovianscale)
printposition("adrastea", jovian[5,515].compute(julian)[:3], mooncolor, moonsize * jovianscale)
printposition("metis", jovian[5,516].compute(julian)[:3], mooncolor, moonsize * jovianscale)

joviansize = 0.01		# ±au
axis.set_xlim(-joviansize, joviansize)
axis.set_ylim(-joviansize, joviansize)

plot.title('Jovian System ' + str(expansedate.date()), color='white')
plot.savefig('output/jovian.png', dpi=300, facecolor='black', bbox_inches='tight')

