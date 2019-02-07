import requests
import zipfile
import time
import csv
import sqlite3
import configparser
import os
import sys

#Get the directory where the script is located
directory = os.path.abspath(os.path.dirname(sys.argv[0]))

#Gets the Charging Station specific configuration set in the Charges.config file
config = configparser.ConfigParser()
config.read(directory + '/Charges.config')

username = config['DEFAULT']['username']
password = config['DEFAULT']['password']
ip = config['DEFAULT']['ip']

ts = int(time.time()*1000)

#Create Session so cookies can be used
s = requests.Session()

#Data to send in the post request, this sends the username and password
#to the login page to create a session.
data = '{"username":"' + username + '","password":"' + password + '"}'

i=s.post('http://' + ip + '/ajax.php', data=data)
print("Collecting Data from Wallbox")

#Get the full loge from the BMW Wallbox Connect
r = s.get('http://' + ip + '/logging.php?getlogszip&t='+str(ts))

#Unzip the logfiles
f = open(directory + '/ChargingData/charges.zip', 'wb')
for chunk in r.iter_content(chunk_size=512 * 1024):
  if chunk: # filter out keep-alive new chunks
    f.write(chunk)
f.close()

zip_ref = zipfile.ZipFile(directory + '/ChargingData/charges.zip', 'r')
zip_ref.extractall(directory + '/ChargingData/')
zip_ref.close()

print("Data Collected")
print("Opening DB")

#In the log files you will find the BMW Wallbox Connect Database. This is an
#sqlite db
connDB = sqlite3.connect(directory + '/ChargingData/database.db')
connCharges = sqlite3.connect(directory + '/charges.db')

db = connDB.cursor()
chargesdb = connCharges.cursor()

#Fetch the needed data from the downloaded DB
db.execute("SELECT ID,SESSIONSEQUENCEID,SESSIONSTARTDATE,SESSIONENDDATE,STARTINGMETERVALUE_ID,ENDINGMETERVALUE_ID,CHARGINGTOKEN_ID FROM CHARGINGSESSION WHERE SESSIONENDDATE AND STARTINGMETERVALUE_ID IS NOT NULL")
rows = db.fetchall()

for row in rows:
  session = row[1]
  startdate = row[2]
  enddate= row[3]
  db.execute("SELECT METERVALUE FROM METERREADING WHERE ID = " + str(row[4]) )
  startmeter = db.fetchall()
  db.execute("SELECT METERVALUE FROM METERREADING WHERE ID = " + str(row[5]) )
  endmeter = db.fetchall()
  token = row[6]
  energy = endmeter[0][0]-startmeter[0][0]
  chargesdb.execute("INSERT OR IGNORE INTO Charges (SESSIONID,STARTDATE,ENDDATE,ENERGY,TOKEN) VALUES('" + str(session) +"', '" + str(startdate) +"', '" + str(enddate) +"', '" + str(energy) +"','" + str(token) +"')")
connCharges.commit()
connDB.close()

data=[]

print("Loading Charges into DB")

#Load the data from the downloaded DB into our local DB and output the data also to .csv
chargesdb.execute("SELECT SESSIONID,STARTDATE,ENDDATE,ENERGY,TOKEN FROM Charges ORDER BY STARTDATE")
rows = chargesdb.fetchall()

for row in rows:
  startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[1]/1000.0))
  endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[2]/1000.0))
  energyUsed = row[3]/1000
  rowData = {'ID':row[0],'SESSIONSTARTDATE':startTime,'SESSIONENDDATE':endTime,'ENERGYUSED':energyUsed,'TOKEN':row[4]}
  data.append(rowData.copy())

keys = data[0].keys()
with open(directory + '/charges.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, fieldnames=["ID","SESSIONSTARTDATE", "SESSIONENDDATE","ENERGYUSED","TOKEN"])
    dict_writer.writeheader()
    dict_writer.writerows(data)


connCharges.close()
print("Data Processing completed, check charges.csv")
