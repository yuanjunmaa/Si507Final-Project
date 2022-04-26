import yelpapi
import requests
import json
from binarytree import build
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from flask import Flask, render_template, request
import re
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import statistics
from plotly.subplots import make_subplots
analyzer = SentimentIntensityAnalyzer()

CACHE_FILENAME = "yelp_cache.json"
CACHE_DICT = {}
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAKUUZAEAAAAAzbHtvsSLym6DurL2MrdQ3G93SOo%3Dn8efk2Nc7YTVIV1whRFMQ5UonduOQCAwBUJqnp737rLaQm9sAI"
tweet_fields = "tweet.fields=text,author_id,created_at"

def open_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key

def make_request(baseurl, params, headers):
    '''Make a request to the Web API using the baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    headers:

    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    response = requests.get(baseurl, params=params, headers=headers)
    return response.json()

def make_request_with_cache(baseurl, params, headers):
    '''Check the cache for a saved result for this baseurl+params
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    headers: 

    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    request_key = construct_unique_key(baseurl, params)
    if request_key in CACHE_DICT.keys():
        print("\ncache hit!", request_key)
        return CACHE_DICT[request_key]
    else:
        print("\ncache miss!", request_key)
        CACHE_DICT[request_key] = make_request(baseurl, params, headers)
        save_cache(CACHE_DICT)
        return CACHE_DICT[request_key]


def search_twitter(query, tweet_fields, bearer_token = BEARER_TOKEN):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}".format(
        query, tweet_fields
    )
    response = requests.request("GET", url, headers=headers)

    print(response.status_code)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()




#create Flask

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('results.html',
        tweet=tweet_score, flask_data=flask_data, term=term, location=location)



if __name__ == "__main__":
    key = "feygYqaz20gOBu8hGKg3ZuWVF"
    secret = "K9d22bsGVCwIdQqOrTAAMl8qMV3Gk4MxtYmOxtF8waPZXWUWJd"
    auth = tweepy.OAuthHandler(key,secret)
    api = tweepy.API(auth)
    client_id = 'WWFNQJ_dl1_Lg0u6zf8GLQ'
    api_key = 'LCBo2cRgiuQbrco8gpAyfUX9eAUh2rBq8kiVTAC9Ee7dMbtdigV7TImIoDc-PJ6JDe-Wuqtv5feIY-4Y6OY7h-HjIIxwLm12UCYGSF907miXmVb47a4u2xgk7cFmYnYx'
    headers = {'Authorization': 'Bearer %s' % api_key}
    base_url = 'https://api.yelp.com/v3/businesses/search'
    location = input("which city do you want to eat? or 'exit' to quit: ")
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAKUUZAEAAAAAzbHtvsSLym6DurL2MrdQ3G93SOo%3Dn8efk2Nc7YTVIV1whRFMQ5UonduOQCAwBUJqnp737rLaQm9sAI"
    tweet_fields = "tweet.fields=text,author_id,created_at"
    # Interaction interface
    if location == 'exit':
        print("\nBye!")
    else:
        term = input("what kind of food you want to eat? or 'exit' to quit: ")
        if term == 'exit':
            print("\nBye!")



    while True:
        if location == "exit" or term == "exit": 
            break
        else: 
            params = {"location": location, "term": term}
            CACHE_DICT = open_cache()
            results = make_request_with_cache(base_url, params, headers)
            businesses = results["businesses"]
            nodes = []
            names = []
            rating = []
            address = []
            phone_num = []
            flask_data = []
            price = []
            review_score = []
            tweet_score = []
            for business in businesses:
                flask_tem = []
                query = business["name"]
                query = re.sub(r'[^\w\s]','',query)
                tweet_search = api.search_30_day(label = 'pro', query = query, tag = 'restaurant')
                names.append(business["name"])
                rating.append(business["rating"])
                address.append(" ".join(business["location"]["display_address"]))
                phone_num.append(business["phone"])
                tweet_score.append(len(tweet_search))
                print(business["name"])
                if "price" in business:
                    price.append(len(business["price"]))
                else:
                    price.append('none')
                flask_tem.append(business["name"])
                flask_tem.append(business["rating"])
                flask_tem.append(" ".join(business["location"]["display_address"]))
                flask_tem.append(business["phone"])
                flask_tem.append(len(tweet_search))
                flask_data.append(flask_tem)
                nodes.append(business["rating"])
                id = business["id"]
                url="https://api.yelp.com/v3/businesses/" + id + "/reviews"
                response = requests.get(url, headers=headers)
                result = response.json()
                reviews = result["reviews"]
                print("--- Reviews ---")
                score = []
                for review in reviews:
                    print("User:", review["user"]["name"], "Rating:", review["rating"], "Review:", review["text"], "\n")
                    score.append(analyzer.polarity_scores(review)["compound"])
                review_score.append(statistics.mean(score))

            # First Bar Chart 
            bar_data = go.Bar(x=names, y=tweet_score)
            basic_layout = go.Layout(title=f"Mention of Restaurant from Tweet in {location}")
            fig = go.Figure(data=bar_data, layout=basic_layout)


            fig.show()
            fig.write_html("bar.html", auto_open = True)

            # Second Bar chart

            high_pri_name = []
            high_pri_rat = []
            low_pri_name = []
            low_pri_rat = []

            for pri in range(len(price)):
                if price[pri] == 2:
                    high_pri_name.append(names[pri])
                    high_pri_rat.append(rating[pri])
                elif price[pri] == 1:
                    low_pri_name.append(names[pri])
                    low_pri_rat.append(rating[pri])
            fig2 = make_subplots( rows=1, cols=2, subplot_titles=("High Price", "Low Price"))
            scatter_high = go.Bar(
                x=high_pri_name, 
                y=high_pri_rat,)
             
            scatter_low = go.Bar(
                x=low_pri_name, 
                y=low_pri_rat,)

            fig2.add_trace(scatter_high, row =1, col=1)
            fig2.add_trace(scatter_low, row = 1, col = 2)
            fig2.update_layout(title_text=f"Rating and Price of restaurant in {location}",showlegend=False)


            fig2.show()
            fig2.write_html("bar2.html", auto_open=True)

            # Build the binary tree
            binary_tree = build(nodes)
            print('Binary tree from list :\n',
                binary_tree)

            print('\nList from binary tree :',
                binary_tree.values)

            # create flask
            app.run(debug=False)

        # Interaction interface
        while True: 
            user_input = input("Would you like to have another search term? then 'yes' or exit:")
            if user_input == "exit":
                location = "exit"
                print("\nBye!")
                break
            else: 
                location = input("which city do you want to eat? or 'exit' to quit: ")
                if location == 'exit':
                    print("\nBye!")
                else:
                    term = input("what kind of food you want to eat? or 'exit' to quit: ")
                    if term == 'exit':
                        print("\nBye!")

                params = {"location": location, "term": term}
                CACHE_DICT = open_cache()
                results = make_request_with_cache(base_url, params, headers)
                businesses = results["businesses"]
                nodes = []
                names = []
                rating = []
                address = []
                phone_num = []
                flask_data = []
                price = []
                review_score = []
                tweet_score = []
                for business in businesses:
                    flask_tem = []
                    query = business["name"]
                    query = re.sub(r'[^\w\s]','',query)
                    tweet_search = api.search_30_day(label = 'pro', query = query, tag = 'restaurant')
                    names.append(business["name"])
                    rating.append(business["rating"])
                    address.append(" ".join(business["location"]["display_address"]))
                    phone_num.append(business["phone"])
                    tweet_score.append(len(tweet_search))
                    if "price" in business:
                        price.append(len(business["price"]))
                    else:
                        price.append('none')
                    flask_tem.append(business["name"])
                    flask_tem.append(business["rating"])
                    flask_tem.append(" ".join(business["location"]["display_address"]))
                    flask_tem.append(business["phone"])
                    flask_tem.append(len(tweet_search))
                    flask_data.append(flask_tem)
                    nodes.append(business["rating"])
                    id = business["id"]
                    url="https://api.yelp.com/v3/businesses/" + id + "/reviews"
                    response = requests.get(url, headers=headers)
                    result = response.json()
                    reviews = result["reviews"]
                    print("--- Reviews ---")
                    for review in reviews:
                        print("User:", review["user"]["name"], "Rating:", review["rating"], "Review:", review["text"], "\n")

                bar_data = go.Bar(x=names, y=tweet_score)
                basic_layout = go.Layout(title=f"Mention of Restaurant from Tweet in {location}")
                fig = go.Figure(data=bar_data, layout=basic_layout)

                fig.show()
                fig.write_html("bar.html", auto_open = True)
                high_pri_name = []
                high_pri_rat = []
                low_pri_name = []
                low_pri_rat = []

                for pri in range(len(price)):
                    if price[pri] == 2:
                        high_pri_name.append(names[pri])
                        high_pri_rat.append(rating[pri])
                    elif price[pri] == 1:
                        low_pri_name.append(names[pri])
                        low_pri_rat.append(rating[pri])
                fig2 = make_subplots( rows=1, cols=2, subplot_titles=("High Price", "Low Price"))
                scatter_high = go.Bar(
                x=high_pri_name, 
                y=high_pri_rat,)
                scatter_low = go.Bar(
                x=low_pri_name, 
                y=low_pri_rat,)
                fig2.add_trace(scatter_high, row =1, col=1)
                fig2.add_trace(scatter_low, row = 1, col = 2)
                fig2.update_layout(title_text=f"Rating and Price of restaurant in {location}",showlegend=False)
                fig2.show()
                fig2.write_html("bar2.html", auto_open=True)


                # Build the binary tree
                binary_tree = build(nodes)
                print('Binary tree from list :\n',
                    binary_tree)


                print('\nList from binary tree :',
                    binary_tree.values)

                # create flask
                app.run(debug=False)
