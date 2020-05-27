# Kuxaku

>Noun
>
>1. space, void, vacuum
>
>Etymology
>
>>Japanese 空白 kuuhaku
>
> -- <https://twitter.com/Nfarmerlinguist/status/692757569236959232>

Solar System object location calculation and map creation for The Expanse role-playing game. Program uses real orbit data from NASA, but not real year 2350 locations. For a background and examples, see: [background.md](background.md)

## Required Python modules

In addition to the Python itself, following modules are required:

- ephem <https://pypi.org/project/ephem/>
- jplephem <https://pypi.org/project/jplephem/>
- spktype21 <https://pypi.org/project/spktype21/>
- matplotlib <https://matplotlib.org/index.html>

These can be installed with Python pip tool (for example: pip install jplephem). Some can also be found from Linux distribution package repositories.

Ephem and Jplephem make most location calculations. Spktype21 is needed by asteroid data using type 21 format. Matplotlib is used to plot tables and Solar System maps.

Program is developed in OpenSuse Tumbleweed Linux and tested also in Windows 10 with Python 3.8. Probably works wherever some recent Python version and above modules work.

## Installation

Instructions for Windows users not familiar with Python or GitHub:

- Download and install Python: <https://www.python.org/downloads/>
- Install above mentioned Python modules in command line:
	- pip install ephem
	- pip install jplephem
	- pip install spktype21
	- pip install matplotlib
- Download kuxaku repository zip-package:
	- top-right green button with text "Clone or download"
	- Select download ZIP, currently about 100MB, includes orbit data
- Extract downloaded package kuxaku-master.zip

## Running program

Go to the program directory and run script kuxaku.py with desired date as a parameter. Date must be given in ISO standard format YYYY-MM-DD. For example:

	kuxaku.py 2350-05-16

Program creates maps and tables as PNG images and puts them into the output subdirectory.

There are some command line options:

	usage: kuxaku.py [-h] [-p] date [juiceg] [juicet]

	positional arguments:
	  date           date in ISO format: YYYY-MM-DD
	  juiceg         optional juice acceleration in standard gravities
	  juicet         optional juice acceleration time in hours

	optional arguments:
	  -h, --help     show this help message and exit
	  -p, --printer  printable images with white background

Optional parameters juiceg and juicet define faster acceleration at both ends of the journey. Option -p creates printer-friendly images with white background.

### Solar System Maps

Coordinate system origin used in maps is the barycenter of the Solar System, which means that the Sun is not exactly at the center.

Inner planet map (inner.png) shows positions of Jupiter, inner planets, important stations and selected asteroids (largest, heaviest or otherwise significant, and few trojans too). For planets and colonized asteroids partial future orbits are displayed as dots separated by one month interval.

Outer planet map (outer.png) shows positions of some Centaurs (small Solar System bodies) and giants Jupiter, Saturn, Uranus and Neptune. Future orbit positions are plotted at one year intervals.

Separate Jovian (jovian.png) and Cronian (cronian.png) maps display major moon positions around Jupiter and Saturnus, respectively. Future orbit positions for some moons are plotted at one hour intervals.

Some objects (notably Eros, Sol Ring and Anderson Station) are currently commented out in the script. These can be turned on by removing the comment character.

### Communication Delay and Travel Times

Communication delay table (delay.png) shows one-way communication delay in minutes between following locations: Mercury, Venus, Earth, Mars, Tycho, Ceres, Pallas, Vesta, Hygiea, Jupiter and Saturn. Delay between planet's moons is usually less than 10 seconds. Delay between Earth and Moon is about 1.3 seconds.

Travel time tables (travel\*.png) show travel times in hours between same locations using 0.5g and 1.0g accelerations. The first one is tolerable for belters and the second one suitable for earthers. Simple brachistochrone equation t=2*sqrt(d/a) is used for calculation. It assumes full acceleration to a halfway point, flip and deceleration to the destination.

Optional command line parameters juiceg and juicet can be used for faster acceleration and deceleration at both ends of the journey. For example, values juiceg 5 and juicet 4 start the journey with 5.0g acceleration for 4 hours. After that cruise acceleration of 0.5g or 1.0g is used normally. At the end of the journey, final deceleration is again done with 5.0g for 4 hours.

Technically it would be possible to have several boost perioids during a long journey, but that is not implemented yet.

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

Preloaded files required by the script can be found from the data subdirectory. They all cover real time period between 2020-01-01 and 2030-01-01.

## Sources

<https://greenroninstore.com/collections/the-expanse-rpg>

<https://expanse.fandom.com/wiki/The_Expanse_Wiki>

<http://www.projectrho.com/public_html/rocket/>
