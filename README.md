# University of Arizona Registrar Calendar Downloader

The University of Arizona Registrar's [Dates and Deadlines Calendar](https://registrar.arizona.edu/dates-and-deadlines) does not have a way to download the events into a .ics file for import into Google/Apple/Outlook Calendar so I made this Python script to get all the events using Selenium and BeautifulSoup. 

### Running The Script
Make sure Python 3 is installed, as is pip (which should be a given). Run the following command in the terminal at the folder location where the script is downloaded: 
```pip install -r requirements.txt && python3 registrar_calendar_downloader.py```

The script will prompt you several times to figure out which calendar you would like to download. Follow the prompts and then a .ics file will be saved to the folder in which the script is in. Sometimes the program will just crash because the registrar's website renders the options too slowly. Run the script again if this happens.