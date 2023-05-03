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

Solar System object location calculation and map creation for The Expanse role-playing game. Program uses real orbit data from NASA, but not real year 2350 locations. For background and examples, see: [background.md](background.md)

Latest changes can be found from [CHANGELOG.md](CHANGELOG.md)

## Required Python Modules

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
	- Select download ZIP, currently about 160MB, includes orbit data
- Extract downloaded package kuxaku-master.zip

## Running Program

Go to the program directory and run script kuxaku.py with desired date as a parameter. Date must be given in ISO standard format YYYY-MM-DD. For example:

	kuxaku.py 2351-05-16

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

Inner planet map (systeminner.png) shows positions of Jupiter, inner planets, important stations and selected asteroids (largest, heaviest or otherwise significant, and few trojans too). For planets and colonized asteroids partial future orbits are displayed as dots separated by one month interval.

Outer planet map (systemouter.png) shows positions of some Centaurs (small Solar System bodies) and giants Jupiter, Saturn, Uranus and Neptune. Future orbit positions are plotted at one year intervals.

Separate Jovian (jovianinner.png) and Cronian (cronianouter.png) maps display major moon positions around Jupiter and Saturnus, respectively. Future orbit positions for moons are plotted at six hour intervals.

Jovian outer system map (jovianouter.png) shows some Jupiter's outer moons with future orbit positions at one week intervals. Cronian inner system map (cronianinner.png) shows Saturnus' rings and inner moons with future orbit positions at one hour intervals

Some objects (notably Eros, Sol Ring and Anderson Station) are currently commented out in the script. These can be turned on by removing the comment character.

### Communication Delay and Travel Times

Communication delay tables (*delay.png) show one-way communication delay in minutes between the most important locations. Delay between planet's moons is usually less than 10 seconds. Delay between Earth and Moon is about 1.3 seconds.

Travel time tables (\*travel\*.png) show travel times in days between same locations using 0.3, 0.5g and 1.0g accelerations. The first one (\*travel03.png) is comfortable for belters. Second one (\*travel05.png) is faster and still tolerable for most belters. Third one with full 1g acceleration (\*travel10.png) is suitable only for earthers. There are separate tables for Sol, Jovian and Cronian systems.

Simple brachistochrone equation t=2*sqrt(d/a) is used for calculation. It assumes full acceleration to a halfway point, flip and deceleration to the destination. Note that the orbital movement of destination or possible obstacles like, for example, the Sun do not matter here.

Optional command line parameters juiceg and juicet can be used for faster acceleration and deceleration at both ends of the journey. For example, values juiceg 6 and juicet 4 start the journey with 6g acceleration for 4 hours. After that the cruise acceleration of 0.5g is used normally. At the end of the journey, final deceleration is again done with 6g for 4 hours. Tables have given parameters in their names (systemtravel05+60x40.png).

### Darian Calendar

Separate Python module darian.py contains conversion from Gregorian calendar to [Darian calendar](https://en.wikipedia.org/wiki/Darian_calendar) used in Mars. Generated image titles display Darian date in parenthesis after the Gregorian date.

### Solar System Document

The file kuxaku.lyx is a document describing the Solar System and Asteroid Belt for players with Python script generated images. It requires LaTeX (<https://www.latex-project.org/>) and LyX (<https://www.lyx.org/>) to produce PDF output. Example file [example.pdf](example.pdf) shows the result.

Colonized asteroid information comes from the RPG rulebook. Other asteroid descriptions are taken from Wikipedia with some modifications.

## Ephemerides Data

Following data files are downloaded from NASA NAIF site <https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/>:

- de430.bsp (Mercury, Venus, Earth and Moon)
- mar097.bsp (Mars, Phobos and Deimos)
- jup310.bsp (Jupiter and its inner moons)
- jup341.bsp (Jupiter's outer moons)
- sat427.bsp (Saturn and its outer moons)
- sat393.bsp (Saturn's ring moons)
- ura111.bsp (Uranus and its moons)
- nep081.bsp (Neptune and its moons)
- plu058.bsp (Pluto and its moons)

To make files smaller, ten year perioid is extracted from them:

	python3 -m jplephem excerpt 2020/1/1 2030/1/1 de430.bsp planets.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 mar097.bsp martian.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 jup310.bsp jovian.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 sat427.bsp cronian.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 sat393.bsp cronian2.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 ura111.bsp uranian.bsp
	python3 -m jplephem excerpt 2020/1/1 2030/1/1 nep081.bsp neptunian.bsp

Jovian outer moons proved to be somewhat problematic. Jplephem couldn't extract all of them from the file jup341.bsp. However, the latest version 2.15 was able to extract some of them, when listed in command line with targets option.

	python3 -m jplephem excerpt --targets 506,507,508,509,510,511,512,513,517,518,519,520,\
		521,522,523,524,525,526,527,528,529,530 2020/1/1 2030/1/1 jup341.bsp jovian2.bsp

Pluto needed similar handling:

	python3 -m jplephem excerpt --targets 9,999 2020/1/1 2030/1/1 plu058.bsp pluto.bsp

Asteroid data is fetched separately with following URL:

<https://ssd.jpl.nasa.gov/x/smb_spk.cgi?OBJECT=1&OPT=Make+SPK&OPTION=Make+SPK&START=2020-JAN-01&STOP=2030-JAN-01&EMAIL=foo@bar.org&TYPE=-B>

Just change the OBJECT parameter to asteroid id number (for example, OBJECT=433 for Eros). Downloaded files used to have name <2000000+id>.bsp (2000433.bsp for Eros). That changed at some point. Newer downloads have name <20000000+id>.bsp (one more zero in the name). Also, new files use sun as a center instead of the barycenter.

Preloaded files required by the script can be found from the data subdirectory. They all cover real time period between 2020-01-01 and 2030-01-01.

## Sources

<https://greenroninstore.com/collections/the-expanse-rpg>

<https://expanse.fandom.com/wiki/The_Expanse_Wiki>

<http://www.projectrho.com/public_html/rocket/>

<https://en.wikipedia.org/wiki/Darian_calendar>

<https://naif.jpl.nasa.gov/naif/index.html>
