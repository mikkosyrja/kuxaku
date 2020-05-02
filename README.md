# kuxaku
Solar system object location calculation for Expanse RPG

Extracting data from original files:

	python3 -m jplephem excerpt 2020/1/1 2025/1/1 de430.bsp planets.bsp
	python3 -m jplephem excerpt 2020/1/1 2025/1/1 ast343de430.bsp asteroids.bsp
	python3 -m jplephem excerpt 2020/1/1 2025/1/1 mar097.bsp martian.bsp
	python3 -m jplephem excerpt 2020/1/1 2025/1/1 jup310.bsp jovian.bsp
	python3 -m jplephem excerpt 2020/1/1 2025/1/1 sat427.bsp cronian.bsp

Getting some additional asteroids:

	https://ssd.jpl.nasa.gov/x/smb_spk.cgi?OBJECT=1677&OPT=Make+SPK&OPTION=Make+SPK&START=2020-JAN-01&STOP=2025-JAN-01&EMAIL=mikko@syrja.org&TYPE=-B
