#quote_of_the_day
import requests
import json

def get_quote_of_the_day():
    response = requests.get("https://www.brainyquote.com/quote_of_the_day/qod.json")
    if response.status_code == 200:
        data = json.loads(response.text)
        quote = data["contents"]["quotes"][0]["quote"]
        return quote
    else:
        return "Sorry, I was unable to get the quote of the day."