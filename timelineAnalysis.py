import lxml
import os
from fastkml import kml
import sys
import json
import requests
import datetime
import collections

# the format of the structured data is a list like => {'time':currTime,'lat': latitude,'lon':longitude}
# the format of the heatmap data is a dict like (latitude,longitude) : int


def main():
	# get kml from provided value or default
	cur_path = os.path.dirname(os.path.realpath(__file__))
	filePath = cur_path + "/data/LocationHistory3.KML"

	structedData = prepare_data(filePath)
	heatmapData = create_heat_map(structedData, 2)

	with open('data/data.json', 'w') as outfile:
		json.dump(structedData, outfile, indent=1, cls=structured_entry_encoder)


def prepare_data(inFilePath):
	tree = lxml.etree.parse(inFilePath)
	# check most recent entry in the KML file and check it again the most recent stored in my own data
	coords = tree.xpath("//gx:coord/text()", namespaces={'gx': 'http://www.google.com/kml/ext/2.2'})
	times = tree.xpath("//xmlns:when/text()", namespaces={'xmlns': 'http://www.opengis.net/kml/2.2'})
	updateData, noData, since = kml_date_check(times[0])

	structedData = load_all(times, coords)
	return(structedData)


def parse_time_2_obj(inTime):
	# take in a sting representing the time in ISO format (how google stores it in KML data)
	# return the date and time as a datetime object
	timeObj = datetime.datetime.strptime(inTime, '%Y-%m-%dT%H:%M:%SZ')
	return(timeObj)


def parse_kml_coord(inCoord):
	# Take in the coordinate data as a string with both lat and long separated by a space
	# split the sting on a space and convert to a floating point number with at most 5 decimal places
	# 5 decimal places represents 1 meters at the equator ( the largest disatnce it will represent)
	# needed 4 dp but this keeps all posible inforation that will be required.
	longitude, latitude, _ = inCoord.split(' ')
	intLat = float(latitude)
	intLong = float(longitude)
	outLat = round(intLat, 5)
	outLong = round(intLong, 5)
	return (outLong, outLat)


def load_all(inTimes, inCoords):
	# parse all the data from a list of times and coordinates stored as strings
	structedData = []
	# for each entry convert the time to a time object and the lat long to floats and store in a list
	# check for existance of data in the dictionary if it exists add one to the count, if not add a new entry
	for item in range(len(inTimes)):
		currTime = parse_time_2_obj(inTimes[item])
		currCoord = inCoords[item]
		longitude, latitude = parse_kml_coord(currCoord)

		record = structured_entry(currTime, latitude, longitude)
		structedData.append(record)

	return structedData


def create_heat_map(inData, inLevel):
	# take in dictionary a round lat longs to the DP specified in inLevel, negative values of inLevel
	# round above the decimal point

	list(map(lambda x:x.round_coord(inLevel), inData))
	outHeatMap = {}
	for value in inData:
		if (value.lat, value.lng) in outHeatMap:
			outHeatMap[(value.lat, value.lng)] = outHeatMap[(value.lat, value.lng)] + 1
		else:
			outHeatMap[(value.lat, value.lng)] = 1

	return(outHeatMap)


def describe_heat_map(inHeat):
	# Return a description of the amount of co-ordinates with a number of entries
	description = {}
	for entry, value in inHeat.items():
		if value not in description:
			description[value] = 1
		else:
			description[value] += 1
	return description

def flatten_structured_data(inData):
	flattenedData = []
	for record in inData:
		pass


def kml_date_check(inCurrentTime):
	# take in a time as a string, convert to a datetime object, if a user data file exists load the time value from it
	# compare the times and determine if the data needs updating, if no file exists assume minimum value of datetime
	currentTime = parse_time_2_obj(inCurrentTime)

	if os.path.isfile('data.json'):
		json_data = open('data.json', 'r').read()
		readTime = json.loads(json_data)['time']
		storedCurrentTime = parse_time_2_obj(readTime)
		readAll = False
	else:
		storedCurrentTime = datetime.datetime.min
		readTime = storedCurrentTime.isoformat() + 'Z'
		readAll = True

	if currentTime > storedCurrentTime:
		return(True, readAll, readTime)
	else:
		return(False, readAll, readTime)


def extract_date(*, inData, inYear='', inMonth='', inDay='', rangeStart='', rangeEnd=''):
	# use the bellow functions with some logic to extract a date
	# clean up rhe below functions as well
	if (bool(inYear) | bool(inMonth) | bool(inDay)) and (bool(rangeStart) | bool(rangeEnd)):
		print('Please supply a specific range or a timeframe from which to extract data, not both')
		raise (SystemExit)
	elif (bool(rangeStart) ^ bool(rangeEnd)):
		message = 'Range end is missing' if bool(rangeStart) else 'Range start is missing'
		print(message)
		raise (SystemExit)
	elif (bool(rangeStart) & bool(rangeEnd)):
		return extract_range(inData, rangeStart, rangeEnd)
	elif (bool(inYear) | bool(inMonth) | bool(inDay)):
		print('in timeframe')
		# to extract a day it needs all three
		# to extract a month it needs a year
		if bool(inYear):
			exYear = extract_year(inData, inYear)
			if bool(inMonth):
				exMonth = extract_month(exYear, inMonth)
				if bool(inDay):
					exDay = extract_day(exMonth, inDay)
					return exDay
				else:
					return exMonth
			else:
				return exYear
		else:
			print('Too low of an increment has been selected without the required higher increments')
			raise(SystemExit)


def extract_year(inData, inYear):
	# take in the structure data as a whole and extact the entries in which the year matches inYear
	outStructure = []
	for entry in inData:
		if entry['time'].year == inYear:
			outStructure.append(entry)
	return(outStructure)


def extract_month(inData, inMonth):
	# take in an extracted year and extact the entries in which the month matches inMonth
	outStructure = []
	for entry in inData:
		if entry['time'].month == inMonth:
			outStructure.append(entry)
	return(outStructure)


def extract_day(inData, inDay):
	# take in an extracted month and extact the entries in which the day matches inDay
	outStructure = []
	for entry in inData:
		if entry['time'].day == inDay:
			outStructure.append(entry)
	return(outStructure)


def extract_range(inData, inStart, inEnd):
	# Take in the structure data as a whole and extact the values between inStart and inEnd
	# inStart and inEnd should be in datetime format
	# TODO parse the time here
	outStructure = []
	for entry in inData:
		if (entry['time'] > inStart and entry['time'] < inEnd):
			outStructure.append(entry)
	return(outStructure)


def country_analysis():
	# get country boundary data set from  GMT
	# feed in a heatmap with 1/2 dp
	# for entry in inheatmap:
	# check if in bounding box of country if so check off a set
	# return % of len set / len dataset

	pass

class structured_entry:
	def __init__(self, time, lat, lng):
		self.time = time
		self.lat = lat
		self.lng = lng
	
	def __str__(self):
		return "Time: {}, lat: {}, lng: {}".format(self.time, self.lat, self.lng)

	def __eq__(self, other):
		lats = self.lat == other.lat
		lngs = self.lng == other.lng
		return lats & lngs 

	def __repr__(self):
		return "Time: {}, lat: {}, lng: {}".format(self.time, self.lat, self.lng)

	def _key(self):
		return (self.lat, self.lng)

	def __hash__(self):
		return hash(self._key())

	def round_coord(self, sigFig):
		self.lat = round(self.lat, sigFig)
		self.lng = round(self.lng, sigFig)
	
# subclass JSONEncoder
class structured_entry_encoder(json.JSONEncoder):
		def default(self, o):
			return {'time':str(o.time), 'lat': o.lat, 'lng': o.lng}

# def ringAround():

if __name__ == '__main__':
	main()
