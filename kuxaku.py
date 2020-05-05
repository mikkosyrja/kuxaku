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

datestring = '2351-06-06'
if ( len(sys.argv) > 1 ):
	datestring = sys.argv[1]

expansedate = dateutil.parser.parse(datestring)
if ( expansedate.year < 2350 or expansedate.year >= 2355 ):
	print("illegal date:", expansedate, "Year must be between 2050 - 2054")
	sys.exit(1)

au = 149597870.691			# astronomical unit in kilometers
delay = au / 17987547.48	# communication delay in minutes/au

places = ('Mercury', 'Venus', 'Earth', 'Mars', 'Ceres', 'Pallas', 'Vesta', 'Hygiea', 'Tycho', 'Jupiter', 'Saturn')
positions = []

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
	for index in range(1, months * 30 + 1, 30):
		pos = kernel[center, planet].compute(julian + index)[:3] + kernel[0, center].compute(julian + index)
		addellipse(pos / au, color, size)

planets = SPK.open('data/planets.bsp')
#print(planets)

date = ephem.Date(expansedate.replace(year = expansedate.year - 330))
julian = ephem.julian_date(date)
print("date:", date, "julian:", julian)

sun = planets[0, 10].compute(julian)
printposition("", sun, [1, 1, 0], sunsize)

positions.append(planets[1, 199].compute(julian) + planets[0,1].compute(julian))
printposition("mercury", positions[-1], mooncolor, moonsize)

positions.append(planets[2, 299].compute(julian) + planets[0,2].compute(julian))
printposition("venus", positions[-1], planetcolor, moonsize)

planetorbit(planets, 1, 199, 1, mooncolor)		# mercury
planetorbit(planets, 2, 299, 3, planetcolor)	# venus

earthbary = planets[0,3].compute(julian)
planetorbit(planets, 3, 399, 6, [0, 0, 1])

positions.append(planets[3, 399].compute(julian) + earthbary)
printposition("earth", positions[-1], [0, 0, 1], planetsize)

#printposition("moon", planets[3, 301].compute(julian) + earthbary, mooncolor, moonsize)

#l4 = SPK.open('../original/ephemerides/L4_de431.bsp')
#print("l4: ", l4[10,394].compute(2457061.5) - sun)

martian = SPK.open('data/martian.bsp')
#print(martian)

marsbary = martian[0,4].compute(julian)
planetorbit(martian, 4, 499, 12, [1, 0, 0])

positions.append(martian[4, 499].compute(julian)[:3] + marsbary)
printposition("mars", positions[-1], [1, 0, 0], planetsize)
#printposition("phobos", martian[4, 401].compute(julian)[:3] + marsbary, mooncolor, moonsize)
#printposition("deimos", martian[4, 402].compute(julian)[:3] + marsbary, mooncolor, moonsize)	# destroyed by earth

def printasteroid(name, id, color = asteroidcolor, size = asteroidsize, months = 0):
	kernel = SPKType21.open("data/" + str(2000000 + id) + ".bsp")
	for index in range(30, months * 30 + 1, 30):
		pos = kernel.compute_type21(0, 2000000 + id, julian + index)[0]
		addellipse(pos / au, color, orbitplosize)
	pos = kernel.compute_type21(0, 2000000 + id, julian)[0]
	if ( months ):
		positions.append(pos)
	printposition(name, pos, color, size)

printasteroid("ceres", 1, colonycolor, asteroidsize, 6)
printasteroid("pallas", 2, colonycolor, asteroidsize, 6)
printasteroid("juno", 3)
printasteroid("vesta", 4, colonycolor, asteroidsize, 6)
printasteroid("astraea", 5)
printasteroid("hebe", 6)
printasteroid("iris", 7)
printasteroid("flora", 8)
printasteroid("metis", 9)
printasteroid("hygiea", 10, colonycolor, asteroidsize, 6)
#printasteroid("eros", 433, colonycolor, asteroidsize, 6)		# destroyed by protomolecule
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

#printasteroid("hungaria", 434)
printasteroid("achilles", 588)
printasteroid("hektor", 624)
printasteroid("patroclus", 617)
printasteroid("priamus", 884)

#printasteroid("anderson", 127, stationcolor, stationsize)		# destroyed by earth, asteroid johanna

printasteroid("tycho", 1677, stationcolor, stationsize, 6)

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
printasteroid("tycho", 1677, stationcolor, stationsize * outerscale)

def outerorbit(kernel, center, planet, years, color, size = orbitplosize):
	for index in range(0, years * 365 + 1, 365):
		pos = kernel[center, planet].compute(julian + index)[:3] + kernel[0, center].compute(julian + index)
		addellipse(pos / au, color, size * outerscale)

outerorbit(jovian, 5, 599, 3, planetcolor, orbitplosize * outerscale)

positions.append(jovian[5,599].compute(julian)[:3] + jupiterbary)
printposition("jupiter", positions[-1], planetcolor, gasgiantsize * outerscale)

cronian = SPK.open('data/cronian.bsp')
#print(cronian)

saturnbary = cronian[0,6].compute(julian)
outerorbit(cronian, 6, 699, 3, planetcolor, orbitplosize * outerscale)

positions.append(cronian[6,699].compute(julian)[:3] + saturnbary)
printposition("saturn", positions[-1], planetcolor, gasgiantsize * outerscale)

uranian = SPK.open('data/uranian.bsp')
#print(uranian)

uranusbary = uranian[0,7].compute(julian)
outerorbit(uranian, 7, 799, 3, planetcolor, orbitplosize * outerscale)

printposition("uranus", uranian[7, 799].compute(julian)[:3] + uranusbary, planetcolor, gasgiantsize * outerscale)

neptunian = SPK.open('data/neptunian.bsp')
#print(neptunian)

neptunebary = neptunian[0,8].compute(julian)
outerorbit(neptunian, 8, 899, 3, planetcolor, orbitplosize * outerscale)

printposition("neptune", neptunian[8, 899].compute(julian)[:3] + neptunebary, planetcolor, gasgiantsize * outerscale)

outersize = 32		# ±au
axis.set_xlim(-outersize, outersize)
axis.set_ylim(-outersize, outersize)

plot.title('Outer System ' + str(expansedate.date()), color='white')
plot.savefig('output/outer.png', dpi=300, facecolor='black', bbox_inches='tight')

#
#	jovian system
#
jovianscale = 0.0015		# size multiplier

plot.figure(3)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor('black')

axis.spines['bottom'].set_color('white')
axis.spines['top'].set_color('white') 
axis.spines['right'].set_color('white')
axis.spines['left'].set_color('white')
axis.tick_params(labelcolor='white', colors='white')

def printjovian(name, id, color = mooncolor, size = moonsize, hours = 0):
	for index in range(1, hours + 1, 1):
		pos = jovian[5,id].compute(julian + index / 24.0)[:3]
		addellipse(pos / au, color, orbitplosize * outerscale * jovianscale)
	printposition(name, jovian[5,id].compute(julian)[:3], color, size * jovianscale)

printposition("", jovian[5,599].compute(julian)[:3], planetcolor, gasgiantsize * jovianscale)
printjovian("io", 501, colonycolor, moonsize, 12)
printjovian("europa", 502, colonycolor, moonsize, 12)
printjovian("ganymede", 503, colonycolor, moonsize, 12)
printjovian("callisto", 504, colonycolor, moonsize, 12)
printjovian("amalthea", 505)
printjovian("thebe", 514)
printjovian("adrastea", 515)
printjovian("metis", 516)

joviansize = 0.015		# ±au
axis.set_xlim(-joviansize, joviansize)
axis.set_ylim(-joviansize, joviansize)

plot.title('Jovian System ' + str(expansedate.date()), color='white')
plot.savefig('output/jovian.png', dpi=300, facecolor='black', bbox_inches='tight')

#
#	cronian system
#
cronianscale = 0.0025		# size multiplier

plot.figure(4)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor('black')

axis.spines['bottom'].set_color('white')
axis.spines['top'].set_color('white') 
axis.spines['right'].set_color('white')
axis.spines['left'].set_color('white')
axis.tick_params(labelcolor='white', colors='white')

def printcronian(name, id, color = mooncolor, size = moonsize, hours = 0):
	for index in range(1, hours + 1, 1):
		pos = cronian[6,id].compute(julian + index / 24.0)[:3]
		addellipse(pos / au, color, orbitplosize * outerscale * cronianscale)
	printposition(name, cronian[6,id].compute(julian)[:3], color, size * cronianscale)

printposition("", cronian[6,699].compute(julian)[:3], planetcolor, gasgiantsize * cronianscale)
printcronian("mimas", 601)
printcronian("enceladus", 602)
printcronian("tethys", 603)
printcronian("dione", 604)
printcronian("rhea", 605, colonycolor, moonsize, 12)
printcronian("titan", 606, colonycolor, moonsize, 12)
printcronian("hyperion", 607, mooncolor, moonsize, 12)
printcronian("iapetus", 608, colonycolor, moonsize, 12)
#printcronian("phoebe", 609)	# destroyed by mars

croniansize = 0.025		# ±au
axis.set_xlim(-croniansize, croniansize)
axis.set_ylim(-croniansize, croniansize)

plot.title('Cronian System ' + str(expansedate.date()), color='white')
plot.savefig('output/cronian.png', dpi=300, facecolor='black', bbox_inches='tight')

#
#	communication delay
#
plot.figure(5)
figure, axis = plot.subplots(figsize=(10, 3), subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor('black')

cell_text = []
for row in range(len(places)):
	cell_row = []
	for col in range(len(places)):
		value = distance(positions[row] - positions[col]) * delay
		cell_row.append('{0:.2g}'.format(value) if value < 100 else '{0:.3g}'.format(value))
	cell_text.append(cell_row)

axis.axis('off')
axis.axis('tight')

table = plot.table(cellText = cell_text, rowLabels = places, colLabels = places, loc = 'center')

plot.title('Communication Delay in Minutes ' + str(expansedate.date()), color='white')
plot.savefig('output/delay.png', dpi=300, facecolor='black', bbox_inches='tight')

