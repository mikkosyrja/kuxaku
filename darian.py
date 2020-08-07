#!/usr/bin/env python3

import math
import datetime

# Conversion from Gregorian to Martian Darian date
# Based on Ruby code in https://github.com/ai/darian and https://github.com/cworreschk/darian_calendar
class Darian:
	year = 0				# year
	month = 0				# month
	sol = 0					# sol of month
	total_sols = 0			# total sols
	week_sol = 0			# sol of week
	season = 0				# season
	sol_of_season = 0		# sol of season
	month_of_season = 0		# month of season
	sol_of_year = 0			# sol of yaer

	# calculates darian date from total sols
	def calculate(self):
		sD = math.floor(self.total_sols / 334296)
		doD = math.floor(self.total_sols - (sD * 334296))

		sC = 0.0
		doC = doD
		if doD != 0:
			sC = math.floor((doD - 1) / 66859)
		if sC != 0:
			doC -= ((sC * 66859) + 1)

		sX = 0.0
		doX = doC
		if sC != 0: # century that does not begin with leap day
			sX = math.floor((doC + 1) / 6686)
			if sX != 0:
				doX -= ((sX * 6686) - 1)
		else:
			sX = math.floor(doC / 6686)
			if sX != 0:
				doX -= (sX * 6686)

		sII = 0.0
		doII = doX
		if (sC != 0) and (sX == 0):	# decade that does not begin with leap day
			sII = math.floor(doX / 1337)
			if sII != 0:
				doII -= (sII * 1337)
		else: # 1338, 1337, 1337, 1337 ...
			if doX != 0:
				sII = math.floor((doX - 1) / 1337)
			if sII != 0:
				doII -= ((sII * 1337) + 1)

		sI = 0.0
		doI = doII
		if (sII == 0) and ((sX != 0) or ((sX == 0) and (sC == 0))):
			sI = math.floor(doII / 669)
			if sI != 0:
				doI -= 669
		else: # 668, 669
			sI = math.floor((doII + 1) / 669)
			if sI != 0:
				doI -= 668

		self.year = (500 * sD) + (100 * sC) + (10 * sX) + (2 * sII) + sI
		self.sol_of_year = doI

		if self.sol_of_year < 167:
			self.season = 0
		elif self.sol_of_year < 334:
			self.season = 1
		elif self.sol_of_year < 501:
			self.season = 2
		else:
			self.season = 3

		self.sol_of_season = self.sol_of_year - 167 * self.season					# 0-167
		self.month_of_season = math.floor(self.sol_of_season / 28)					# 0-5

		self.month = self.month_of_season + (6 * self.season) + 1					# 1-24
		self.sol = self.sol_of_year - (((self.month - 1) * 28) - self.season) + 1	# 1-28
		self.week_sol = ((self.sol - 1) % 7) + 1									# 1-7

	# returns ISO format darian date
	def string(self):
		date = str(self.year) + '-' + '{:02}'.format(self.month) + '-' + '{:02}'.format(self.sol)
		return date

	# constructor taking gregorian date
	def __init__(self, year, month, day):
		dt = datetime.datetime(year, month, day)
		days = dt.timestamp()  / 86400.0 + 719527		# 719527 is days until 0 year for Unix Epoch
		self.total_sols = (days - 587744.77817) / 1.027491251
		self.calculate()
