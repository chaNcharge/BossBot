import mechanicalsoup

from collections import namedtuple

#Webscrape for holidays tie it region
def get_RegionHDays(cur, con):
    regions = [
        ('North America' ,'https://www.qppstudio.net/public-holidays/north-america.htm'),
        ('Central America', 'https://www.qppstudio.net/public-holidays/central-america.htm'),
        ('South America', 'https://www.qppstudio.net/public-holidays/south-america.htm'),
        ('Europe', 'https://www.qppstudio.net/public-holidays/europe.htm'),
        ('Asia', 'https://www.qppstudio.net/public-holidays/asia.htm'),
        ('Middle East', 'https://www.qppstudio.net/public-holidays/middle-east.htm'),
        ('Africa', 'https://www.qppstudio.net/public-holidays/africa.htm'),
        ('Oceania' , 'https://www.qppstudio.net/public-holidays/oceania.htm'),
        ('World','https://www.qppstudio.net/public-holidays/world.htm')
        ]
    for region, website in regions:
        # make request to website and retrive the content
        browser = mechanicalsoup.StatefulBrowser()
        browser.open(website)
        # extract table header
        date_time = browser.page.find_all("time")
        dates = [value.text for value in date_time]
        #create a named tuple to store the region and assocated holidays
        Holiday = namedtuple("Holiday",["region", "holiday"])
        holiday = Holiday(region= region, holiday=dates)
        #maybe need to make it into a dataframe using pandas where region is coloum 1 and the holiday dates are in coloum 2
        #insert data in to database
        cur.execute("INSERT INTO schedule (region,holiday) VALUES(?,?)", (holiday.region,holiday.holiday))
        con.commit()