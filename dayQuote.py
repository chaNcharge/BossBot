#quote_of_the_day
#form They Said So Quotes API
# referance document https://quotes.rest/
import requestsgit 

def get_quote_of_the_day():
    try:
        response = requests.get("https://quotes.rest/qod")
        response.raise_for_status()  # raise an exception if the response status code is not 200
        data = response.json()
        quote = data["contents"]["quotes"][0]["quote"]
        author = data["contents"]["quotes"][0]["author"]
        return f"\"{quote}\" - {author}"
    except (requests.exceptions.RequestException, IndexError, KeyError) as err:
        return f"Sorry, I was unable to get the quote of the day. Error: {str(err)}"