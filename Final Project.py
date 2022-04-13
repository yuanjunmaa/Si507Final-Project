import tweepy
import re
from typing import Tuple
import yelpapi
import requests
import json
from binarytree import build
from bs4 import BeautifulSoup
from enum import auto
import plotly.graph_objects as go
from flask import Flask, render_template, request

key = "gjpSPukYc4JSNUgRSVUlQmKyG"
secret = "mPuSIGXKkgEOTpwtSssSjweH6DcvSOix064vjztqv3flu593PB"
auth = tweepy.OAuthHandler(key,secret)
api = tweepy.API(auth)

CACHE_FILENAME = ''
CACHE_DICT = {}

def open_cache():
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()
def construct_unique_key(baseurl, params):
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key

def make_request(baseurl, params, headers):
    response = requests.get(baseurl, params=params, headers=headers)
    return response.json()

def make_request_with_cache(baseurl, params, headers):
    request_key = construct_unique_key(baseurl, params)
    if request_key in CACHE_DICT.keys():
        print("\ncache hit!", request_key)
        return CACHE_DICT[request_key]
    else:
        print("\ncache miss!", request_key)
        CACHE_DICT[request_key] = make_request(baseurl, params, headers)
        save_cache(CACHE_DICT)
        return CACHE_DICT[request_key]

bar_data = go.Bar(x=name, y=rating)
basic_layout = go.Layout(title=f"Restaurant rating in {location}")
fig = go.Figure(data=bar_data, layout=basic_layout)

scatter_data = go.Scatter(
                x=rating, 
                y=price,
                text=name, 
                marker={'symbol':'square', 'size':30, 'color': 'green'},
                mode='markers+text')
fig.show()


