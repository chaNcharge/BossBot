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
    # Retrieve website based on region
    website = regions.get(R)
    if not website:
        return None

    # Make request to website and retrieve the content
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(website)

    # Extract dates with specified datetime attribute
    dates = []
    for time_elem in browser.page.find_all("time", {"datetime": True}):
        dates.append(time_elem['datetime'])

    # Insert data into database for user
    return dates