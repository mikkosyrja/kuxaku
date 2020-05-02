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

Solar System object location calculation for The Expanse RPG.

**Note:** Uses real orbit data from NASA, but wrong time period. Only for gaming.

## Required Python modules

- ephem <https://pypi.org/project/ephem/>
- jplephem <https://pypi.org/project/jplephem/>
- spktype21 <https://pypi.org/project/spktype21/>
- matplotlib <https://matplotlib.org/index.html>

Ephem and Jplephem make most location calculations. Spktype21 is needed by some asteroid data using type 21 format. Matplotlib is used to plot Solar System map.

Jplephem should automatically install ephem, but for some reason that did not happen in Windows. So, may need manual installation with pip.

Program is tested and developed in OpenSuse Tumbleweed Linux and Windows 10 with Python 3.8. Probably works wherever some recent Python version and above mentioned modules work.

## Running program

Copy or clone the repository and run kuxaku.py. It creates two simple maps inner.png and outer.png to output subdirectory. First one has inner planet and asteroid locations within five AUs (Jupiters's orbit). Second map contains rest of the Solar System.

### Solar System Maps

Inner planet map shows positions of Jupiter, inner planets, important stations and selected asteroids (largest, heaviest or otherwise significant). For planets and colonized asteroids partial future orbits are displayed as dots separated by one month interval.

Outer planet map shows positions of gas giants Jupiter, Saturn, Uranus and Neptune.

### Communication Delay

xxx

### Travel Time

xxx

## Ephemerides data

Following data files are dowloaded from <https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/>:

- de430.bsp (Mercury, Venus, Earth and Moon)
- mar097.bsp (Mars, Phobos and Deimos)
- ast343de430.bsp (Asteroid Belt)
- jup310.bsp (Jupiter and its moons)
- sat427.bsp (Saturn and its moons)
- ura111.bsp (Uranus and its moons)
- nep081.bsp (Neptune and its moons)

Some files contain ephemerides data only until year 2050 and The Expanse happens in 2350. So, we have to cheat a little. Python script subtracts 330 years and uses 2020 locations for all Solar System objects in 2350.

This is acceptable for gaming purposes and most players will never notice. What is important here, is that heavenly bodies move predictably during the campaign and their relative distances can be used as a plot point.

To make files smaller, we extract only few years from them:

	python3 -m jplephem excerpt 2020/1/1 2025/1/1 de430.bsp planets.bsp
	python3 -m jplephem excerpt 2020/1/1 2025/1/1 ast343de430.bsp asteroids.bsp
	python3 -m jplephem excerpt 2020/1/1 2025/1/1 mar097.bsp martian.bsp
	python3 -m jplephem excerpt 2020/1/1 2025/1/1 jup310.bsp jovian.bsp
	python3 -m jplephem excerpt 2020/1/1 2025/1/1 sat427.bsp cronian.bsp
	python3 -m jplephem excerpt 2020/1/1 2025/1/1 ura111.bsp uranian.bsp
	python3 -m jplephem excerpt 2020/1/1 2025/1/1 nep081.bsp neptunian.bsp

Extracted files can be found from the data subdirectory in this repository.

Above ast343de430.bsp contains only some 300+ most important asteroids. Others must be fetched separately:

	https://ssd.jpl.nasa.gov/x/smb_spk.cgi?OBJECT=1677&OPT=Make+SPK&OPTION=Make+SPK&START=2020-JAN-01&STOP=2025-JAN-01&EMAIL=foo@bar.org&TYPE=-B
	https://ssd.jpl.nasa.gov/x/smb_spk.cgi?OBJECT=588&OPT=Make+SPK&OPTION=Make+SPK&START=2020-JAN-01&STOP=2025-JAN-01&EMAIL=foo@bar.org&TYPE=-B
	https://ssd.jpl.nasa.gov/x/smb_spk.cgi?OBJECT=624&OPT=Make+SPK&OPTION=Make+SPK&START=2020-JAN-01&STOP=2025-JAN-01&EMAIL=foo@bar.org&TYPE=-B
	https://ssd.jpl.nasa.gov/x/smb_spk.cgi?OBJECT=617&OPT=Make+SPK&OPTION=Make+SPK&START=2020-JAN-01&STOP=2025-JAN-01&EMAIL=foo@bar.org&TYPE=-B
	https://ssd.jpl.nasa.gov/x/smb_spk.cgi?OBJECT=884&OPT=Make+SPK&OPTION=Make+SPK&START=2020-JAN-01&STOP=2025-JAN-01&EMAIL=foo@bar.org&TYPE=-B

Books, TV Show and Role-playing game all lack technical details. Some improvisation is needed.

For example, I have used Tycho Brahe (asteroid 1677) as a location of Tycho Station. Yes, Tycho Station has drives and can be moved, but that doesn't happen too often. Most of the time it just circles around the sun like any other asteroid.

Same goes with destroyed Anderson Station. It is mentioned that it is located "at the far end of the colonized Belt, almost at the opposite side from the major port Ceres". So. I just searched suitably located asteroid (127 Johanna) with more or less same orbital period and used its position.
