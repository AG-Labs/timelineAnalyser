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
	#get kml from provided value or default
	cur_path = os.path.dirname(os.path.realpath(__file__))
	filePath = cur_path + "/data/LocationHistory2.KML"
	
	structedData, heatmapData = prepareData(filePath)

	#testing funcitons for extracting parts of the data
	my2018Data = extractYear(structedData, 2018)

	startRangeToExtract = datetime.datetime(2017,8,1)
	endRangeToExtract = datetime.datetime(2018,8,31)
	myRange = extractRange(structedData,startRangeToExtract, endRangeToExtract)



def prepareData(inFilePath):
	
	tree = lxml.etree.parse(inFilePath)
	#check most recent entry in the KML file and check it again the most recent stored in my own data
	coords = tree.xpath("//gx:coord/text()",namespaces={'gx':'http://www.google.com/kml/ext/2.2'})
	times = tree.xpath("//xmlns:when/text()", namespaces={'xmlns':'http://www.opengis.net/kml/2.2'})
	updateData, noData ,since = kmlDateCheck(times[0])

	structedData = loadAll(times, coords)		
	heatmapData = createHeatMap(structedData, 2)
	
	with open('data/data.json', 'w') as outfile:
		json.dump(structedData, outfile, default=str, indent=1)
	return(structedData, heatmapData)

def parseTime2Obj(inTime):
	#take in a sting representing the time in ISO format (how google stores it in KML data)
	#return the date and time as a datetime object
	timeObj = datetime.datetime.strptime(inTime, '%Y-%m-%dT%H:%M:%SZ')
	return(timeObj)

def parseKMLCoord(inCoord):
	#take in the coordinate data as a string with both lat and long separated by a space
	#split the sting on a space and convert to a floating point number with at most 5 decimal places
	#5 decimal places represents 1 meters at the equator ( the largest disatnce it will represent) 
	#needed 4 dp but this keeps all posible inforation that will be required.
	longitude,latitude, _ = inCoord.split(' ')
	intLat = float(latitude)
	intLong = float(longitude)
	outLat = round(intLat, 5)
	outLong = round(intLong, 5)
	return (outLong, outLat)

def loadAll(inTimes, inCoords):
	# parse all the data from a list of times and coordinates stored as strings
	structedData = []
	# for each entry convert the time to a time object and the lat long to floats and store in a list
	# check for existance of data in the dictionary if it exists add one to the count, if not add a new entry
	for item in range(len(inTimes)):
		currTime = parseTime2Obj(inTimes[item])
		currCoord = inCoords[item]
		longitude,latitude = parseKMLCoord(currCoord)

		structedData.append({'time':currTime,'lat': latitude,'lon':longitude})

	return structedData

def loadSection(inTimes, inCoords, inData, inHeatMap):
	# parse all the data from a list of times and coordinates stored as strings	
	# for each entry convert the time to a time object and the lat long to floats and store in a list
	# check for existance of data in the dictionary if it exists add one to the count, if not add a new entry
	for item in range(len(inTimes)):
		currTime = parseTime2Obj(inTimes[item])
		currCoord = inCoords[item]
		longitude,latitude = parseKMLCoord(currCoord)

		inData.insert(0,{'time':currTime,'lat': latitude,'lon':longitude})
		if (latitude,longitude) in inHeatMap:
			inHeatMap[(latitude,longitude)] += 1
		else:
			inHeatMap[(latitude,longitude)] = 1

	return (inData, inHeatMap)

def createHeatMap(inData, inLevel):
	# take in dictionary a round lat longs to the DP specified in inLevel, negative values of inLevel 
	# round above the decimal point
	# ********* extend this to take in either a dict or an array *********
	outHeatMap = {}
	for value in inData:
		newLat = round(value['lat'], inLevel)
		newLong = round(value['lon'], inLevel)
		if (newLat,newLong) in outHeatMap:
			outHeatMap[(newLat,newLong)] = outHeatMap[(newLat,newLong)] + 1
		else:
			outHeatMap[(newLat,newLong)] = 1

	return(outHeatMap)

def describeHeatMap(inHeat):
	#******************** check and correct this function*****************
	description ={}
	for entry, value in inHeat.items():
		if value not in description:
			description[value] = 1
		else:
			description[value] += 1
	return description

def kmlDateCheck(inCurrentTime):
	#take in a time as a string, convert to a datetime object, if a user data file exists load the time value from it
	# compare the times and determine if the data needs updating, if no file exists assume minimum value of datetime
	currentTime = parseTime2Obj(inCurrentTime)

	if os.path.isfile('data.json'):
		json_data = open('data.json','r').read()
		readTime = json.loads(json_data)['time']
		storedCurrentTime = parseTime2Obj(readTime)
		readAll = False
	else:
		storedCurrentTime = datetime.datetime.min
		readTime = storedCurrentTime.isoformat()+'Z'
		readAll = True

	if currentTime > storedCurrentTime:
		return(True,readAll,readTime)
	else:
		return(False,readAll,readTime)

def extractYear(inData, inYear):
	# take in the structure data as a whole and extact the entries in which the year matches inYear
	outStructure=[]
	for entry in inData:
		if entry['time'].year == inYear:
			outStructure.append(entry)
	return(outStructure)

def extractMonth(inData, inYear, inMonth):
	# take in the structure data as a whole and extact the entries in which the year matches inYear and 
	# the month matches inMonth
	outStructure=[]
	for entry in inData:
		if entry['time'].year == inYear:
			if entry['time'].month == inMonth:
				outStructure.append(entry)
	return(outStructure)

def extractMonthFromYear(inData, inMonth):
	# take in an extracted year and extact the entries in which the month matches inMonth
	outStructure = []
	for entry in inData:
		if entry['time'].month == inMonth:
			outStructure.append(entry)
	return(outStructure)

def extractDay(inData, inYear, inMonth, inDay):
	# take in the structure data as a whole and extact the entries in which the year matches inYear and 
	# the month matches inMonth and the day matches inDay
	outStructure=[]
	for entry in inData:
		if entry['time'].year == inYear:
			if entry['time'].month == inMonth:
				if entry['time'].day == inDay:
					outStructure.append(entry)
	return(outStructure)

def extractDayFromMonth(inData, inDay):
	# take in an extracted month and extact the entries in which the day matches inDay
	outStructure = []
	for entry in inData:
		if entry['time'].day == inDay:
			outStructure.append(entry)
	return(outStructure)

def extractRange(inData, inStart, inEnd):
	# take in the structure data as a whole and extact the values between inStart and inEnd
	# inStart and inEnd should eb in datetime format
	outStructure = []
	for entry in inData:
		if (entry['time'] > inStart and entry['time'] < inEnd):
			outStructure.append(entry)
	return(outStructure)

def countryAnalysis():
	#get country boundary data set from  GMT
	#feed in a heatmap with 1/2 dp 
	#for entry in inheatmap:
		#check if in bounding box of country if so check off a set
	#return % of len set / len dataset

	pass


#def ringAround():

if __name__ == '__main__':
	main()
