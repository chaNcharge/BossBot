import mechanicalsoup

from collections import namedtuple

#Webscrape for holidays tie it region
def get_RegionHDays(R):
    regions = {
        'North America': 'https://www.qppstudio.net/public-holidays/north-america.htm',
        'Central America': 'https://www.qppstudio.net/public-holidays/central-america.htm',
        'South America': 'https://www.qppstudio.net/public-holidays/south-america.htm',
        'Europe': 'https://www.qppstudio.net/public-holidays/europe.htm',
        'Asia': 'https://www.qppstudio.net/public-holidays/asia.htm',
        'Middle East': 'https://www.qppstudio.net/public-holidays/middle-east.htm',
        'Africa': 'https://www.qppstudio.net/public-holidays/africa.htm',
        'Oceania': 'https://www.qppstudio.net/public-holidays/oceania.htm',
        'World': 'https://www.qppstudio.net/public-holidays/world.htm'
    }
    # retrive website based on region
    website = regions[R]
    # make request to website and retrive the content
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(website)
    # extract table header
    date_time = browser.page.find_all("time")
    dates = [value.text for value in date_time]
    #insert data in to database into database for user
    return dates