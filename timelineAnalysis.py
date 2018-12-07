import lxml
import os 
from fastkml import kml
import sys
import pickle
import json
from matplotlib import pyplot
import requests
import datetime

def main():
	scriptStartTime = datetime.datetime.now()
	myGmapsAPIKey = ''

	cur_path = os.path.dirname(os.path.realpath(__file__))
	filePath = cur_path + "/HistoryKML/LocationHistory.KML"
	tree = lxml.etree.parse(filePath)

	coords = tree.xpath("//gx:coord/text()",namespaces={'gx':'http://www.google.com/kml/ext/2.2'})
	times = tree.xpath("//xmlns:when/text()", namespaces={'xmlns':'http://www.opengis.net/kml/2.2'})
	updateData, noData ,since = kmlDateCheck(times[0])

	prepTime = datetime.datetime.now()
	print('prep time \t\t\t\t {}'.format(prepTime - scriptStartTime))

	if os.path.isfile('parsedKML.pickle'):
		pickleStartTime = datetime.datetime.now()
		pickle_in = open("parsedKML.pickle","rb")
		structedData = pickle.load(pickle_in)
		pickle_in = open("heatData.pickle","rb")
		heatmapData = pickle.load(pickle_in)
		pickle_in = open("heatDataLong.pickle","rb")
		longheatmap = pickle.load(pickle_in)
		pickleEndTime = datetime.datetime.now()	
		print('unpickling time is\t\t {}'.format(pickleEndTime - pickleStartTime))
		if updateData:
			print('update the data')
			for ind, value in enumerate(times):
				if value == since:
					removeFrom = ind + 1
					break
			print(removeFrom)
			timesToUpdate = times[:removeFrom]
			coordsToUpdate = coords[:removeFrom]
			structedData, heatmapData, longheatmap = loadSection(timesToUpdate,coordsToUpdate, structedData, heatmapData, longheatmap)
			with open('data.json', 'w') as outfile:
				json.dump(times[0], outfile)

	else:
		loadAllStart = datetime.datetime.now()
		structedData, heatmapData, longheatmap = loadAll(times, coords)
		loadAllEnd = datetime.datetime.now()
		print('load all time is \t\t {}'.format(loadAllEnd - loadAllStart))
		pickle_out = open("parsedKML.pickle","wb")
		pickle.dump(structedData, pickle_out)
		pickle_out.close()
		pickle_out = open("heatData.pickle","wb")
		pickle.dump(heatmapData, pickle_out)
		pickle_out.close()
		pickle_out = open("heatDataLong.pickle","wb")
		pickle.dump(longheatmap, pickle_out)
		pickle_out.close()

	oneCoord = coords[0]
	(oneLong,oneLat) = parseKMLCoord(oneCoord)
	print(oneLong)
	print(oneLat)

	extratYearStart = datetime.datetime.now()
	my2018Data = extractYear(structedData, 2018)
	extratYearEnd = datetime.datetime.now()	
	print('extracting 1 year took {}'.format(extratYearEnd - extratYearStart))

	extractMonthStart = datetime.datetime.now()
	my2018MarData = extractMonth(structedData, 2018, 3)
	extractMonthEnd = datetime.datetime.now()
	print('extracting month with month1 took {}'.format(extractMonthEnd - extractMonthStart))

	extractMonthStart2 = datetime.datetime.now()
	my2018MarData2 = extractMonthFromYear(my2018Data, 10)
	extractMonthEnd2 = datetime.datetime.now()
	print('extracting month with month2 took {}\n'.format(extractMonthEnd2 - extractMonthStart2))

	extractDayStart = datetime.datetime.now()
	my2018Oct10Data = extractDay(structedData, 2018, 10, 3)
	extractDayEnd = datetime.datetime.now()
	print('extracting day with day1 took {}'.format(extractDayEnd - extractDayStart))
	print(len(my2018Oct10Data))

	extractDayStart2 = datetime.datetime.now()
	my2018Oct10Data2 = extractDayFromMonth(my2018MarData, 3)
	extractDayEnd2 = datetime.datetime.now()
	print('extracting day with day2 took {}'.format(extractDayEnd2 - extractDayStart2))
	print(len(my2018Oct10Data))


	startRangeToExtract = datetime.datetime(2017,8,1)
	endRangeToExtract = datetime.datetime(2018,8,31)

	extractRangeStart = datetime.datetime.now()
	myRange = extractRange(structedData,startRangeToExtract, endRangeToExtract)
	extractRangeEnd = datetime.datetime.now()
	print('extracting range took {}'.format(extractRangeEnd - extractRangeStart))

	#myRequest = 'https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&key={}'.format(oneLat,oneLong,myGmapsAPIKey)
	#response =requests.get(myRequest)
	#print(response.json())

def parseTime2oBJ(inTime):
	timeObj = datetime.datetime.strptime(inTime, '%Y-%m-%dT%H:%M:%SZ')
	return(timeObj)

def parseKMLCoord(inCoord):
	longitude,latitude, _ = inCoord.split(' ')
	intLat = float(latitude)
	intLong = float(longitude)
	return (intLong, intLat)

def loadAll(inTimes, inCoords):
	structedData = []
	heatmapDict = {}
	heatmapDict2 = {}

	for item in range(len(inTimes)):
		currTime = parseTime2oBJ(inTimes[item])
		currCoord = inCoords[item]
		longitude,latitude = parseKMLCoord(currCoord)
		longitudeR = round(longitude, 4)
		latitudeR = round(latitude, 4)

		structedData.append({'time':currTime,'lat': latitude,'lon':longitude})
		if (latitudeR,longitudeR) in heatmapDict:
			heatmapDict[(latitudeR,longitudeR)] += 1
		else:
			heatmapDict[(latitudeR,longitudeR)] = 1
		if (latitude,longitude) in heatmapDict2:
			heatmapDict2[(latitude,longitude)] += 1
		else:
			heatmapDict2[(latitude,longitude)] = 1

	return (structedData, heatmapDict, heatmapDict2)

def loadSection(inTimes, inCoords, inData, inHeatMap, inHeatMap2):
	for item in range(len(inTimes)):
		currTime = parseTime2oBJ(inTimes[item])
		currCoord = inCoords[item]
		longitude,latitude = parseKMLCoord(currCoord)
		longitudeR = round(longitude, 4)
		latitudeR = round(latitude, 4)

		inData.insert(0,{'time':currTime,'lat': latitude,'lon':longitude})
		if (latitudeR,longitudeR) in inHeatMap:
			inHeatMap[(latitudeR,longitudeR)] += 1
		else:
			inHeatMap[(latitudeR,longitudeR)] = 1
		if (latitude,longitude) in inHeatMap2:
			inHeatMap2[(latitude,longitude)] += 1
		else:
			inHeatMap2[(latitude,longitude)] = 1
	return (inData, inHeatMap, inHeatMap2)


def describeHeatMap(inHeat):
	description ={}
	for entry, value in inHeat.items():
		if value not in description:
			description[value] = 1
		else:
			description[value] += 1
	return description

def kmlDateCheck(inCurrentTime):
	currentTime = parseTime2oBJ(inCurrentTime)

	if os.path.isfile('data.json'):
		json_data = open('data.json','r').read()
		readTime = json.loads(json_data)
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
	outStructure=[]
	for entry in inData:
		if entry['time'].year == inYear:
			outStructure.append(entry)
	return(outStructure)

def extractMonth(inData, inYear, inMonth):
	outStructure=[]
	for entry in inData:
		if entry['time'].year == inYear:
			if entry['time'].month == inMonth:
				outStructure.append(entry)
	return(outStructure)

def extractMonthFromYear(inData, inMonth):
	outStructure = []
	for entry in inData:
		if entry['time'].month == inMonth:
			outStructure.append(entry)
	return(outStructure)


def extractDay(inData, inYear, inMonth, inDay):
	outStructure=[]
	for entry in inData:
		if entry['time'].year == inYear:
			if entry['time'].month == inMonth:
				if entry['time'].day == inDay:
					outStructure.append(entry)
	return(outStructure)

def extractDayFromMonth(inData, inDay):
	outStructure = []
	for entry in inData:
		if entry['time'].day == inDay:
			outStructure.append(entry)
	return(outStructure)

def extractRange(inData, inStart, inEnd):
	outStructure = []
	for entry in inData:
		if (entry['time'] > inStart and entry['time'] < inEnd):
			outStructure.append(entry)
	return(outStructure)


#def printShortDescp(inData):
#def ringAround():

if __name__ == '__main__':
	main()
