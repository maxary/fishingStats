import pymssql
from library import webScrape
import pprint

def insertIntoScheduleSQL(dataTable):
    #First as a precaution, lets delete everything in the Table"
    cursor.execute("DELETE FROM stockingSchedule")

    insert_query = """INSERT INTO stockingSchedule(region, name, date, quantity) VALUES (%s, %s, %s, %s)"""
    for region in dataTable.keys():
        for entry in dataTable[region]:
            cursor.execute(insert_query, (region,
                                    entry['Name'], 
                                    entry['Date'], 
                                    entry['Quantity']))                


def insertIntoHistorySQL(dataTable):
    #First as a precaution, lets delete everything in the Table"
    cursor.execute("DELETE FROM stockingHistory")

    insert_query = """INSERT INTO stockingHistory(region, name, date, quantity) VALUES (%s, %s, %s, %s)"""
    for region in dataTable.keys():
        for entry in dataTable[region]:
            cursor.execute(insert_query, (region,
                                    entry['Name'], 
                                    entry['Date'], 
                                    entry['Quantity']
                                    ))  

def calculatedBestFishingSpot():
    # General equation based on fish stocking survival rate research:
    # value = CurrentYearStockingQuantity + CurrentYear-1StockingQuantity*0.78/1 + CurrentYear-2StockingQuantity*0.78/2 + .....

    projectedFishTable = {}
    for region in completeTable['stockingSchedule'].keys():
        projectedFishTable[region]={}
        for entry in completeTable['stockingSchedule'][region]:
            projectedFishTable[region][entry['Name']] = float(entry['Quantity'].replace(",", ""))

    for region in completeTable['stockingHistory'].keys():
        for entry in completeTable['stockingHistory'][region]:
            if int((entry['Date'].split('/'))[2]) == 2024:
                projectedFishTable[region][entry['Name']] = float(entry['Quantity'].replace(",", ""))
            else:
                stockedYearValue = 2024 - int((entry['Date'].split('/'))[2]) # Grab the year that it was stocked
                if entry['Name'] not in projectedFishTable[region]:
                    projectedFishTable[region][entry['Name']]=float(0)
                projectedFishTable[region][entry['Name']]+= float(entry['Quantity'].replace(",", ""))*(0.78/stockedYearValue)

    return projectedFishTable

# Localhost/SQL information
SERVER = 'localhost'
DATABASE = 'FishingStats'
USERNAME = 'sa'
PASSWORD = 'tempPass'
TCON = 'yes'

# Connect to Idaho fish and game website and gather the data there
conn = pymssql.connect(SERVER, USERNAME, PASSWORD, DATABASE)
cursor = conn.cursor(as_dict=True)
completeTable = webScrape.getInfoFromWebsite()

#Create the tables if they don't exists in SQL, then add all the data to them
cursor.execute("""IF (NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].stockingHistory') AND type in (N'U'))) 
                    BEGIN 
                        CREATE TABLE stockingHistory (region VARCHAR(255), 
                                                      name VARCHAR(255), 
                                                      date VARCHAR(255),    
                                                      quantity VARCHAR(255)) 
                    END""")
insertIntoHistorySQL(completeTable['stockingHistory'])

cursor.execute("""IF (NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].stockingSchedule') AND type in (N'U'))) 
                    BEGIN 
                        CREATE TABLE stockingSchedule (region VARCHAR(255), 
                                                       name VARCHAR(255), 
                                                       date VARCHAR(255), 
                                                       quantity VARCHAR(255)) 
                    END""")
insertIntoScheduleSQL(completeTable['stockingSchedule'])

projectedFishTable = calculatedBestFishingSpot()

# Finally, print off the values of the bodies of water in descening order by region
print('Southwest Region')
print({k: v for k, v in sorted(projectedFishTable['Southwest Region'].items(), reverse=True, key=lambda item: item[1])})
print('')

print('Salmon Region')
print({k: v for k, v in sorted(projectedFishTable['Salmon Region'].items(), reverse=True, key=lambda item: item[1])})
print('')

print('Magic Valley Region')
print({k: v for k, v in sorted(projectedFishTable['Magic Valley Region'].items(), reverse=True, key=lambda item: item[1])})
print('')

print('Panhandle Region')
print({k: v for k, v in sorted(projectedFishTable['Panhandle Region'].items(), reverse=True, key=lambda item: item[1])})
print('')

print('Clearwater Region')
print({k: v for k, v in sorted(projectedFishTable['Clearwater Region'].items(), reverse=True, key=lambda item: item[1])})
print('')

print('Southeast Region')
print({k: v for k, v in sorted(projectedFishTable['Southeast Region'].items(), reverse=True, key=lambda item: item[1])})
print('')

print('Upper Snake Region')
print({k: v for k, v in sorted(projectedFishTable['Upper Snake Region'].items(), reverse=True, key=lambda item: item[1])})
print('')

conn.commit()
cursor.close()
conn.close()