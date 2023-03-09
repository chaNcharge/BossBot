#quote_of_the_day
#form They Said So Quotes API
# referance document https://quotes.rest/
import requests
import json

def get_quote_of_the_day():
    response = requests.get("https://quotes.rest/qod")
    data = response.json()
    if response.status_code == 200:
        quote = data["contents"]["quotes"][0]["quote"]
        author = data["contents"]["quotes"][0]["author"]
        print(f"\"{quote}\" - {author}")
    else:
        return "Sorry, I was unable to get the quote of the day."