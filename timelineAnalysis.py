import lxml
import os 
from fastkml import kml
import sys
import pickle
import json
import requests
import datetime
import collections

# the format of the structured data is a list like => {'time':currTime,'lat': latitude,'lon':longitude}
# the format of the heatmap data is a dict like (latitude,longitude) : int

def main():

	#fill in API key
	myGmapsAPIKey = ''
	#fill in relative path to KML file, have it in a folder due to a JSON file being stored as well
	cur_path = os.path.dirname(os.path.realpath(__file__))
	filePath = cur_path + "/HistoryKML/LocationHistory.KML"
	
	structedData, heatmapData = prepareData(filePath)

	#testing funcitons for extracting parts of the data
	my2018Data = extractYear(structedData, 2018)

	startRangeToExtract = datetime.datetime(2017,8,1)
	endRangeToExtract = datetime.datetime(2018,8,31)
	myRange = extractRange(structedData,startRangeToExtract, endRangeToExtract)

	#myRequest = 'https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&key={}'.format(oneLat,oneLong,myGmapsAPIKey)
	#response =requests.get(myRequest)
	#print(response.json())


def prepareData(inFilePath):
	
	tree = lxml.etree.parse(inFilePath)
	#check most recent entry in the KML file and check it again the most recent stored in my own data
	coords = tree.xpath("//gx:coord/text()",namespaces={'gx':'http://www.google.com/kml/ext/2.2'})
	times = tree.xpath("//xmlns:when/text()", namespaces={'xmlns':'http://www.opengis.net/kml/2.2'})
	updateData, noData ,since = kmlDateCheck(times[0])
	#check for a local parsed version of the data
	if os.path.isfile('parsedKML.pickle'):
		#if it exists and need updating add the new entries to the start of the file
		structedData, heatmapData = unpickleData()
		if updateData:
			for ind, value in enumerate(times):
				if value == since:
					removeFrom = ind + 1
					break
			timesToUpdate = times[:removeFrom]
			coordsToUpdate = coords[:removeFrom]
			structedData, heatmapData = loadSection(timesToUpdate,coordsToUpdate, structedData, heatmapData)
			#oce the data has been updated add the newest time to my data file and then pickle 
			#the parsed data for future useage
			with open('data.json', 'w') as outfile:
				json.dump({'time':times[0]}, outfile, indent=4)
			pickleData(structedData, heatmapData)
	else:
		#if it doesnt exist load all from file and generate a heatmap and a date object list of the data
		structedData, heatmapData = loadAll(times, coords)
		pickleData(structedData, heatmapData)
		with open('data.json', 'w') as outfile:
			json.dump({'time':times[0]}, outfile, indent=4)
	return(structedData, heatmapData)

def parseTime2oBJ(inTime):
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
	heatmapDict = {}
	# for each entry convert the time to a time object and the lat long to floats and store in a list
	# check for existance of data in the dictionary if it exists add one to the count, if not add a new entry
	for item in range(len(inTimes)):
		currTime = parseTime2oBJ(inTimes[item])
		currCoord = inCoords[item]
		longitude,latitude = parseKMLCoord(currCoord)

		structedData.append({'time':currTime,'lat': latitude,'lon':longitude})
		if (latitude,longitude) in heatmapDict:
			heatmapDict[(latitude,longitude)] += 1
		else:
			heatmapDict[(latitude,longitude)] = 1

	return (structedData, heatmapDict)

def loadSection(inTimes, inCoords, inData, inHeatMap):
	# parse all the data from a list of times and coordinates stored as strings	
	# for each entry convert the time to a time object and the lat long to floats and store in a list
	# check for existance of data in the dictionary if it exists add one to the count, if not add a new entry
	for item in range(len(inTimes)):
		currTime = parseTime2oBJ(inTimes[item])
		currCoord = inCoords[item]
		longitude,latitude = parseKMLCoord(currCoord)

		inData.insert(0,{'time':currTime,'lat': latitude,'lon':longitude})
		if (latitude,longitude) in inHeatMap:
			inHeatMap[(latitude,longitude)] += 1
		else:
			inHeatMap[(latitude,longitude)] = 1

	return (inData, inHeatMap)

def pickleData(inData, inHeatMap, inHeatMapLong):
		pickle_out = open("parsedKML.pickle","wb")
		pickle.dump(inData, pickle_out)
		pickle_out.close()
		pickle_out = open("heatData.pickle","wb")
		pickle.dump(inHeatMap, pickle_out)
		pickle_out.close()
		pickle_out = open("heatDataLong.pickle","wb")
		pickle.dump(inHeatMapLong, pickle_out)
		pickle_out.close()
		print('Pickled Data')

def unpickleData():
	pickle_in = open("parsedKML.pickle","rb")
	outData = pickle.load(pickle_in)
	pickle_in = open("heatData.pickle","rb")
	heatmap = pickle.load(pickle_in)
	
	return(outData,heatmap)

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
	currentTime = parseTime2oBJ(inCurrentTime)

	if os.path.isfile('data.json'):
		json_data = open('data.json','r').read()
		readTime = json.loads(json_data)['time']
		storedCurrentTime = parseTime2oBJ(readTime)
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

def getSquare(lllon, lllat, urlon, urlat, inData):
	# take in the four corners of a squre and either the keys of a heatamp dict or a 
	# list of all the parsed data return a list of lat and long points within the specified bounds
	if isinstance(inData, collections.KeysView): 
		outDataLat = []
		outDataLon = []
		counter = 0
		for item in inData:
			if (item[1] > lllon and item[0] > lllat and urlon > item[1] and urlat > item[0]):
				outDataLat.append(item[0])
				outDataLon.append(item[1])
				counter += 1
	elif isinstance(inData, list):
		outDataLat = []
		outDataLon = []
		counter = 0
		for item in inData:
			if (item['lon'] > lllon and item['lat'] > lllat and urlon > item['lon'] and urlat > item['lat']):
				outDataLat.append(item['lat'])
				outDataLon.append(item['lon'])
				counter += 1				
	return(outDataLon, outDataLat)


#def printShortDescp(inData):
#def ringAround():

if __name__ == '__main__':
	main()
