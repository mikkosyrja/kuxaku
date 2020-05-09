# Kuxaku

>Noun
>
>1. space, vacuum
>
>Etymology
>
>>Japanese 空白 kuuhaku
>
> -- <https://twitter.com/Nfarmerlinguist/status/692757569236959232>

Solar System object location calculation for The Expanse role-playing game.

Program uses real orbit data from NASA, but not real year 2350 locations. Some ephemerides files contain orbit data only until year 2050 and we have to cheat a little. Python script subtracts 330 years and uses 2020 locations for all objects. This is acceptable for gaming purposes and most players will never notice.

What is important here, is that heavenly bodies move predictably during the campaign and their relative positions can be used as a plot point. Unfortunately, it also means that travel times and asteroid locations mentioned in some published adventures need adjustment. Communication delay and travel time tables in the rulebook are based on distances between orbits, not between actual objects. If two planets happen to be opposite sides of the Sun, the real distance is much longer.

Because books, TV series and role-playing game all lack lots of technical detail, some additional improvisation is needed.

For example, location and orbit of Tycho Brahe (asteroid 1677) is used for Tycho Station. Yes, Tycho Station has drives and can be moved, but that doesn't happen too often. Most of the time it just circles around the sun like any other asteroid.

Same goes with destroyed Anderson Station. It is mentioned that it is located "at the far end of the colonized Belt, almost at the opposite side from the major port Ceres". Suitably located asteroid (127 Johanna) with more or less same orbital period is used for its position.

Sol Ring is another problem. It is said to be "stationary positioned little less than 2 AU outside the orbit of Uranus". That means about 22 AU from Sun to random direction. I decided to put it to direction -PI/4 in ecliptic plane, which is in the same hemisphere as current locations of outer planets.

## Required Python modules

In addition to the Python itself, following modules are required:

- ephem <https://pypi.org/project/ephem/>
- jplephem <https://pypi.org/project/jplephem/>
- spktype21 <https://pypi.org/project/spktype21/>
- matplotlib <https://matplotlib.org/index.html>

These can be installed with Python pip tool (for example: pip install jplephem). Some can also be found from Linux distribution package repositories.

Ephem and Jplephem make most location calculations. Spktype21 is needed by some asteroid data using type 21 format. Matplotlib is used to plot tables and Solar System maps.

Program is developed in OpenSuse Tumbleweed Linux and tested also in Windows 10 with Python 3.8. Probably works wherever some recent Python version and above modules work.

## Running program

Copy or clone the repository and run kuxaku.py with some date as a command line parameter. Date must be given in ISO standard format YYYY-MM-DD. For example:

	./kuxaku.py 2351-07-08

Program creates maps and tables as PNG images and puts them to the output subdirectory.

### Solar System Maps

Coordinate system origin used in maps is the barycenter of the Solar System, which means that the Sun is not exactly at the center.

Inner planet map shows positions of Jupiter, inner planets, important stations and selected asteroids (largest, heaviest or otherwise significant, and few trojans too). For planets and colonized asteroids partial future orbits are displayed as dots separated by one month interval.

Outer planet map shows positions of some Centaurs and giants Jupiter, Saturn, Uranus and Neptune. Future orbit positions are plotted at one year intervals.

Separate Jovian and Cronian maps display major moon positions around Jupiter and Saturnus. Future orbit positions for some moons are plotted at one hour intervals.

### Communication Delay and Travel Times

Communication delay table shows one-way communication delay in minutes between following locations: Mercury, Venus, Earth, Mars, Tycho, Ceres, Pallas, Vesta, Hygiea, Jupiter and Saturn. Delay between planet's moons is usually less than 10 seconds. Delay between Earth and Moon is about 1.3 seconds.

Travel time tables show travel times in hours between same locations using 0.3g, 1.0g and 2.0g accelerations. Simple brachistochrone equation t=2*sqrt(d/a) is used.

## Ephemerides data

Following data files are downloaded from <https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/>:

- de430.bsp (Mercury, Venus, Earth and Moon)
- mar097.bsp (Mars, Phobos and Deimos)
- jup310.bsp (Jupiter and its moons)
- sat427.bsp (Saturn and its moons)
- ura111.bsp (Uranus and its moons)
- nep081.bsp (Neptune and its moons)

To make files smaller, ten year perioid is extracted from them:

	python3 -m jplephem excerpt 2020/1/1 2030/1/1 de430.bsp planets.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 mar097.bsp martian.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 jup310.bsp jovian.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 sat427.bsp cronian.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 ura111.bsp uranian.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 nep081.bsp neptunian.bsp

Asteroid data is fetched separately with following URL:

<https://ssd.jpl.nasa.gov/x/smb_spk.cgi?OBJECT=1&OPT=Make+SPK&OPTION=Make+SPK&START=2020-JAN-01&STOP=2030-JAN-01&EMAIL=foo@bar.org&TYPE=-B>

Just change the OBJECT parameter to asteroid id number (for example, OBJECT=433 for Eros). Downloaded files have name <2000000+id>.bsp (2000433.bsp for Eros).

Preloaded files required by the script can be found from the data subdirectory.

## Sources

<https://greenroninstore.com/collections/the-expanse-rpg>

<https://expanse.fandom.com/wiki/The_Expanse_Wiki>

<http://www.projectrho.com/public_html/rocket/>
