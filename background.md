# Backgroud

There is a very good reason why every fantasy world should have a map. If in a modern day thriller somebody in Paris says that "Let's go to Tokyo", everyone has some idea what that would mean. If somebody in The Witcher universe Brokilon Forest says that "Let's go to Cintra", no one has any idea how long that is going to take. Reader should have a same knowledge as an average citizen of the world and, medieval or not, most have at least cursory knowledge about major geographical locations. They know where to head and how much gear to pack. Kind of mental subway map.

The fantasy world of The Expanse doesn't have a map. Yes, we have familiar names like Mars and Jupiter, but no real information where they are or even how far apart they are. Alex makes a call to Bobbie while flying by Mars. It's a short call because of Rocinante's high speed at that moment. Very cool indeed, but the orbital position of Mars must have been in the route of Rocinante towards outer planets. How convenient.

Planets and asteroids really don't exist all over their orbits like described in the RPG rulebook. They have their own constantly changing locations around the Sun. Miller does a quite remarkably orbital detective work when tracking down the location of Scopuli. In the universe of The Expanse, this kind of newtonian knowledge should be as common as ideas of north and east are for us earthers.

# Maps

Program uses real orbit data from NASA, but not real year 2350 locations. Some ephemerides files contain orbit data only until year 2050 and we have to cheat a little. Python script subtracts 330 years and uses locations starting from year 2020. This is quite acceptable for gaming purposes and especially for The Expance, where actual dates are somewhat vague anyway.

Use of this data was just the easiest way to populate otherwise very empty space with real asteroids and moons without too much work. You may never visit 7066 Nessus, but its strange orbit alone makes outer planet map so much more interesting.

The most important thing here is, that heavenly bodies move predictably during the campaign and their relative positions can be used as a plot point. Unfortunately, it also means that travel times and asteroid locations mentioned in some published adventures need adjustment. Communication delay and travel time tables in the rulebook are based on distances between orbits, not between actual objects. If two planets happen to be opposite sides of the Sun, the real distance is much longer.

Because, in addition to dates, The Expance universe lacks lots of other technical details, some additional improvisation is needed.

For example, location and orbit of Tycho Brahe (asteroid 1677) is used for Tycho Station. Yes, Tycho Station has drives and can be moved, but that doesn't happen too often. Most of the time it just circles around the sun like any other asteroid.

Same goes with destroyed Anderson Station. It is mentioned that it is located "at the far end of the colonized Belt, almost at the opposite side from the major port Ceres". Suitably located asteroid (127 Johanna) with more or less same orbital period is used for its position.

Sol Ring is another problem. It is said to be "stationary positioned little less than 2 AU outside the orbit of Uranus". That means about 22 AU from Sun to random direction. I decided to put it to direction -PI/4 in ecliptic plane, which is in the same hemisphere as current locations of outer planets.

# Travel

Simple travel profiles used do not always make sense. Faster one could be: initial high-g acceleration with the juice for a few hours, 1g cruise to a halfway point, 1g deceleration cruise and final high-g braking with the juice again. Belters, of course, would prefer cruising at 0.3g and some would like to brake earlier to avoid the juice hangover at arrival. Tables alone cannot handle all that. We may need some kind of travel calculator program.

