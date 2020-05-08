#!/usr/bin/env python3

import os
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
if ( expansedate.year < 2350 or expansedate.year >= 2360 ):
	print("illegal date:", expansedate, "Year must be between 2050 - 2059")
	sys.exit(1)

date = ephem.Date(expansedate.replace(year = expansedate.year - 330))
julian = ephem.julian_date(date)
print("date:", date, "julian:", julian)

lastdate = ephem.Date(expansedate.replace(year = 2029))
lastjulian = ephem.julian_date(lastdate)

outputdir = 'output/'
if not os.path.exists(outputdir):
	os.mkdir(outputdir)

au = 149597870.691			# astronomical unit in kilometers
delay = au / 17987547.48	# communication delay in minutes/au
acc = au * 1000 / 9.81		# distance in meters and acceleration 

minx = miny = maxx = maxy = 0	# boundaries

places = ('Mercury', 'Venus', 'Earth', 'Mars', 'Tycho', 'Ceres', 'Pallas', 'Vesta', 'Hygiea', 'Jupiter', 'Saturn')
positions = []	# must be filled in above order

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

orbitplotsize = 0.04

def addellipse(auposition, color, size):
	ellipse = Ellipse(xy = auposition, width = size, height = size)
	axis.add_artist(ellipse)
	ellipse.set_facecolor(color)
	ellipse.set_clip_box(axis.bbox)
	global minx, miny, maxx, maxy
	minx = min(minx, auposition[0])
	miny = min(miny, auposition[1])
	maxx = max(maxx, auposition[0])
	maxy = max(maxy, auposition[1])

def distance(position):		# position in kilometers
	return math.sqrt(position[0] * position[0] + position[1] * position[1] + position[2] * position[2]) / au

def direction(position):	# direction in radians
	return math.atan2(position[1], position[0])

def plotposition(name, position, color, size):
#	print(name + ":", position, distance(position), direction(position) / math.pi * 180)
	auposition = position / au
	addellipse(auposition, color, size / 2)
	vertical = ('top' if position[1] < 0 else 'bottom')
	horizontal = ('right' if position[0] < 0 else 'left')
	plot.text(auposition[0], auposition[1], name, fontsize = 5, color='white', ha = horizontal, va = vertical)

def planetorbit(kernel, center, planet, months, color, size = orbitplotsize):
	for index in range(30, months * 30 + 1, 30):
		if ( julian + index < lastjulian ):
			pos = kernel[center, planet].compute(julian + index)[:3] + kernel[0, center].compute(julian + index)
			addellipse(pos / au, color, size)

def savemap(axis, title, name, legend):
	xpos = ypos = 0.05
	horizontal = 'left'
	vertical = 'bottom'
	if ( abs(minx) > abs(maxx) ):
		xpos = 0.95
		horizontal = 'right'
	if ( abs(miny) > abs(maxy) ):
		ypos = 0.95
		vertical = 'top'
	axis.text(xpos, ypos, 'orbit dot = ' + legend + '\naxis units in AU', horizontalalignment = horizontal, verticalalignment = vertical,
		transform = axis.transAxes, fontsize = 7, bbox = dict(boxstyle='round', facecolor = [0.6, 0.6, 0.6]))
	plot.title(title + ' ' + str(expansedate.date()), color='white')
	plot.savefig(outputdir + name, dpi = 300, facecolor = 'black', bbox_inches = 'tight')

#
#	inner planets
#
minx = miny = maxx = maxy = 0

planets = SPK.open('data/planets.bsp')
#print(planets)

sun = planets[0, 10].compute(julian)
plotposition("", sun, [1, 1, 0], sunsize)

positions.append(planets[1, 199].compute(julian) + planets[0,1].compute(julian))
plotposition("mercury", positions[-1], mooncolor, moonsize)

positions.append(planets[2, 299].compute(julian) + planets[0,2].compute(julian))
plotposition("venus", positions[-1], planetcolor, moonsize)

planetorbit(planets, 1, 199, 1, mooncolor)		# mercury
planetorbit(planets, 2, 299, 3, planetcolor)	# venus

earthbary = planets[0,3].compute(julian)
planetorbit(planets, 3, 399, 6, [0, 0, 1])

positions.append(planets[3, 399].compute(julian) + earthbary)
plotposition("earth", positions[-1], [0, 0, 1], planetsize)
#plotposition("moon", planets[3, 301].compute(julian) + earthbary, mooncolor, moonsize)

#l4 = SPK.open('../original/ephemerides/L4_de431.bsp')
#print("l4: ", l4[10,394].compute(2457061.5) - sun)

martian = SPK.open('data/martian.bsp')
#print(martian)

marsbary = martian[0,4].compute(julian)
planetorbit(martian, 4, 499, 8, [1, 0, 0])

positions.append(martian[4, 499].compute(julian)[:3] + marsbary)
plotposition("mars", positions[-1], [1, 0, 0], planetsize)
#plotposition("phobos", martian[4, 401].compute(julian)[:3] + marsbary, mooncolor, moonsize)
#plotposition("deimos", martian[4, 402].compute(julian)[:3] + marsbary, mooncolor, moonsize)	# destroyed by earth

def plotasteroid(name, id, color = asteroidcolor, size = asteroidsize, months = 0):
	kernel = SPKType21.open("data/" + str(2000000 + id) + ".bsp")
	for index in range(30, months * 30 + 1, 30):
		pos = kernel.compute_type21(0, 2000000 + id, julian + index)[0]
		addellipse(pos / au, color, orbitplotsize)
	pos = kernel.compute_type21(0, 2000000 + id, julian)[0]
	if ( months ):
		positions.append(pos)
	plotposition(name, pos, color, size)

#plotasteroid("anderson", 127, stationcolor, stationsize)		# destroyed by earth, asteroid johanna
plotasteroid("tycho", 1677, stationcolor, stationsize, 6)

plotasteroid("ceres", 1, colonycolor, asteroidsize, 6)
plotasteroid("pallas", 2, colonycolor, asteroidsize, 6)
plotasteroid("juno", 3)
plotasteroid("vesta", 4, colonycolor, asteroidsize, 6)
plotasteroid("astraea", 5)
plotasteroid("hebe", 6)
#plotasteroid("iris", 7)
plotasteroid("flora", 8)
plotasteroid("metis", 9)
plotasteroid("hygiea", 10, colonycolor, asteroidsize, 6)
#plotasteroid("egeria", 13)
plotasteroid("eunomia", 15)
plotasteroid("psyche", 16)
#plotasteroid("melpomene", 18)
plotasteroid("massalia", 20)
#plotasteroid("euphrosyne", 31)
plotasteroid("eugenia", 45)
#plotasteroid("doris", 48)
plotasteroid("europa", 52)
plotasteroid("cybele", 65)
plotasteroid("sylvia", 87)
#plotasteroid("thisbe", 88)
plotasteroid("antiope", 90)
plotasteroid("camilla", 107)
plotasteroid("kleopatra", 216)
#plotasteroid("nausikaa", 192)
plotasteroid("ida", 243)
plotasteroid("bamberga", 324)
#plotasteroid("ursula", 375)
#plotasteroid("eros", 433, colonycolor, asteroidsize, 6)		# destroyed by protomolecule
#plotasteroid("patientia", 451)
plotasteroid("davida", 511)
#plotasteroid("herculina", 532)
plotasteroid("interamnia", 704)
plotasteroid("ganymed", 1036)

#plotasteroid("hungaria", 434)
plotasteroid("achilles", 588)
plotasteroid("patroclus", 617)
plotasteroid("hektor", 624)
#plotasteroid("priamus", 884)

jovian = SPK.open('data/jovian.bsp')
#print(jovian)

jupiterbary = jovian[0,5].compute(julian)
planetorbit(jovian, 5, 599, 24, planetcolor)

plotposition("jupiter", jovian[5,599].compute(julian)[:3] + jupiterbary, planetcolor, gasgiantsize)

innersize = 5.5		# ±au
axis.set_xlim(-innersize, innersize)
axis.set_ylim(-innersize, innersize)

savemap(axis, 'Inner System', 'inner.png', 'month')

#
#	outer planets
#
minx = miny = maxx = maxy = 0

outerscale = 3		# size multiplier

plot.figure(2)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor('black')

axis.spines['bottom'].set_color('white')
axis.spines['top'].set_color('white') 
axis.spines['right'].set_color('white')
axis.spines['left'].set_color('white')
axis.tick_params(labelcolor='white', colors='white')

plotposition("", sun, [1, 1, 0], sunsize * outerscale)

plotposition("earth", planets[3,399].compute(julian) + earthbary, [0, 0, 1], planetsize * outerscale)
plotposition("mars", martian[4,499].compute(julian)[:3] + marsbary, [1, 0, 0], planetsize * outerscale)

plotasteroid("ceres", 1, colonycolor, asteroidsize * outerscale)
plotasteroid("tycho", 1677, stationcolor, stationsize * outerscale)

def outerorbit(kernel, center, planet, years, color, size = orbitplotsize):
	for index in range(365, years * 365 + 1, 365):
		if ( julian + index < lastjulian ):
			pos = kernel[center, planet].compute(julian + index)[:3] + kernel[0, center].compute(julian + index)
			addellipse(pos / au, color, size * outerscale)

outerorbit(jovian, 5, 599, 8, planetcolor, orbitplotsize * outerscale)

positions.append(jovian[5,599].compute(julian)[:3] + jupiterbary)
plotposition("jupiter", positions[-1], planetcolor, gasgiantsize * outerscale)

cronian = SPK.open('data/cronian.bsp')
#print(cronian)

saturnbary = cronian[0,6].compute(julian)
outerorbit(cronian, 6, 699, 8, planetcolor, orbitplotsize * outerscale)

positions.append(cronian[6,699].compute(julian)[:3] + saturnbary)
plotposition("saturn", positions[-1], planetcolor, gasgiantsize * outerscale)

uranian = SPK.open('data/uranian.bsp')
#print(uranian)

uranusbary = uranian[0,7].compute(julian)
outerorbit(uranian, 7, 799, 8, planetcolor, orbitplotsize * outerscale)

plotposition("uranus", uranian[7, 799].compute(julian)[:3] + uranusbary, planetcolor, gasgiantsize * outerscale)

#gatedistance = 22 * au	# "little less than 2 AU outside the orbit of Uranus"
#gatedirection = -math.pi / 4
#solgate = numpy.array([gatedistance * math.cos(gatedirection), gatedistance * math.sin(gatedirection), 0.0])
#plotposition("sol gate", solgate, stationcolor, stationsize * outerscale)

neptunian = SPK.open('data/neptunian.bsp')
#print(neptunian)

neptunebary = neptunian[0,8].compute(julian)
outerorbit(neptunian, 8, 899, 8, planetcolor, orbitplotsize * outerscale)

plotposition("neptune", neptunian[8, 899].compute(julian)[:3] + neptunebary, planetcolor, gasgiantsize * outerscale)

outersize = 32		# ±au
axis.set_xlim(-outersize, outersize)
axis.set_ylim(-outersize, outersize)

savemap(axis, 'Outer System', 'outer.png', 'year')

#
#	jovian system
#
minx = miny = maxx = maxy = 0

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
		addellipse(pos / au, color, orbitplotsize * outerscale * jovianscale)
	plotposition(name, jovian[5,id].compute(julian)[:3], color, size * jovianscale)

plotposition("", jovian[5,599].compute(julian)[:3], planetcolor, gasgiantsize * jovianscale)
printjovian("io", 501, colonycolor, moonsize, 12)
printjovian("europa", 502, colonycolor, moonsize, 12)
printjovian("ganymede", 503, colonycolor, moonsize, 12)
printjovian("callisto", 504, colonycolor, moonsize, 12)
printjovian("amalthea", 505)
printjovian("thebe", 514)
printjovian("adrastea", 515)
printjovian("metis", 516)

joviansize = 0.014		# ±au
axis.set_xlim(-joviansize, joviansize)
axis.set_ylim(-joviansize, joviansize)

savemap(axis, 'Jovian System', 'jovian.png', 'hour')

#
#	cronian system
#
minx = miny = maxx = maxy = 0

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
		addellipse(pos / au, color, orbitplotsize * outerscale * cronianscale)
	plotposition(name, cronian[6,id].compute(julian)[:3], color, size * cronianscale)

plotposition("", cronian[6,699].compute(julian)[:3], planetcolor, gasgiantsize * cronianscale)
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

savemap(axis, 'Cronian System', 'cronian.png', 'hour')

#
#	common tables
#
distances = []	# distances in au
for row in range(len(places)):
	cellrow = []
	for col in range(len(places)):
		if ( col >= row ):
			cellrow.append(distance(positions[row] - positions[col]))
		else:	# mirror value
			cellrow.append(distances[col][row])
	distances.append(cellrow)

#
#	communication delay
#
plot.figure(5)
figure, axis = plot.subplots(figsize=(10, 3), subplot_kw={'aspect': 'equal'})

celltext = []
for row in range(len(places)):
	cellrow = []
	for col in range(len(places)):
		if ( col >= row ):
			value = distances[row][col] * delay
			cellrow.append('{0:.2g}'.format(value) if value < 100 else '{0:.3g}'.format(value))
		else:	# mirror value
			cellrow.append(celltext[col][row])
	celltext.append(cellrow)

axis.axis('off')
axis.axis('tight')
axis.table(cellText = celltext, rowLabels = places, colLabels = places, loc = 'center')
axis.set_title('Communication Delay in Minutes ' + str(expansedate.date()), color='white')
axis.patch.set_facecolor('black')

plot.savefig(outputdir + 'delay.png', dpi = 300, facecolor = 'black', bbox_inches = 'tight')

#
#	travel time
#
#plot.figure(6)
#figure, axis = plot.subplots(3, 1, figsize=(10, 9), subplot_kw={'aspect': 'equal'})

def traveltime(index, g):
	plot.figure(index)
	figure, axis = plot.subplots(figsize=(10, 3), subplot_kw={'aspect': 'equal'})
	celltext = []
	for row in range(len(places)):
		cellrow = []
		for col in range(len(places)):
			if ( col >= row ):
				value = 2 * math.sqrt(distances[row][col] * acc / g)
				cellrow.append('{0:.3g}'.format(value / 3600))
			else:	# mirror value
				cellrow.append(celltext[col][row])
		celltext.append(cellrow)

	axis.axis('off')
	axis.axis('tight')
	axis.table(cellText = celltext, rowLabels = places, colLabels = places, loc = 'center')
	axis.set_title('Travel Time in Hours (' + str(g) + 'g) ' + str(expansedate.date()), color='white')
	axis.patch.set_facecolor('black')

	plot.savefig(outputdir + 'travel' + '{:02.0f}'.format(g * 10) + '.png', dpi = 300, facecolor = 'black', bbox_inches = 'tight')

traveltime(6, 0.3)
traveltime(7, 1.0)
traveltime(8, 2.0)

