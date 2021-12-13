#!/usr/bin/env python3

import os
import math
import shutil
import dateutil.parser
import argparse

import darian
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
	os._exit(1)

date = ephem.Date(expansedate.replace(year = expansedate.year - 330))
julian = ephem.julian_date(date)
darian = darian.Darian(expansedate.year, expansedate.month, expansedate.day)

#print("expanse date:", arguments.date)
#print("darian date:", darian.string())
print("gregorian date:", date.datetime().date().isoformat())
#print("julian day:", julian)

lastdate = ephem.Date(expansedate.replace(year = 2029))
lastjulian = ephem.julian_date(lastdate)

outputdir = 'output/'
if not os.path.exists(outputdir):
	os.mkdir(outputdir)

gravity = 9.80665				# standard gravity
aukm = 149597870.7				# astronomical unit in kilometers
gmkm = 1000000					# gigameter in kilometers
augm = aukm / gmkm				# astronomical unit in gigameters
delay = aukm / 17987547.48		# communication delay in minutes/au

minx = miny = maxx = maxy = 0	# current boundaries

systemplaces = ('Venus', 'Earth', 'Mars', 'Tycho', 'Ceres', 'Pallas', 'Vesta', 'Hygiea', 'Jupiter', 'Saturn')
systempositions = []	# must be filled in above order

numpy.set_printoptions(precision=5)

mapdpi = 600

foreground = 'white'
background = 'black'
legendbox = [0.6, 0.6, 0.6]
legendframe = legendbox
ringcolor = [0.1, 0.1, 0.1]
if arguments.printer:
	foreground = 'black'
	background = 'white'
	legendbox = 'white'
	legendframe = 'black'
	ringcolor = 'white'

plot.figure(0)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor(background)

suncolor = [1.0, 1.0, 0]			# yellow
planetcolor = [0, 0.5, 0]			# green
mooncolor = [0.4, 0.4, 0.4]			# gray
colonycolor = [0.6, 0, 0.6]			# purple
stationcolor = [1.0, 0.6, 0]		# orange
asteroidcolor = [0.4, 0.4, 0.4]		# gray

majorfont = 5		# important places
minorfont = 4		# not so important
legendfont = 6		# legend texts
axisfont = 6		# axis texts

# relative sizes
sunsize = 0.8
planetsize = 0.6
moonsize = 0.5
asteroidsize = 0.4
gasgiantsize = 0.7
stationsize = 0.3

orbitdots = 6
orbitdotsize = 0.04		# in AU

edgetolerance = 0.8		# 20% from the edge
orbittolerance = 0.2	# 20% from the Sun

def addellipse(kmposition, color, ausize, unit = 'AU'):
	if unit == 'AU':
		position = kmposition / aukm
		size = ausize
	else:	# Gm
		position = kmposition / gmkm
		size = ausize * augm
	ellipse = Ellipse(xy = position, width = size, height = size)
	axis.add_artist(ellipse)
	ellipse.set_facecolor(color)
	ellipse.set_clip_box(axis.bbox)
	global minx, miny, maxx, maxy
	minx = min(minx, position[0])
	miny = min(miny, position[1])
	maxx = max(maxx, position[0])
	maxy = max(maxy, position[1])

def distance(position):		# position in kilometers
	return math.sqrt(position[0] * position[0] + position[1] * position[1] + position[2] * position[2]) / aukm

def direction(position):	# direction in radians
	return math.atan2(position[1], position[0])

# Label positioning rules:
#	1) Away from the Sun both horizontally and vertically
#	2) Away from the orbit dots with following exceptions:
#		a) No horizontally, if vertically within 20% from the Sun.
#		b) No vertically, if horizontally within 20% from the Sun.
#	3) Away from edge if within 20% from it
def plotlabel(name, kmposition, auedge, orbit = False, retrograde = False, major = False, unit = 'AU'):
	if unit == 'AU':
		position = kmposition / aukm
		edge = auedge
	else:	# Gm
		position = kmposition / gmkm
		edge = auedge * augm
	horizontal = ('right' if position[0] < 0 else 'left')	# away from sun
	if orbit and abs(position[1]) > edge * orbittolerance:
		if retrograde:
			horizontal = ('left' if position[1] < 0 else 'right')	# away from orbit
		else:
			horizontal = ('right' if position[1] < 0 else 'left')	# away from orbit
	if edge and position[0] < edge * -edgetolerance:
		horizontal = 'left'		# keep text inside
	if edge and position[0] > edge * edgetolerance:
		horizontal = 'right'	# keep text inside
	vertical = ('top' if position[1] < 0 else 'bottom')		# away from sun
	if orbit and abs(position[0]) > edge * orbittolerance:
		if retrograde:
			vertical = ('bottom' if position[0] > 0 else 'top')		# away from orbit
		else:
			vertical = ('top' if position[0] > 0 else 'bottom')		# away from orbit
	font = (majorfont if major else minorfont)
	plot.text(position[0], position[1], name, fontsize = font, color = foreground, ha = horizontal, va = vertical)

def plotposition(name, kmposition, color, size, auedge, orbit = False, retrograde = False, major = False, unit = 'AU'):
	addellipse(kmposition, color, size / 2, unit)
	plotlabel(name, kmposition, auedge, orbit, retrograde, major, unit)

def planetorbit(kernel, center, planet, months, color, size = orbitdotsize):
	for index in range(30, months * 30 + 1, 30):
		if julian + index < lastjulian:
			position = kernel[center, planet].compute(julian + index)[:3] + kernel[0, center].compute(julian + index)
			addellipse(position, color, size)

def titledate():
	return ' ' + str(expansedate.date()) + ' (' + darian.string() + ')'

def savemap(axis, ausize, title, name, dots, unit = 'AU'):
	if unit == 'AU':
		size = ausize
	else:	# Gm
		size = ausize * augm
	axis.set_xlim(-size, size)
	axis.set_ylim(-size, size)
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
	axis.text(xpos, ypos, 'orbit dot = ' + dots + '\naxis units in ' + unit, horizontalalignment = horizontal,
		verticalalignment = vertical, transform = axis.transAxes, fontsize = legendfont,
		bbox = dict(boxstyle='round', facecolor = legendbox, edgecolor = legendframe, linewidth = 0.7))
	plot.xticks(fontsize = axisfont)
	plot.yticks(fontsize = axisfont)
	plot.title(title + titledate(), fontsize = 8)
	plot.savefig(outputdir + name, dpi = mapdpi, facecolor = legendbox, bbox_inches = 'tight')

#
#	inner planets
#
innersize = 5.5		# ±au
innerscale = 0.7	# plot scale
minx = miny = maxx = maxy = 0

planets = SPK.open('data/planets.bsp')
#print(planets)

sun = planets[0, 10].compute(julian)
plotposition("", sun, suncolor, sunsize * innerscale, innersize)

position = planets[1, 199].compute(julian) + planets[0,1].compute(julian)
plotposition("Mercury", position, mooncolor, moonsize * innerscale, innersize)

systempositions.append(planets[2, 299].compute(julian) + planets[0,2].compute(julian))
plotposition("Venus", systempositions[-1], planetcolor, moonsize * innerscale, innersize, orbit = True, major = True)

planetorbit(planets, 1, 199, 1, mooncolor)		# mercury
planetorbit(planets, 2, 299, 3, planetcolor)	# venus

earthbary = planets[0,3].compute(julian)
planetorbit(planets, 3, 399, orbitdots, [0, 0, 1])

systempositions.append(planets[3, 399].compute(julian) + earthbary)
plotposition("Earth", systempositions[-1], [0, 0, 1], planetsize * innerscale, innersize, orbit = True, major = True)
#plotposition("Moon", planets[3, 301].compute(julian) + earthbary, mooncolor, moonsize * innerscale)

#l4 = SPK.open('../original/ephemerides/L4_de431.bsp')
#print("l4: ", l4[10,394].compute(2457061.5) - sun)

martian = SPK.open('data/martian.bsp')
#print(martian)

marsbary = martian[0,4].compute(julian)
planetorbit(martian, 4, 499, orbitdots, [1, 0, 0])

systempositions.append(martian[4, 499].compute(julian)[:3] + marsbary)
plotposition("Mars", systempositions[-1], [1, 0, 0], planetsize * innerscale, innersize, orbit = True, major = True)
#plotposition("Phobos", martian[4, 401].compute(julian)[:3] + marsbary, mooncolor, moonsize * innerscale)
#plotposition("Deimos", martian[4, 402].compute(julian)[:3] + marsbary, mooncolor, moonsize * innerscale)	# destroyed by earth

def plotasteroid(name, id, color = asteroidcolor, size = asteroidsize, months = 0, major = False):
	kernel = SPKType21.open("data/" + str(2000000 + id) + ".bsp")
	for index in range(30, months * 30 + 1, 30):
		position = kernel.compute_type21(0, 2000000 + id, julian + index)[0]
		addellipse(position, color, orbitdotsize)
	pos = kernel.compute_type21(0, 2000000 + id, julian)[0]
	if months:
		systempositions.append(pos)
	if id != 127 and id != 1677:
		name = str(id) + ' ' + name
	plotposition(name, pos, color, size * innerscale, innersize, orbit = months, major = (months or major))

plotasteroid("Tycho", 1677, stationcolor, stationsize, orbitdots)

plotasteroid("Ceres", 1, colonycolor, asteroidsize, orbitdots)
plotasteroid("Pallas", 2, colonycolor, asteroidsize, orbitdots)
plotasteroid("Juno", 3)
plotasteroid("Vesta", 4, colonycolor, asteroidsize, orbitdots)
plotasteroid("Astraea", 5)
plotasteroid("Hebe", 6)
plotasteroid("Iris", 7)
plotasteroid("Flora", 8)
plotasteroid("Metis", 9)
plotasteroid("Hygiea", 10, colonycolor, asteroidsize, orbitdots)
plotasteroid("Eunomia", 15)
plotasteroid("Psyche", 16)
plotasteroid("Massalia", 20)
plotasteroid("Lutetia", 21)
plotasteroid("Themis", 24)
plotasteroid("Eugenia", 45)
plotasteroid("Europa", 52)
plotasteroid("Cybele", 65)
plotasteroid("Sylvia", 87)
plotasteroid("Antiope", 90)
plotasteroid("Camilla", 107)
plotasteroid("Kleopatra", 216)
plotasteroid("Herculina", 532)
plotasteroid("Achilles", 588)
plotasteroid("Patroclus", 617)
plotasteroid("Hektor", 624)
plotasteroid("Interamnia", 704)
plotasteroid("Hidalgo", 944)
plotasteroid("Ganymed", 1036)
plotasteroid("Amor", 1221)
plotasteroid("Apollo", 1862)
plotasteroid("Mentor", 3451)
plotasteroid("Cruithne", 3753)
plotasteroid("Eureka", 5261)
#plotasteroid("Apophis", 99942)
plotasteroid("Bennu", 101955)
plotasteroid("Atira", 163693)

jovian = SPK.open('data/jovian.bsp')
jovian2 = SPK.open('data/jovian2.bsp')
#print(jovian)
#print(jovian2)

jupiterbary = jovian[0,5].compute(julian)
planetorbit(jovian, 5, 599, 12, planetcolor)

plotposition("Jupiter", jovian[5,599].compute(julian)[:3] + jupiterbary, planetcolor, gasgiantsize * innerscale, innersize, orbit = True, major = True)

savemap(axis, innersize, 'Inner System', 'systeminner.png', 'month')

plotasteroid("Anderson", 127, stationcolor, stationsize)		# destroyed by earth, asteroid johanna

plotasteroid("Egeria", 13)
plotasteroid("Melpomene", 18)
plotasteroid("Euphrosyne", 31)
plotasteroid("Doris", 48)
plotasteroid("Thisbe", 88)
plotasteroid("Nausikaa", 192)
plotasteroid("Mathilde", 253)
plotasteroid("Ida", 243)
plotasteroid("Bamberga", 324)
plotasteroid("Ursula", 375)
plotasteroid("Eros", 433, colonycolor, asteroidsize)	# destroyed by protomolecule
plotasteroid("Hungaria", 434)
plotasteroid("Patientia", 451)
plotasteroid("Davida", 511)
plotasteroid("Priamus", 884)
plotasteroid("Agamemnon", 911)
plotasteroid("Gaspra", 951)
plotasteroid("Ryugu", 162173)

savemap(axis, innersize, 'Inner System', 'systeminner_all.png', 'month')

#
#	outer planets
#
outersize = 32		# ±au
outerscale = 3		# plot scale
minx = miny = maxx = maxy = 0

plot.figure(0)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor(background)

plotposition("", sun, [1, 1, 0], sunsize * outerscale, outersize)

plotposition("Earth", planets[3,399].compute(julian) + earthbary, [0, 0, 1], planetsize * outerscale, outersize, major = True)
plotposition("Mars", martian[4,499].compute(julian)[:3] + marsbary, [1, 0, 0], planetsize * outerscale, outersize, major = True)

plotasteroid("Ceres", 1, colonycolor, asteroidsize * outerscale, major = True)
plotasteroid("Tycho", 1677, stationcolor, stationsize * outerscale, major = True)

def outerorbit(kernel, center, planet, years, color, size = orbitdotsize):
	for index in range(365, years * 365 + 1, 365):
		if julian + index < lastjulian:
			position = kernel[center, planet].compute(julian + index)[:3] + kernel[0, center].compute(julian + index)
			addellipse(position, color, size * outerscale * outerscale)

outerorbit(jovian, 5, 599, orbitdots, planetcolor)

systempositions.append(jovian[5,599].compute(julian)[:3] + jupiterbary)
plotposition("Jupiter", systempositions[-1], planetcolor, gasgiantsize * outerscale, outersize, orbit = True, major = True)

cronian = SPK.open('data/cronian.bsp')
cronian2 = SPK.open('data/cronian2.bsp')
#print(cronian)
#print(cronian2)

saturnbary = cronian[0,6].compute(julian)
outerorbit(cronian, 6, 699, orbitdots, planetcolor)

systempositions.append(cronian[6,699].compute(julian)[:3] + saturnbary)
plotposition("Saturn", systempositions[-1], planetcolor, gasgiantsize * outerscale, outersize, orbit = True, major = True)

uranian = SPK.open('data/uranian.bsp')
#print(uranian)

uranusbary = uranian[0,7].compute(julian)
outerorbit(uranian, 7, 799, orbitdots, planetcolor)

plotposition("Uranus", uranian[7, 799].compute(julian)[:3] + uranusbary, planetcolor, gasgiantsize * outerscale, outersize, orbit = True, major = True)

neptunian = SPK.open('data/neptunian.bsp')
#print(neptunian)

neptunebary = neptunian[0,8].compute(julian)
outerorbit(neptunian, 8, 899, orbitdots, planetcolor)

plotposition("Neptune", neptunian[8, 899].compute(julian)[:3] + neptunebary, planetcolor, gasgiantsize * outerscale, outersize, orbit = True, major = True)

def plotcentaur(name, id, color = asteroidcolor, size = asteroidsize, years = 0):
	kernel = SPKType21.open("data/" + str(2000000 + id) + ".bsp")
#	for index in range(30, months * 30 + 1, 30):
	for index in range(365, years * 365 + 1, 365):
		position = kernel.compute_type21(0, 2000000 + id, julian + index)[0]
		addellipse(position, color, orbitdotsize * outerscale * outerscale)
	pos = kernel.compute_type21(0, 2000000 + id, julian)[0]
	plotposition(str(id) + ' ' + name, pos, color, size * outerscale, outersize, years)

plotcentaur("Hidalgo", 944, asteroidcolor, asteroidsize, orbitdots)
plotcentaur("Chiron", 2060, asteroidcolor, asteroidsize, orbitdots)
plotcentaur("Pholus", 5145, asteroidcolor, asteroidsize, orbitdots)
plotcentaur("Nessus", 7066, asteroidcolor, asteroidsize, orbitdots)
plotcentaur("Asbolus", 8405, asteroidcolor, asteroidsize, orbitdots)
plotcentaur("Chariklo", 10199, asteroidcolor, asteroidsize, orbitdots)
plotcentaur("Hylonome", 10370, asteroidcolor, asteroidsize, orbitdots)

savemap(axis, outersize, 'Outer System', 'systemouter.png', 'year')

gatedistance = 22 * aukm	# "little less than 2 AU outside the orbit of Uranus"
gatedirection = -math.pi * 3 / 4 # “This is the Ring. And this is Uranus. They are literally the two spots furthest from each other in the universe that have humans near them”
solgate = numpy.array([gatedistance * math.cos(gatedirection), gatedistance * math.sin(gatedirection), 0.0])
plotposition("Sol Gate", solgate, stationcolor, stationsize * outerscale, outersize)

savemap(axis, outersize, 'Outer System', 'systemouter_all.png', 'year')

#
#	jovian inner system
#
jovianunit = 'Gm'
joviansize = 0.014		# ±au
minx = miny = maxx = maxy = 0

plot.figure(0)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor(background)

def printjovian(name, id, color = mooncolor, size = moonsize, quarters = 0, major = False):
	for index in range(1, quarters + 1, 1):
		position = jovian[5,id].compute(julian + index / 4)[:3]
		addellipse(position, color, orbitdotsize * outerscale * joviansize / 10, unit = jovianunit)
	plotposition(name, jovian[5,id].compute(julian)[:3], color, size * joviansize / 10, joviansize, quarters, False, major, unit = jovianunit)

plotposition("", jovian[5,599].compute(julian)[:3], planetcolor, gasgiantsize * joviansize / 10, joviansize, unit = jovianunit)
printjovian("Io", 501, colonycolor, moonsize, orbitdots, major = True)
printjovian("Europa", 502, colonycolor, moonsize, orbitdots, major = True)
printjovian("Ganymede", 503, colonycolor, moonsize, orbitdots, major = True)
printjovian("Callisto", 504, colonycolor, moonsize, orbitdots, major = True)
printjovian("Amalthea", 505)
printjovian("Thebe", 514)
printjovian("Adrastea", 515)
printjovian("Metis", 516)

jovianplaces = ('Ganym.', 'Callisto', 'Leda', 'Himalia', 'Elara', 'Lysithea', 'Ananke', 'Pasiphae', 'Carme', 'Sinope')
jovianpositions = []	# must be filled in above order

jovianpositions.append(jovian[5,503].compute(julian)[:3])	# Ganymede
jovianpositions.append(jovian[5,504].compute(julian)[:3])	# Callisto

savemap(axis, joviansize, 'Jovian Inner System', 'jovianinner.png', '6 hours', jovianunit)

#
#	jovian outer system
#
joviansize = 0.21		# ±au
minx = miny = maxx = maxy = 0

plot.figure(0)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor(background)

def printjovianouter(name, id, weeks = 0, retrograde = False):
	for index in range(1, weeks + 1, 1):
		position = jovian2[5,id].compute(julian + index * 7)[:3]
		addellipse(position, mooncolor, orbitdotsize * outerscale * joviansize / 10, unit = jovianunit)
	plotposition(name, jovian2[5,id].compute(julian)[:3], mooncolor, moonsize * joviansize / 10, joviansize, weeks, retrograde, unit = jovianunit)

plotposition("", jovian[5,599].compute(julian)[:3], planetcolor, gasgiantsize * joviansize / 10, joviansize, unit = jovianunit)
printjovian("", 501, colonycolor)	# Io
printjovian("", 502, colonycolor)	# Europa
printjovian("Ganymede", 503, colonycolor, major = True)
printjovian("Callisto", 504, colonycolor, major = True)

printjovianouter("Himalia", 506, orbitdots)
printjovianouter("Elara", 507, orbitdots)
printjovianouter("Pasiphae", 508, orbitdots, True)
printjovianouter("Sinope", 509, orbitdots, True)
printjovianouter("Lysithea", 510, orbitdots)
printjovianouter("Carme", 511, orbitdots, True)
printjovianouter("Ananke", 512, orbitdots, True)
printjovianouter("Leda", 513, orbitdots)
#printjovianouter("Callirrhoe", 517, orbitdots)
printjovianouter("Themisto", 518, orbitdots)
printjovianouter("Kalyke", 523, orbitdots, True)
printjovianouter("Iocaste", 524, orbitdots, True)
printjovianouter("Praxidike", 527, orbitdots, True)

jovianpositions.append(jovian2[5,513].compute(julian)[:3])	# Leda
jovianpositions.append(jovian2[5,506].compute(julian)[:3])	# Himalia
jovianpositions.append(jovian2[5,507].compute(julian)[:3])	# Elara
jovianpositions.append(jovian2[5,510].compute(julian)[:3])	# Lysithea
jovianpositions.append(jovian2[5,512].compute(julian)[:3])	# Ananke
jovianpositions.append(jovian2[5,508].compute(julian)[:3])	# Pasiphae
jovianpositions.append(jovian2[5,511].compute(julian)[:3])	# Carme
jovianpositions.append(jovian2[5,509].compute(julian)[:3])	# Sinope

savemap(axis, joviansize, 'Jovian Outer System', 'jovianouter.png', 'week', 'Gm')

#
#	cronian inner system
#
cronianunit = 'Gm'
croniansize = 0.003			# ±au
minx = miny = maxx = maxy = 0

plot.figure(0)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor(background)

def printring(name, kminner, kmouter):
	if cronianunit == 'AU':
		inner = kminner / aukm
		outer = kmouter / aukm
	else:	# Gm
		inner = kminner / gmkm
		outer = kmouter / gmkm
	plot.text((inner + outer) / -2, 0, name, fontsize = majorfont, color = foreground, ha = 'center', va = 'center')
	axis.add_artist(plot.Circle((0.0, 0.0), outer, fill = True, color = ringcolor, lw = 0.2))
	axis.add_artist(plot.Circle((0.0, 0.0), inner, fill = True, color = background, lw = 0.2))
	axis.add_artist(plot.Circle((0.0, 0.0), inner, fill = False, color = foreground, lw = 0.2))
	axis.add_artist(plot.Circle((0.0, 0.0), outer, fill = False, color = foreground, lw = 0.2))

printring('A', 118000, 137000)	# ring a in km
printring('B', 92000, 118000)	# ring b in km
printring('C', 75000, 92000)	# ring c in km
printring('', 67000, 75000)		# ring d in km

def printcronianring(name, id, color = mooncolor, size = moonsize, hours = 0):
	for index in range(1, hours + 1, 1):
		position = cronian2[6,id].compute(julian + index / 24)[:3]
		addellipse(position, color, orbitdotsize * outerscale * croniansize / 10, unit = cronianunit)
	plotposition(name, cronian2[6,id].compute(julian)[:3], color, size * croniansize / 10, croniansize, hours, unit = cronianunit)

def printcronianinner(name, id, color = mooncolor, size = moonsize, hours = 0):
	for index in range(1, hours + 1, 1):
		position = cronian[6,id].compute(julian + index / 24)[:3]
		addellipse(position, color, orbitdotsize * outerscale * croniansize / 10, unit = cronianunit)
	plotposition(name, cronian[6,id].compute(julian)[:3], color, size * croniansize / 10, croniansize, hours, unit = cronianunit)

plotposition("", cronian[6,699].compute(julian)[:3], planetcolor, gasgiantsize * croniansize / 10, croniansize, unit = cronianunit)

printcronianring("Janus", 610, mooncolor, moonsize, 3)
printcronianring("Epimethus", 611, mooncolor, moonsize, 3)
printcronianring("Helene", 612, mooncolor, moonsize, 4)
printcronianring("Telesto", 613, mooncolor, moonsize, 4)
printcronianring("Calypso", 614, mooncolor, moonsize, 4)
printcronianring("Prometheus", 616, mooncolor, moonsize, 3)
printcronianring("Pandora", 617, mooncolor, moonsize, 3)
printcronianring("Polydeuces", 634, mooncolor, moonsize, 4)

printcronianinner("Mimas", 601, mooncolor, moonsize, 4)
printcronianinner("Enceladus", 602, mooncolor, moonsize, 4)
printcronianinner("Tethys", 603, mooncolor, moonsize, 4)
printcronianinner("Dione", 604, mooncolor, moonsize, 4)

cronianplaces = ('Prometh.', 'Janus', 'Mimas', 'Encelad.', 'Tethys', 'Dione', 'Rhea', 'Titan', 'Hyperion', 'Iapetus')
cronianpositions = []	# must be filled in above order

cronianpositions.append(cronian2[6,616].compute(julian)[:3])	# Prometheus
cronianpositions.append(cronian2[6,610].compute(julian)[:3])	# Janus
cronianpositions.append(cronian[6,601].compute(julian)[:3])		# Mimas
cronianpositions.append(cronian[6,602].compute(julian)[:3])		# Enceladus
cronianpositions.append(cronian[6,603].compute(julian)[:3])		# Tethys
cronianpositions.append(cronian[6,604].compute(julian)[:3])		# Dione

savemap(axis, croniansize, 'Cronian Inner System', 'cronianinner.png', 'hour', cronianunit)

#
#	cronian outer system
#
croniansize = 0.024		# ±au
minx = miny = maxx = maxy = 0

plot.figure(0)
figure, axis = plot.subplots(subplot_kw={'aspect': 'equal'})
axis.patch.set_facecolor(background)

def printcronianouter(name, id, color = mooncolor, size = moonsize, halfs = 0, major = False):
	for index in range(1, halfs + 1, 1):
		position = cronian[6,id].compute(julian + index / 2)[:3]
		addellipse(position, color, orbitdotsize * outerscale * croniansize / 10, unit = cronianunit)
	plotposition(name, cronian[6,id].compute(julian)[:3], color, size * croniansize / 10, croniansize, halfs, False, major, unit = cronianunit)

plotposition("", cronian[6,699].compute(julian)[:3], planetcolor, gasgiantsize * croniansize / 10, croniansize, unit = cronianunit)
axis.add_artist(plot.Circle((0.0, 0.0), 137000 / gmkm, fill = False, color = foreground, lw = 0.2))

printcronianouter("Mimas", 601)
printcronianouter("Enceladus", 602)
printcronianouter("Tethys", 603)
printcronianouter("Dione", 604)
printcronianouter("Rhea", 605, colonycolor, moonsize, orbitdots, major = True)
printcronianouter("Titan", 606, colonycolor, moonsize, orbitdots, major = True)
printcronianouter("Hyperion", 607, mooncolor, moonsize, orbitdots)
printcronianouter("Iapetus", 608, colonycolor, moonsize, orbitdots, major = True)
#printcronianouter("Phoebe", 609)	# destroyed by mars

cronianpositions.append(cronian[6,605].compute(julian)[:3])		# Rhea
cronianpositions.append(cronian[6,606].compute(julian)[:3])		# Titan
cronianpositions.append(cronian[6,607].compute(julian)[:3])		# Hyperion
cronianpositions.append(cronian[6,608].compute(julian)[:3])		# Iapetus

savemap(axis, croniansize, 'Cronian Outer System', 'cronianouter.png', '12 hours', cronianunit)

#
#	calculate distances between places
#
def calculatedistances(places, positions, distances):
	for row in range(len(places)):
		cellrow = []
		for col in range(len(places)):
			if col >= row:
				cellrow.append(distance(positions[row] - positions[col]))
			else:	# mirror value
				cellrow.append(distances[col][row])
		distances.append(cellrow)

#
#	common tables for distances in au
#
systemdistances = []
calculatedistances(systemplaces, systempositions, systemdistances)
joviandistances = []
calculatedistances(jovianplaces, jovianpositions, joviandistances)
croniandistances = []
calculatedistances(cronianplaces, cronianpositions, croniandistances)

#
#	communication delay
#
def commdelay(name, places, distances, unit, system):
	print('Writing:', outputdir + name + '.png')

	plot.figure(0)
	figure, axis = plot.subplots(figsize=(10, 3), subplot_kw={'aspect': 'equal'})

	celltext = []
	for row in range(len(places)):
		cellrow = []
		for col in range(len(places)):
			if col >= row:
				value = distances[row][col] * delay
				if unit == 'Seconds':
					value = value * 60
				cellrow.append('{0:.0f}'.format(value))
			else:	# mirror value
				cellrow.append(celltext[col][row])
		celltext.append(cellrow)

	axis.axis('off')
	axis.axis('tight')
	axis.table(cellText = celltext, rowLabels = places, colLabels = places, loc = 'center')
	axis.set_title(system + ' Communication Delay in ' + unit + ' ' + titledate())
	#axis.patch.set_facecolor(background)

	plot.savefig(outputdir + name + '.png', dpi = 300, facecolor = legendbox, bbox_inches = 'tight')

commdelay('systemdelay', systemplaces, systemdistances, 'Minutes', 'System')
commdelay('joviandelay', jovianplaces, joviandistances, 'Seconds', 'Jovian')
#commdelay('croniandelay', cronianplaces, croniandistances, 'Seconds', 'Cronian')

#
#	travel time
#
def traveltime(name, places, distances, unit, system, cruiseg, juiceg = 0, juicet = 0):
	title = system + ' Travel Time in ' + unit + ' (' + str(cruiseg) + 'g'
	filename = outputdir + name + '{:02.0f}'.format(cruiseg * 10)
	if juiceg and juicet:
		title += ' + ' + str(juiceg) + 'g x ' + str(juicet) + 'h'
		filename += '+' + '{:02.0f}'.format(juiceg * 10) + 'x' + '{:02.0f}'.format(juicet * 10)
	title += ')' + titledate()
	filename += '.png'
	print('Writing:', filename)

	plot.figure(0)
	figure, axis = plot.subplots(figsize=(10, 3), subplot_kw={'aspect': 'equal'})
	celltext = []
	for row in range(len(places)):
		cellrow = []
		for col in range(len(places)):
			if col > row:
				jt = juicet * 3600
				js = gravity * juiceg * jt
				jd = js * jt
				cd = distances[row][col] * aukm * 1000 - jd
				if cd > 0:	# juice + cruise
					cg = gravity * cruiseg
					ct = (math.sqrt(js * js + cg * cd) - js) / cg
					value = (jt * 2 + ct * 2) / 3600
				else:	# all juice
					value = 2 * math.sqrt((distances[row][col]) * (au * 1000 / gravity) / juiceg) / 3600
				if unit == 'Days':
					cellrow.append('{0:.1f}'.format(value / 24))
				elif unit == 'Hours':
					cellrow.append('{0:.1f}'.format(value))
				else:
					cellrow.append('{0:.0f}'.format(value))
			elif col == row:	# diagonal
				cellrow.append('0')
			else:	# mirror value
				cellrow.append(celltext[col][row])
		celltext.append(cellrow)

	axis.axis('off')
	axis.axis('tight')
	axis.table(cellText = celltext, rowLabels = places, colLabels = places, loc = 'center')
#	axis.patch.set_facecolor(background)
	axis.set_title(title)
	plot.savefig(filename, dpi = 300, facecolor = legendbox, bbox_inches = 'tight')

traveltime('systemtravel', systemplaces, systemdistances, 'Days', 'System', 0.3)
traveltime('systemtravel', systemplaces, systemdistances, 'Days', 'System', 0.5)
traveltime('systemtravel', systemplaces, systemdistances, 'Days', 'System', 1.0)
traveltime('systemtravel', systemplaces, systemdistances, 'Days', 'System', 0.5, 6, 4)
if arguments.juiceg and arguments.juicet:
	traveltime('systemtravel', systemplaces, systemdistances, 'Days', 'System', 0.5, arguments.juiceg, arguments.juicet)

traveltime('joviantravel', jovianplaces, joviandistances, 'Hours', 'Jovian', 0.3)
traveltime('joviantravel', jovianplaces, joviandistances, 'Hours', 'Jovian', 0.5)
traveltime('joviantravel', jovianplaces, joviandistances, 'Hours', 'Jovian', 1.0)

traveltime('croniantravel', cronianplaces, croniandistances, 'Hours', 'Cronian', 0.3)
traveltime('croniantravel', cronianplaces, croniandistances, 'Hours', 'Cronian', 0.5)
#traveltime('croniantravel', cronianplaces, croniandistances, 'Hours', 'Cronian', 1.0)
