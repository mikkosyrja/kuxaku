#!/usr/bin/env python3

import math
import numpy
import ephem

from jplephem.spk import SPK

import matplotlib
#matplotlib.use('ps')

import matplotlib.pyplot as plot
from matplotlib.patches import Ellipse

from spktype21 import SPKType21

numpy.set_printoptions(precision=5)

fig, axis = plot.subplots(subplot_kw={'aspect': 'equal'})

au = 149597870.691

def distance(position):
	return math.sqrt(position[0] * position[0] + position[1] * position[1] + position[2] * position[2]) / au

def printposition(name, position, color, size):
	print(name + ":", position, distance(position))
	ellipse = Ellipse(xy=position[:2] / au, width=size / 2, height=size / 2)
	axis.add_artist(ellipse)
	ellipse.set_clip_box(axis.bbox)
	ellipse.set_facecolor(color)
	plot.text(position[0] / au, position[1] / au, name, fontsize = 5)
					   
planets = SPK.open('data/planets.bsp')
#print(planets)

date = ephem.Date('2021-06-06')
julian = ephem.julian_date(date)
print("date:", date, "julian:", julian)

sun = planets[0,10].compute(julian)
printposition("sun", sun, [1, 1, 0], 2)

printposition("mercury", planets[1,199].compute(julian) + planets[0,1].compute(julian), [0, 1, 0], 1)
printposition("venus", planets[2,299].compute(julian) + planets[0,2].compute(julian), [0, 1, 0], 1)

earthbary = planets[0,3].compute(julian)

printposition("earth", planets[3,399].compute(julian) + earthbary, [0, 0, 1], 1)
#printposition("moon", planets[3,301].compute(julian) + earthbary, [0, 0, 1], 0.5)

#l4 = SPK.open('../original/ephemerides/L4_de431.bsp')
#print("l4: ", l4[10,394].compute(2457061.5) - sun)

martian = SPK.open('data/martian.bsp')
#print(martian)

marsbary = martian[0,4].compute(julian)

printposition("mars", martian[4,499].compute(julian)[:3] + marsbary, [1, 0, 0], 1)
#printposition("phobos", martian[4,401].compute(julian)[:3] + marsbary, [1, 0, 0], 0.5)
#printposition("deimos", martian[4,402].compute(julian)[:3] + marsbary, [1, 0, 0], 0.5)

#asteroids = SPK.open('data/asteroids.bsp')
#asteroids = SPK.open('data/original/codes_300ast_20100725.bsp')
asteroids = SPK.open('../original/ephemerides/ast343de430.bsp')
#print(asteroids)

printposition("ceres", asteroids[10,2000001].compute(julian) + sun, [0, 0, 1], 0.5)
printposition("pallas", asteroids[10,2000002].compute(julian) + sun, [0, 0, 1], 0.5)
printposition("juno", asteroids[10,2000003].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("vesta", asteroids[10,2000004].compute(julian) + sun, [0, 0, 1], 0.5)
printposition("astraea", asteroids[10,2000005].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("hebe", asteroids[10,2000006].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("iris", asteroids[10,2000007].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("flora", asteroids[10,2000008].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("metis", asteroids[10,2000009].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("hygiea", asteroids[10,2000010].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("interamnia", asteroids[10,2000704].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("europa", asteroids[10,2000052].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("davida", asteroids[10,2000511].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("sylvia", asteroids[10,2000087].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("eunomia", asteroids[10,2000015].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("euphrosyne", asteroids[10,2000031].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("patientia", asteroids[10,2000451].compute(julian) + sun, [0, 1, 1], 0.5)
#printposition("hektor", asteroids[10,2000624].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("cybele", asteroids[10,2000065].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("bamberga", asteroids[10,2000324].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("thisbe", asteroids[10,2000088].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("herculina", asteroids[10,2000532].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("doris", asteroids[10,2000048].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("ursula", asteroids[10,2000375].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("camilla", asteroids[10,2000107].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("eugenia", asteroids[10,2000045].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("psyche", asteroids[10,2000016].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("egeria", asteroids[10,2000013].compute(julian) + sun, [0, 1, 1], 0.5)
#printposition("apophis", asteroids[10,2099942].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("melpomene", asteroids[10,2000018].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("ganymed", asteroids[10,2001036].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("nausikaa", asteroids[10,2000192].compute(julian) + sun, [0, 1, 1], 0.5)
printposition("massalia", asteroids[10,2000020].compute(julian) + sun, [0, 1, 1], 0.5)
#printposition("hungaria", asteroids[10,2000434].compute(julian) + sun, [0, 1, 1], 0.5)

def printasteroid(id):	# for testing
	printposition(str(id), asteroids[10,2000000 + id].compute(julian) + sun, [0, 0, 0], 0.3)

printposition("anderson", asteroids[10,2000127].compute(julian) + sun, [0, 0, 0], 0.3)	# johanna

tycho = SPKType21.open('data/2001677.bsp')
printposition("tycho", tycho.compute_type21(0, 2001677, julian)[0], [0, 0, 0], 0.3)
#print(tycho)

jovian = SPK.open('data/jovian.bsp')
#print(jovian)

jupiterbary = jovian[0,5].compute(julian)

printposition("jupiter", jovian[5,599].compute(julian)[:3] + jupiterbary, [0, 1, 0], 1)
#printposition("io", jovian[5,501].compute(julian)[:3] + jupiterbary, [0, 1, 0], 0.5)
#printposition("europa", jovian[5,502].compute(julian)[:3] + jupiterbary, [0, 1, 0], 0.5)
#printposition("ganymede", jovian[5,503].compute(julian)[:3] + jupiterbary, [0, 1, 0], 0.5)
#printposition("callisto", jovian[5,504].compute(julian)[:3] + jupiterbary, [0, 1, 0], 0.5)
#printposition("amalthea", jovian[5,505].compute(julian)[:3] + jupiterbary, [0, 1, 0], 0.5)
#printposition("thebe", jovian[5,514].compute(julian)[:3] + jupiterbary, [0, 1, 0], 0.5)
#printposition("adrastea", jovian[5,515].compute(julian)[:3] + jupiterbary, [0, 1, 0], 0.5)
#printposition("metis", jovian[5,516].compute(julian)[:3] + jupiterbary, [0, 1, 0], 0.5)

cronian = SPK.open('data/cronian.bsp')
#print(cronian)

saturnbary = cronian[0,6].compute(julian)

printposition("saturn", cronian[6,699].compute(julian)[:3] + saturnbary, [0, 1, 0], 1)
#printposition("mimas", cronian[6,601].compute(julian)[:3] + saturnbary, [0, 1, 0], 1)
#printposition("enceladus", cronian[6,602].compute(julian)[:3] + saturnbary, [0, 1, 0], 1)
#printposition("tethys", cronian[6,603].compute(julian)[:3] + saturnbary, [0, 1, 0], 1)
#printposition("dione", cronian[6,604].compute(julian)[:3] + saturnbary, [0, 1, 0], 1)
#printposition("rhea", cronian[6,605].compute(julian)[:3] + saturnbary, [0, 1, 0], 1)
#printposition("titan", cronian[6,606].compute(julian)[:3] + saturnbary, [0, 1, 0], 1)
#printposition("hyperion", cronian[6,607].compute(julian)[:3] + saturnbary, [0, 1, 0], 1)
#printposition("iapetus", cronian[6,608].compute(julian)[:3] + saturnbary, [0, 1, 0], 1)
#printposition("phoebe", cronian[6,609].compute(julian)[:3] + saturnbary, [0, 1, 0], 1)

axis.set_xlim(-5, 5)
axis.set_ylim(-5, 5)

titledate = date.datetime().replace(year=2351)
plot.title(titledate)

plot.savefig('output/kuxaku.png', dpi=300)
