import requests
import csv
import math
import time
import Queue
import re
from robobrowser import RoboBrowser
from datetime import datetime

def login():
	"""Used to login into a server
	returns a robobrowser instance logined in
	"""
	s = requests.Session()
	s.headers['User-Agent'] = 'Mozilla (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7'
	browser = RoboBrowser(history=True, parser='html5lib', session=s)

	browser.open('http://en.ogame.gameforge.com')

	loginForm = browser.get_form('loginForm')
	print loginForm['uni'].value
	print loginForm['login'].value
	print loginForm['pass'].value

	loginForm['uni'].value = 'SERVER URL'
	loginForm['login'].value = 'USERNAME'
	loginForm['pass'].value = 'PASSWORD'

	browser.submit_form(loginForm)

	if 'loginError' in browser.url:
		print 'loginError'
		return None

	return browser

def getBuildingCost(buildingName, level):
	"""Calculates what the "buildingName" will cost at the given level.
	Returns a cost dict containing metal, crystal, duet and power costs
	"""

	baseDict = {}
	with open(r'./buildingsBaseCost.csv', 'r') as baseCostFile:
		reader = csv.DictReader(baseCostFile)
		for row in reader:
			baseDict[row['Building']] = row

	buildingName = buildingName.lower()
	if buildingName not in baseDict.keys():
		print 'Building', buildingName, 'unkown'
		return None

	baseMetal = int(baseDict[buildingName]['Metal'])
	baseCrystal = int(baseDict[buildingName]['Crystal'])
	baseDeut = int(baseDict[buildingName]['Deuterium'])

	metalCost = None
	crystalCost = None
	deutCost = None
	base = None
	if buildingName in ['metal mine', 'solar plant', 'deuterium synthesizer']:
		base = 1.5
	elif buildingName == 'crystal mine':
		base = 1.6
	elif buildingName == 'fusion reactor':
		base = 1.8
	else:
		base = 2.0

	costDict = {}
	costDict['metalCost'] = int(baseMetal * math.pow(base, level-1))
	costDict['crystalCost'] = int(baseCrystal * math.pow(base, level-1))
	costDict['deutCost'] = int(baseDeut * math.pow(base, level-1))

	powerCost = 0
	basePowerCost = 0
	if buildingName in ['metal mine', 'crystal mine', 'fusion reactor']:
		basePowerCost = 10
	elif buildingName == 'deuterium synthesizer':
		basePowerCost = 20

	costDict['powerCost'] = basePowerCost * level * math.pow(1.1, level)

	return costDict

def getCurrentLevels():
	"""Reads currentLevels.csv
	returns a dictionary of your current Building levels
	"""
	levelDict = {}
	with open(r'./currentLevels.csv', 'r') as currentLevels:
		reader = csv.DictReader(currentLevels)
		for row in reader:
			levelDict[row['building']] = row['currentLevel']

	print levelDict

def getStorageCapacity(currentLevel):
	return 5000 * int(2.5 * math.exp(20 * currentLevel / 33.0))

def getProductionTime(category, name, infoDict):
	category = category.lower()
	name = name.lower()

	if category in 'ships and defense':
		pass
	elif category in 'buildings':
		numerator  = infoDict['metalCost'] + infoDict['crystalCost']
		denominator = 2500.0 * (1 + infoDict['roboticsLevel']) * infoDict['universeSpeed'] * math.pow(2, infoDict['nanitesLevel'])
	
	hours = numerator/denominator
	seconds = 3600 * hours

	print seconds

def getProductionPerSecond(buildingName, level):
	pass
 
def getBuildQueue():
	"""Used to determine what to build next
	Returns a queue from the buildQueue.csv, or if thats empty the defaultRotation.csv
	"""
	buildQueue = Queue.Queue()

 	with open(r'./buildQueue.csv', 'r') as buildQueueFile:
 		reader = csv.DictReader(buildQueueFile)
 		for row in reader:
 			buildQueue.put(row['nextBuilding'])

 	if buildQueue.empty():
 		with open(r'./defaultRotation.csv', 'r') as defaultRotation:
 			reader = csv.DictReader(defaultRotation)
 			for row in reader:
 				buildQueue.put(row['nextBuilding'])

 	return buildQueue

def buildCheck(browser, buildingName, currentLevel):
	pass

def buildResource(browser, buildingName):
	"""Clicks the appropriate button to build given buildingName
	"""
	browser.open('http://s135-en.ogame.gameforge.com/game/index.php?page=resources')

	#finds the buttons for each building, The html doesnt have clear id names, so we have to map buttonN to building name
	buildingIdDict = {}
	buildingIdDict['metal mine'] = 'button1'
	buildingIdDict['crystal mine'] = 'button2'
	buildingIdDict['duet mine'] = 'button3'
	buildingIdDict['solar plant'] = 'button4'
	buildingIdDict['fusion reactor'] = 'button5'
	buildingIdDict['solar satellite'] = 'button6'
	buildingIdDict['metal storage'] = 'button7'
	buildingIdDict['crystal storage'] = 'button8'
	buildingIdDict['duet storage'] = 'button9'

	button = browser.find(id=buildingIdDict[buildingName.lower()])
	buttonLinks = button.find_all('a')

def submitQuickBuild(browser, buttonLink):
	#extract the build link that they send through javascript onclick. And just open a new link to that, which will start the build
	buildLink = buttonLink['onclick']
	buildLink = re.search(".*'(.*)'.*", buildLink)
	buildLink = buildLink.group(1)
	browser.open(buildLink)

def getLevelFromButton(browser, buttonLink):
	#extract the digits from the text in span class="level"
	currentLevel = buttonLinks[1].find(class_="ecke")
	currentLevel = currentLevel.find(class_="level").text
	currentLevel = int(re.sub(r"\D", "", currentLevel))

	return currentLevel

def getCurrentResources(browser):
	currentResources = {}
	currentResources['metal'] = browser.find(id="resources_metal").text
	currentResources['crystal'] = browser.find(id="resources_crystal").text
	currentResources['duet'] = browser.find(id="resources_deuterium").text

	return currentResources

def main():

	getStorageCapacity(10)
	getCurrentLevels()

	costDict = getBuildingCost('metal mine', 7)
	infoDict = costDict.copy()
	infoDict['roboticsLevel'] = 0
	infoDict['universeSpeed'] = 5
	infoDict['nanitesLevel'] = 0
	print infoDict
	getProductionTime('building', 'metal mine', infoDict)

	buildQueue = getBuildQueue()

	while(not buildQueue.empty()):
		print buildQueue.get()

	browser = login()
	
	if browser:

		time.sleep(7)
		
		buildResource(browser, 'metal mine')

		print browser


	# print 'Done', datetime.now()
	
if __name__ == '__main__':
	main()