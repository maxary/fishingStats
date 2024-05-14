import requests
from bs4 import BeautifulSoup,SoupStrainer


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
    print(rows)
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    data.pop(0) # Removing first entry since it only defines column titles which we don't need and is empty anyway
    return data

def getHistoricalTablesFromSite(url,region):
    ### Searches the link for the given region and sends back a table containing the stocking history for the region ###
    response = requests.get(url)
    html_data = response.text
    soup = BeautifulSoup(html_data, "html.parser")
    tableSoup = soup.find('table', attrs={'class':'table table-condensed table-hover'})
    print(soup)
    rows = tableSoup.find_all('tr')
    print(rows)
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    data.pop(0) # Removing first entry since it only defines column titles which we don't need and is empty anyway
    print(data)
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
        return 0
    stockingTable={}
    """ for region in stockingScheuduleLinks.keys():
        stockingTable[region] = getScheduleTablesFromSite(stockingScheuduleLinks[region], region)
    ### """

    completeTable={}
    completeTable['Stocking Schedule']=stockingTable
    completeTable['Historical Stocking']=historicalTable
    return completeTable

