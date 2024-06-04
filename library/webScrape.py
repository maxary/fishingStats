import requests
import pprint
from bs4 import BeautifulSoup,SoupStrainer
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC


def getLinks(inputSoup,baseUrl, searchSchedule):
    #### This searches the main link to gather the links for each of the regions ###
    stockingScheuduleSoup = inputSoup.find(id=searchSchedule) 
    links = {}
    for link in stockingScheuduleSoup.find_all('a', href=True):
        links[link.contents[0]]=baseUrl+link['href']
    return links

def getScheduleTablesFromSite(url,region):
    ### Searches the link for the given region and sends back a table containing the stocking schedule for the region ###
    response = requests.get(url)
    html_data = response.text
    soup = BeautifulSoup(html_data, "html.parser")
    tableSoup = soup.find('table', attrs={'class':'table table-responsive table-bordered table-condensed table-hover table-striped'})
    rows = tableSoup.find_all('tr')
    data = []
    for row in rows:
        dataEntry = {}
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if cols: # Only add values if data is not empty
            dataEntry['Name'] = cols[0]
            dataEntry['Date'] = cols[1]
            dataEntry['Quantity'] = cols[2]
            data.append(dataEntry)

    data.pop(0) # Removing first entry since it only defines column titles which we don't need and is empty anyway
    return data

def getHistoricalTablesFromSite(url,region):
    ### Searches the link for the given region and sends back a table containing the stocking history for the region ###
    options = ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.implicitly_wait(30)

    page=1
    max_page = (driver.find_element(by='xpath', value="//li[@class='page-item page-last']")).text
    if (int(max_page)) > 5: max_page=5 ## We only care about recent stocking histories, so limit our searches to only the first few pages of data
    data = []

    ### Parse through each of the pages of data, collecting each page of data saving it off and contiue onto the next page
    while page<=max_page:
        time.sleep(10)
        wait = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//table[@class='table table-condensed table-hover']//tbody//tr[@data-index='24']//td[4]")))
        rows = driver.find_elements(by='xpath', value="//table[@class='table table-condensed table-hover']//tbody//tr")
        for row in rows:
            dataEntry = {}
            dataEntry['Name'] = row.find_element(by='xpath', value='./td[1]').text
            dataEntry['Tributary of'] = row.find_element(by='xpath', value='./td[2]').text
            dataEntry['County'] = row.find_element(by='xpath', value='./td[3]').text
            dataEntry['Species'] = row.find_element(by='xpath', value='./td[4]').text
            dataEntry['Quantity'] = row.find_element(by='xpath', value='./td[5]').text
            dataEntry['General Size'] = row.find_element(by='xpath', value='./td[6]').text
            dataEntry['Date'] = row.find_element(by='xpath', value='./td[7]').text 
            data.append(dataEntry)

        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='page-item page-next']//a[@class='page-link']"))).click()
        page=page+1
    
    driver.close()


    return data

def getInfoFromWebsite():
    ## MAIN FUNCTION ##
    ## This gather a list of links from the idaho government which contain tables of fish stocking data ###
    baseUrl = 'https://idfg.idaho.gov'
    url = '/fish/stocking#:~:text=Fish%20and%20Game%20stock%20over,rainbow%20trout%20and%20kokanee%20salmon.'
    response = requests.get(baseUrl+url)
    html_data = response.text
    soup = BeautifulSoup(html_data, "html.parser")
    stockingScheuduleLinks = getLinks(soup, baseUrl, 'stocking-schedule') 
    historicalStockingLinks = getLinks(soup, baseUrl, 'historical-stocking')
    #######

    ### For each region in Idaho, parse through the tables for each and save them off to send to the main.py ###
    historicalTable={}
    for region in historicalStockingLinks.keys():
        historicalTable[region] = getHistoricalTablesFromSite(historicalStockingLinks[region], region)
    stockingTable={}
    for region in stockingScheuduleLinks.keys():
        stockingTable[region] = getScheduleTablesFromSite(stockingScheuduleLinks[region], region)
    ### 

    completeTable={}
    completeTable['stockingSchedule']=stockingTable
    completeTable['stockingHistory']=historicalTable
    return completeTable

