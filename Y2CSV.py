from selenium import webdriver
from bs4 import BeautifulSoup as BS
from bs4 import SoupStrainer as SS
import datetime
import time
import csv
import argparse

#  Get command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("businesstype", help="Enter the business type you are searching for.")
parser.add_argument("businesslocation", help="Enter the location of the business you are looking for,"
											  " if more than one word use '+' to join them together.")
args = parser.parse_args()

#  Set search parameters from parsed arguments - Yell returns max 250 results
busType = args.businesstype
busLoc = args.businesslocation

busData = []

#  loop through pages - 25 results per page - allow for 10 pages starting at 1
for i in range(1, 11):

	#  search URL
	URL = "https://www.yell.com/ucs/UcsSearchAction.do?find=Y&keywords={0}&location={1}&pageNum={2}".format(busType,
																											busLoc, i)
	#  Define browser driver
	driver = webdriver.Chrome()

	#  Collect webpage contents
	driver.get(URL)
	page_source = driver.page_source

	#  Define listings part of page
	divs = SS(class_="col-sm-15 col-md-14 col-lg-15 businessCapsule--mainContent")

	#  parse only the parts of the page listed above
	soup = BS(page_source, 'html.parser', parse_only=divs)
	print('Collecting data...')
	#  Loop through retrieved data extracting information - try/except those that dont always have data
	for each in soup:
		busName = each.find('span', class_="businessCapsule--name").text
		busNo = each.find('span', class_="business--telephoneNumber").text

		try:
			busDesc = each.find(attrs={'itemprop': 'description'}).text
		except:
			busDesc = ''

		try:
			busAddrStreet = each.find(attrs={'itemprop': 'streetAddress'}).text
		except:
			busAddrStreet = ''

		try:
			busAddrLocality = each.find(attrs={'itemprop': 'addressLocality'}).text
		except:
			busAddrLocality = ''

		try:
			busAddrPostCode = each.find(attrs={'itemprop': 'postalCode'}).text
		except:
			busAddrPostCode = ''

		try:
			busWeb = each.find(attrs={'data-tracking': 'WL:CLOSED'}).get('href')
		except:
			busWeb = ''

		#  Create dictionary of information for insertion in to list
		dataString = {}
		dataString['busName'] = busName
		dataString['busNo'] = busNo
		dataString['busDesc'] = busDesc

		#  If there is an address than place a comma between locality and post code
		if len(busAddrStreet) > 0:
			dataString['busAddr'] = busAddrStreet + busAddrLocality + ', ' + busAddrPostCode
		else:
			dataString['busAddr'] = ''

		dataString['busWeb'] = busWeb

		#  Add business data to a list
		busData.append(dataString)

	#  If less than 10 pages of results (250) then break out of the loop
	if len(soup) == 0:
		driver.close()
		break

	#  Delay polling pages to avoid captcha
	time.sleep(2)

	#  Close browser window
	driver.close()

#  Create file name for CSV
filename = str(datetime.date.today()) + busType + busLoc + '.csv'

#  Write data to CSV file
with open(filename, 'w') as f:
	writer = csv.writer(f)
	for i in range(0, len(busData)):
		row = (busData[i]['busName'], busData[i]['busAddr'], busData[i]['busNo'])
		print(row)
		writer.writerow(row)

print('Results written to: {}'.format(filename))
