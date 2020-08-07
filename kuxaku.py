#!/usr/bin/env python3

import os
import sys
import math
import shutil
import datetime
import dateutil.parser

import darian

import argparse

import numpy
import ephem

from jplephem.spk import SPK
from spktype21 import SPKType21

import matplotlib.pyplot as plot
from matplotlib.patches import Ellipse

parser = argparse.ArgumentParser()
parser.add_argument("date", help = "date in ISO format: YYYY-MM-DD")
parser.add_argument("juiceg", help = "optional juice acceleration in standard gravities", type = float, nargs = '?', default = 0)
parser.add_argument("juicet", help = "optional juice acceleration time in hours", type = float, nargs = '?', default = 0)
parser.add_argument("-p", "--printer", help = "printable images with white background", action = "store_true")
arguments = parser.parse_args()

expansedate = dateutil.parser.parse(arguments.date)
if expansedate.year < 2350 or expansedate.year >= 2360:
	print("illegal date:", expansedate, "Year must be between 2350 - 2359")
	sys.exit(1)

date = ephem.Date(expansedate.replace(year = expansedate.year - 330))
julian = ephem.julian_date(date)
darian = darian.Darian(expansedate.year, expansedate.month, expansedate.day)

print("expanse date:", arguments.date)
print("darian date:", darian.string())
print("gregorian date:", date.datetime().date().isoformat())
print("julian day:", julian)

lastdate = ephem.Date(expansedate.replace(year = 2029))
lastjulian = ephem.julian_date(lastdate)

outputdir = 'output/'
if not os.path.exists(outputdir):
	os.mkdir(outputdir)

gravity = 9.80665			# standard gravity
au = 149597870.691			# astronomical unit in kilometers
delay = au / 17987547.48	# communication delay in minutes/au
acc = au * 1000 / gravity	# acceleration scale factor

minx = miny = maxx = maxy = 0	# current boundaries

places = ('Mercury', 'Venus', 'Earth', 'Mars', 'Tycho', 'Ceres', 'Pallas', 'Vesta', 'Hygiea', 'Jupiter', 'Saturn')
positions = []	# must be filled in above order

numpy.set_printoptions(precision=5)

foreground = 'white'
background = 'black'
legendbox = [0.6, 0.6, 0.6]
if arguments.printer:
	foreground = 'black'
	background = 'white'
	legendbox = [0.9, 0.9, 0.9]

plot.figure(1)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor(background)

axis.spines['bottom'].set_color(foreground)
axis.spines['top'].set_color(foreground)
axis.spines['right'].set_color(foreground)
axis.spines['left'].set_color(foreground)
axis.tick_params(labelcolor = foreground, colors = foreground)

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

def plotposition(name, position, color, size, auedge = 0):
#	print(name + ":", position, distance(position), direction(position) / math.pi * 180)
	auposition = position / au
	addellipse(auposition, color, size / 2)
	horizontal = ('right' if position[0] < 0 else 'left')
	if auedge and auposition[0] < auedge * -0.8:
		horizontal = 'left'		# keep text inside
	if auedge and auposition[0] > auedge * 0.8:
		horizontal = 'right'	# keep text inside
	vertical = ('top' if position[1] < 0 else 'bottom')
	plot.text(auposition[0], auposition[1], name, fontsize = 5, color = foreground, ha = horizontal, va = vertical)

def planetorbit(kernel, center, planet, months, color, size = orbitplotsize):
	for index in range(30, months * 30 + 1, 30):
		if julian + index < lastjulian:
			pos = kernel[center, planet].compute(julian + index)[:3] + kernel[0, center].compute(julian + index)
			addellipse(pos / au, color, size)

def titledate():
	return ' ' + str(expansedate.date()) + ' (' + darian.string() + ')'

def savemap(axis, title, name, legend):
	print('Writing:', outputdir + name)
	xpos = ypos = 0.05
	horizontal = 'left'
	vertical = 'bottom'
	if abs(minx) > abs(maxx):
		xpos = 0.95
		horizontal = 'right'
	if abs(miny) > abs(maxy):
		ypos = 0.95
		vertical = 'top'
	axis.text(xpos, ypos, 'orbit dot = ' + legend + '\naxis units in AU', horizontalalignment = horizontal, verticalalignment = vertical,
		transform = axis.transAxes, fontsize = 7, bbox = dict(boxstyle='round', facecolor = legendbox))
	plot.xticks(fontsize = 7)
	plot.yticks(fontsize = 7)
	plot.title(title + titledate(), color = foreground, fontsize = 8)
	plot.savefig(outputdir + name, dpi = 300, facecolor = background, bbox_inches = 'tight')

#
#	inner planets
#
innersize = 5.5		# ±au
minx = miny = maxx = maxy = 0

planets = SPK.open('data/planets.bsp')
#print(planets)

sun = planets[0, 10].compute(julian)
plotposition("", sun, [1, 1, 0], sunsize)

positions.append(planets[1, 199].compute(julian) + planets[0,1].compute(julian))
plotposition("Mercury", positions[-1], mooncolor, moonsize)

positions.append(planets[2, 299].compute(julian) + planets[0,2].compute(julian))
plotposition("Venus", positions[-1], planetcolor, moonsize)

planetorbit(planets, 1, 199, 1, mooncolor)		# mercury
planetorbit(planets, 2, 299, 3, planetcolor)	# venus

earthbary = planets[0,3].compute(julian)
planetorbit(planets, 3, 399, 6, [0, 0, 1])

positions.append(planets[3, 399].compute(julian) + earthbary)
plotposition("Earth", positions[-1], [0, 0, 1], planetsize)
#plotposition("Moon", planets[3, 301].compute(julian) + earthbary, mooncolor, moonsize)

#l4 = SPK.open('../original/ephemerides/L4_de431.bsp')
#print("l4: ", l4[10,394].compute(2457061.5) - sun)

martian = SPK.open('data/martian.bsp')
#print(martian)

marsbary = martian[0,4].compute(julian)
planetorbit(martian, 4, 499, 8, [1, 0, 0])

positions.append(martian[4, 499].compute(julian)[:3] + marsbary)
plotposition("Mars", positions[-1], [1, 0, 0], planetsize)
#plotposition("Phobos", martian[4, 401].compute(julian)[:3] + marsbary, mooncolor, moonsize)
#plotposition("Deimos", martian[4, 402].compute(julian)[:3] + marsbary, mooncolor, moonsize)	# destroyed by earth

def plotasteroid(name, id, color = asteroidcolor, size = asteroidsize, months = 0):
	kernel = SPKType21.open("data/" + str(2000000 + id) + ".bsp")
	for index in range(30, months * 30 + 1, 30):
		pos = kernel.compute_type21(0, 2000000 + id, julian + index)[0]
		addellipse(pos / au, color, orbitplotsize)
	pos = kernel.compute_type21(0, 2000000 + id, julian)[0]
	if months:
		positions.append(pos)
	if id != 127 and id != 1677:
		name = str(id) + ' ' + name
	plotposition(name, pos, color, size, innersize)

#plotasteroid("Anderson", 127, stationcolor, stationsize)		# destroyed by earth, asteroid johanna
plotasteroid("Tycho", 1677, stationcolor, stationsize, 6)

plotasteroid("Ceres", 1, colonycolor, asteroidsize, 6)
plotasteroid("Pallas", 2, colonycolor, asteroidsize, 6)
plotasteroid("Juno", 3)
plotasteroid("Vesta", 4, colonycolor, asteroidsize, 6)
plotasteroid("Astraea", 5)
plotasteroid("Hebe", 6)
#plotasteroid("Iris", 7)
plotasteroid("Flora", 8)
plotasteroid("Metis", 9)
plotasteroid("Hygiea", 10, colonycolor, asteroidsize, 6)
#plotasteroid("Egeria", 13)
plotasteroid("Eunomia", 15)
plotasteroid("Psyche", 16)
#plotasteroid("Melpomene", 18)
plotasteroid("Massalia", 20)
plotasteroid("Themis", 24)
#plotasteroid("Euphrosyne", 31)
plotasteroid("Eugenia", 45)
#plotasteroid("Doris", 48)
plotasteroid("Europa", 52)
plotasteroid("Cybele", 65)
plotasteroid("Sylvia", 87)
#plotasteroid("Thisbe", 88)
plotasteroid("Antiope", 90)
plotasteroid("Camilla", 107)
plotasteroid("Kleopatra", 216)
#plotasteroid("Nausikaa", 192)
plotasteroid("Ida", 243)
#plotasteroid("Bamberga", 324)
#plotasteroid("Ursula", 375)
#plotasteroid("Eros", 433, colonycolor, asteroidsize, 6)		# destroyed by protomolecule
#plotasteroid("Hungaria", 434)
#plotasteroid("Patientia", 451)
plotasteroid("Davida", 511)
#plotasteroid("Herculina", 532)
plotasteroid("Achilles", 588)
plotasteroid("Patroclus", 617)
plotasteroid("Hektor", 624)
#plotasteroid("Interamnia", 704)
#plotasteroid("Priamus", 884)
plotasteroid("Hidalgo", 944)
plotasteroid("Gaspra", 951)
plotasteroid("Ganymed", 1036)

jovian = SPK.open('data/jovian.bsp')
#print(jovian)

jupiterbary = jovian[0,5].compute(julian)
planetorbit(jovian, 5, 599, 24, planetcolor)

plotposition("Jupiter", jovian[5,599].compute(julian)[:3] + jupiterbary, planetcolor, gasgiantsize)

axis.set_xlim(-innersize, innersize)
axis.set_ylim(-innersize, innersize)

savemap(axis, 'Inner System', 'inner.png', 'month')

#
#	outer planets
#
outersize = 32		# ±au
outerscale = 3		# size multiplier
minx = miny = maxx = maxy = 0

plot.figure(2)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor(background)

axis.spines['bottom'].set_color(foreground)
axis.spines['top'].set_color(foreground)
axis.spines['right'].set_color(foreground)
axis.spines['left'].set_color(foreground)
axis.tick_params(labelcolor = foreground, colors = foreground)

plotposition("", sun, [1, 1, 0], sunsize * outerscale)

plotposition("Earth", planets[3,399].compute(julian) + earthbary, [0, 0, 1], planetsize * outerscale)
plotposition("Mars", martian[4,499].compute(julian)[:3] + marsbary, [1, 0, 0], planetsize * outerscale)

plotasteroid("Ceres", 1, colonycolor, asteroidsize * outerscale)
plotasteroid("Tycho", 1677, stationcolor, stationsize * outerscale)

def outerorbit(kernel, center, planet, years, color, size = orbitplotsize):
	for index in range(365, years * 365 + 1, 365):
		if julian + index < lastjulian:
			pos = kernel[center, planet].compute(julian + index)[:3] + kernel[0, center].compute(julian + index)
			addellipse(pos / au, color, size * outerscale * outerscale)

outerorbit(jovian, 5, 599, 8, planetcolor)

positions.append(jovian[5,599].compute(julian)[:3] + jupiterbary)
plotposition("Jupiter", positions[-1], planetcolor, gasgiantsize * outerscale)

cronian = SPK.open('data/cronian.bsp')
#print(cronian)

saturnbary = cronian[0,6].compute(julian)
outerorbit(cronian, 6, 699, 8, planetcolor)

positions.append(cronian[6,699].compute(julian)[:3] + saturnbary)
plotposition("Saturn", positions[-1], planetcolor, gasgiantsize * outerscale)

uranian = SPK.open('data/uranian.bsp')
#print(uranian)

uranusbary = uranian[0,7].compute(julian)
outerorbit(uranian, 7, 799, 8, planetcolor)

plotposition("Uranus", uranian[7, 799].compute(julian)[:3] + uranusbary, planetcolor, gasgiantsize * outerscale)

#gatedistance = 22 * au	# "little less than 2 AU outside the orbit of Uranus"
#gatedirection = -math.pi * 3 / 4 # “This is the Ring. And this is Uranus. They are literally the two spots furthest from each other in the universe that have humans near them”
#solgate = numpy.array([gatedistance * math.cos(gatedirection), gatedistance * math.sin(gatedirection), 0.0])
#plotposition("sol gate", solgate, stationcolor, stationsize * outerscale)

neptunian = SPK.open('data/neptunian.bsp')
#print(neptunian)

neptunebary = neptunian[0,8].compute(julian)
outerorbit(neptunian, 8, 899, 8, planetcolor)

plotposition("Neptune", neptunian[8, 899].compute(julian)[:3] + neptunebary, planetcolor, gasgiantsize * outerscale, outersize)

def plotcentaur(name, id, color = asteroidcolor, size = asteroidsize, years = 0):
	kernel = SPKType21.open("data/" + str(2000000 + id) + ".bsp")
#	for index in range(30, months * 30 + 1, 30):
	for index in range(365, years * 365 + 1, 365):
		pos = kernel.compute_type21(0, 2000000 + id, julian + index)[0]
		addellipse(pos / au, color, orbitplotsize * outerscale * outerscale)
	pos = kernel.compute_type21(0, 2000000 + id, julian)[0]
	plotposition(str(id) + ' ' + name, pos, color, size * outerscale, outersize)

plotcentaur("Hidalgo", 944, asteroidcolor, asteroidsize, 6)
plotcentaur("Chiron", 2060, asteroidcolor, asteroidsize, 6)
plotcentaur("Pholus", 5145, asteroidcolor, asteroidsize, 6)
plotcentaur("Nessus", 7066, asteroidcolor, asteroidsize, 6)
plotcentaur("Asbolus", 8405, asteroidcolor, asteroidsize, 6)
plotcentaur("Chariklo", 10199, asteroidcolor, asteroidsize, 6)
plotcentaur("Hylonome", 10370, asteroidcolor, asteroidsize, 6)

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
axis.patch.set_facecolor(background)

axis.spines['bottom'].set_color(foreground)
axis.spines['top'].set_color(foreground)
axis.spines['right'].set_color(foreground)
axis.spines['left'].set_color(foreground)
axis.tick_params(labelcolor = foreground, colors = foreground)

def printjovian(name, id, color = mooncolor, size = moonsize, hours = 0):
	for index in range(1, hours + 1, 1):
		pos = jovian[5,id].compute(julian + index / 24.0)[:3]
		addellipse(pos / au, color, orbitplotsize * outerscale * jovianscale)
	plotposition(name, jovian[5,id].compute(julian)[:3], color, size * jovianscale)

plotposition("", jovian[5,599].compute(julian)[:3], planetcolor, gasgiantsize * jovianscale)
printjovian("Io", 501, colonycolor, moonsize, 12)
printjovian("Europa", 502, colonycolor, moonsize, 12)
printjovian("Ganymede", 503, colonycolor, moonsize, 12)
printjovian("Callisto", 504, colonycolor, moonsize, 12)
printjovian("Amalthea", 505)
printjovian("Thebe", 514)
printjovian("Adrastea", 515)
printjovian("Metis", 516)

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
axis.patch.set_facecolor(background)

axis.spines['bottom'].set_color(foreground)
axis.spines['top'].set_color(foreground)
axis.spines['right'].set_color(foreground)
axis.spines['left'].set_color(foreground)
axis.tick_params(labelcolor = foreground, colors = foreground)

def printcronian(name, id, color = mooncolor, size = moonsize, hours = 0):
	for index in range(1, hours + 1, 1):
		pos = cronian[6,id].compute(julian + index / 24.0)[:3]
		addellipse(pos / au, color, orbitplotsize * outerscale * cronianscale)
	plotposition(name, cronian[6,id].compute(julian)[:3], color, size * cronianscale)

plotposition("", cronian[6,699].compute(julian)[:3], planetcolor, gasgiantsize * cronianscale)
printcronian("Mimas", 601)
printcronian("Enceladus", 602)
printcronian("Tethys", 603)
printcronian("Dione", 604)
printcronian("Rhea", 605, colonycolor, moonsize, 12)
printcronian("Titan", 606, colonycolor, moonsize, 12)
printcronian("Hyperion", 607, mooncolor, moonsize, 12)
printcronian("Iapetus", 608, colonycolor, moonsize, 12)
#printcronian("Phoebe", 609)	# destroyed by mars

croniansize = 0.025		# ±au
axis.set_xlim(-croniansize, croniansize)
axis.set_ylim(-croniansize, croniansize)

savemap(axis, 'Cronian System', 'cronian.png', 'hour')

#
#	common tables for distances in au
#
distances = []
for row in range(len(places)):
	cellrow = []
	for col in range(len(places)):
		if col >= row:
			cellrow.append(distance(positions[row] - positions[col]))
		else:	# mirror value
			cellrow.append(distances[col][row])
	distances.append(cellrow)

#
#	communication delay
#
print('Writing:', outputdir + 'delay.png')

plot.figure(5)
figure, axis = plot.subplots(figsize=(10, 3), subplot_kw={'aspect': 'equal'})

celltext = []
for row in range(len(places)):
	cellrow = []
	for col in range(len(places)):
		if col >= row:
			value = distances[row][col] * delay
			cellrow.append('{0:.2g}'.format(value) if value < 100 else '{0:.3g}'.format(value))
		else:	# mirror value
			cellrow.append(celltext[col][row])
	celltext.append(cellrow)

axis.axis('off')
axis.axis('tight')
axis.table(cellText = celltext, rowLabels = places, colLabels = places, loc = 'center')
axis.set_title('Communication Delay in Minutes' + titledate(), color = foreground)
axis.patch.set_facecolor(background)

plot.savefig(outputdir + 'delay.png', dpi = 300, facecolor = background, bbox_inches = 'tight')

#
#	travel time
#
def traveltimex(index, cruiseg, juiceg = 0, juicet = 0):
	title = 'Travel Time in Hours (' + str(cruiseg) + 'g'
	filename = outputdir + 'travel' + '{:02.0f}'.format(cruiseg * 10)
	if juiceg and juicet:
		title += ' + ' + str(juiceg) + 'g x ' + str(juicet) + 'h'
		filename += '+' + '{:02.0f}'.format(juiceg * 10) + 'x' + '{:02.0f}'.format(juicet * 10)
	title += ')' + titledate()
	filename += '.png'
	print('Writing:', filename)

	plot.figure(index)
	figure, axis = plot.subplots(figsize=(10, 3), subplot_kw={'aspect': 'equal'})
	celltext = []
	for row in range(len(places)):
		cellrow = []
		for col in range(len(places)):
			if col > row:
				jt = juicet * 3600
				js = gravity * juiceg * jt
				jd = js * jt
				cd = distances[row][col] * au * 1000 - jd
				if cd > 0:	# juice + cruise
					cg = gravity * cruiseg
					ct = (math.sqrt(js * js + cg * cd) - js) / cg
					value = (jt * 2 + ct * 2) / 3600
					cellrow.append('{0:.3g}'.format(value))
				else:	# all juice
					value = 2 * math.sqrt((distances[row][col]) * acc / juiceg)
					cellrow.append('{0:.3g}'.format(value / 3600))
			elif col == row:	# diagonal
				cellrow.append('0')
			else:	# mirror value
				cellrow.append(celltext[col][row])
		celltext.append(cellrow)

	axis.axis('off')
	axis.axis('tight')
	axis.table(cellText = celltext, rowLabels = places, colLabels = places, loc = 'center')
	axis.patch.set_facecolor(background)
	axis.set_title(title, color = foreground)
	plot.savefig(filename, dpi = 300, facecolor = background, bbox_inches = 'tight')
	if juiceg and juicet:
		shutil.copy2(filename, outputdir + 'travel' + '{:02.0f}'.format(cruiseg * 10) + '+boost.png')

traveltimex(6, 0.5)
traveltimex(7, 1.0)
if arguments.juiceg and arguments.juicet:
	traveltimex(8, 0.5, arguments.juiceg, arguments.juicet)
	traveltimex(9, 1.0, arguments.juiceg, arguments.juicet)
