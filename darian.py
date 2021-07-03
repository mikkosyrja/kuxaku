#!/usr/bin/env python3

# Note: because both following conversions ignore time of the day, round trip usually produces previous day

import os
import math
import datetime

import dateutil.parser
import argparse
import ephem

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
		if (sC != 0) and (sX == 0):		# decade that does not begin with leap day
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


MARS_TO_EARTH_DAYS = 1.027491251
EPOCH_OFFSET = 587744.77817
eDaysInMonth = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def isEarthLeapYear(year):
	if (year % 400) == 0:
		return True
	if (year % 100) == 0:
		return False
	if (year % 4) == 0:
		return True;
	return False;

# Convert martian time to Date()
# Based on javascript code in https://github.com/mr-faraday/darian-system
def convMarsToEarth(year, month, day):

	solsSince = day + ((month - 1) * 28) - math.floor((month - 1) / 6) + 668 * year + math.floor(year / 2) + math.floor((year-1) / 10) - math.floor((year-1) / 100) + math.floor((year-1) / 1000)
	d = math.floor(solsSince * MARS_TO_EARTH_DAYS + EPOCH_OFFSET) + 1

	sCD = math.floor(d / 146097)   # what 400 year span
	doCD= math.floor(d - (sCD * 146097))

	sC = 0
	doC = doCD
	if doCD != 0:
		sC = math.floor((doCD - 1) / 36524)
	if sC != 0:
		doC -= (sC * 36524 + 1)

	sIV = 0
	doIV = doC
	if sC != 0: 	# 1460 + 1461*24
		sIV = math.floor((doC + 1) / 1461)
		if sIV != 0:
			doIV -= (sIV * 1461 - 1)
	else:	# 1461*25
		sIV = Math.floor(doC / 1461)
		if sIV != 0:
			doIV -= (sIV * 1461)

	sI = 0
	doI = doIV
	if sC != 0 and sIV == 0:	# four 365-day years in a row
		sI = math.floor(doIV / 365)
		if sI != 0:
			doI -= (sI * 365)
	else:	# normal leap year cycle
		if doI != 0:
			sI = math.floor((doIV - 1) / 365)
		if sI != 0:
			doI -= (sI * 365 + 1)

	earthYear = 400*sCD + 100*sC + 4*sIV + sI
	tmpDayOfYear = doI + 1

	for index in range(1, 12):
		tmpDaysInMonth = eDaysInMonth[index]
		if index == 2 and not isEarthLeapYear(earthYear):
			tmpDaysInMonth -= 1

		if tmpDayOfYear > tmpDaysInMonth:
			tmpDayOfYear -= tmpDaysInMonth
		else:
			break;

	earthMonth = index;
	earthDay = tmpDayOfYear;

	print("gregorian date: " + str(earthYear - 330) + '-' + str(earthMonth) + '-' + str(earthDay))
	print("expanse date: " + str(earthYear) + '-' + str(earthMonth) + '-' + str(earthDay))


#parser = argparse.ArgumentParser()
#parser.add_argument("date", help = "date in ISO format: YYYY-MM-DD")
# parser.add_argument("-d", "--darian", help = "input is darian date", action = "store_true")
#parser.add_argument("-g", "--gregorian", help = "input is gregorian date", action = "store_true")
#arguments = parser.parse_args()

#inputdate = dateutil.parser.parse(arguments.date)

#date = ephem.Date(inputdate)
#julian = ephem.julian_date(date)
#darian = Darian(inputdate.year, inputdate.month, inputdate.day)

#print("julian day:", julian)
#print("darian date:", darian.string())

# convMarsToEarth(darian.year, darian.month, darian.sol)

'''
for yyyy in range(2020, 2021):
	for mm in range(1, 13):
		ddmm = eDaysInMonth[mm]
		if mm == 2 and not isEarthLeapYear(yyyy):
			ddmm -= 1;
		for dd in range(1, ddmm + 1):
			isodate = str(yyyy) + '-' + '{:02}'.format(mm) + '-' + '{:02}'.format(dd)
			darian = Darian(yyyy, mm, dd)
			dariandate = str(darian.year) + '-' + '{:02}'.format(darian.month) + '-' + '{:02}'.format(darian.sol)
			print(isodate + '  ' + dariandate)
'''
