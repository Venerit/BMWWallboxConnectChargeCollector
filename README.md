# BMWWallboxConnectChargeCollector
This Python script collects and stores charging sessions from a BMW Wallbox Connect Charger.
As BMW only provides an app to collect the charges of the last 30 days this script creates a local database and stores
the charges as long as you run the script on a daily basis. It then converts the local database to a csv file which you can then
easily import in XLS.
The script output will contain the following fields: ID,SESSIONSTARTDATE,SESSIONENDDATE,ENERGYUSED,TOKEN.<br>
ID: Unique ID only used in the DB, so not really relevant<br>
SESSIONSTARTDATE: start date of the charging session<br>
SESSIONENDDATE: end date of the charging session<br>
ENERGYUSED: energy used during the charging session in Wh<br>
TOKEN: Which token was used during the charging, a BMW Wallbox Connect comes with 4 RFID cards for 4 different users<br>
<br>
This script was developed for Python3.6<br>
Python modules used:requests, zipfile, time, csv, sqlite3, configparser<br>
<br>
I'm not a professional coder by any means, I'm just providing this script as the 30 days limitation on the app was really annoying.<br>
<br>
Usage:<br>
Step 1:<br>
Change the name of the Charges.config.example to Charges.config and adjust the content to reflect your situation. It should be self-explanatory<br>
Step 2:<br>
Rename the charges.db.new file to charges.db<br>
Step 3:<br>
Set up a cron job to run daily, the DB in the Wallbox only stores a small amount of charges, so it's best to run the script once a day to make sure you collect all charges.<br><br>
Example:<br>
From Ubuntu run crontab -e and put in the below crontab configuration<br>
MAILTO=""<br>
SHELL="/bin/bash"<br>
00 14   * * *   python3 /home/user/Charging/GetCharges.py<br>
