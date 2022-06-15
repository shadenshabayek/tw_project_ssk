import csv
import datetime
import glob
import json
import time
import os
import os.path
import pandas as pd
import numpy as np
import requests

from csv import writer
from dotenv import load_dotenv
from time import sleep
from matplotlib import pyplot as plt
from minet import multithreaded_resolve
from ural import get_domain_name
from ural import is_shortened_url


def connect_to_endpoint_historical_search(bearer_token, query, start_time, end_time, next_token=None):
    #max_results: A number between 10 and the system limit (currently 500). By default, a request response will return 10 results.
    #300 requests per 15-minute window (app auth)
    #changelog: max results is now 100!
    max_results=100

    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    params = {"tweet.fields" : "in_reply_to_user_id,author_id,context_annotations,created_at,public_metrics,entities,geo,id,possibly_sensitive,lang,referenced_tweets,conversation_id", "user.fields":"username,name,description,location,created_at,entities,public_metrics","expansions":"author_id,referenced_tweets.id,referenced_tweets.id.author_id,attachments.media_keys"}

    if (next_token is not None):
        url = "https://api.twitter.com/2/tweets/search/all?max_results={}&query={}&start_time={}&end_time={}&next_token={}".format(max_results, query, start_time, end_time, next_token)
    else:
        url = "https://api.twitter.com/2/tweets/search/all?max_results={}&start_time={}&end_time={}&query={}".format(max_results, start_time, end_time, query)

    with requests.request("GET", url, params=params, headers=headers) as response:

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        return response.json()

def write_results(json_response, filename, query, list_individuals):

    #print(json_response['data'])
    with open(filename, "a+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["query",
                                "type_of_tweet",
                                "referenced_tweet_id",
                                "conversation_id",
                                 "id",
                                 "author_id",
                                 "username",
                                 "name",
                                 "created_at",
                                 "text",
                                 "possibly_sensitive",
                                 "retweet_count",
                                 "reply_count",
                                 "like_count",
                                 "quote_count",
                                 "hashtags",
                                 "in_reply_to_user_id",
                                 "in_reply_to_username",
                                 "in_reply_to_username_within_list",
                                 "quoted_user_id",
                                 "quoted_username",
                                 "quoted_username_within_list",
                                 "retweeted_username",
                                 "retweeted_username_within_list",
                                 "mentions_username",
                                 "mentions_username_within_list",
                                 "lang",
                                 "expanded_urls",
                                 "domain_name",
                                 "theme",
                                 "theme_description",
                                 "user_created_at",
                                 "user_profile_description",
                                 "user_location",
                                 #"user_expanded_url",
                                 "followers_count",
                                 "following_count",
                                 "tweet_count",
                                 "listed_count",
                                 "collection_date",
                                 "collection_method"],
                                extrasaction='ignore')

        if 'data' and 'includes' in json_response:

            for tweet in json_response['data']:

                user_index = {}

                for user in json_response['includes']['users']:

                    if 'id' in user.keys():

                        user_index[user['id']] = user

                        if tweet['author_id'] == user['id']:

                            tweet['username'] = user['username']
                            tweet['name'] = user['name']
                            tweet['user_created_at'] = user['created_at']
                            tweet['followers_count'] = user['public_metrics']['followers_count']
                            tweet['following_count'] = user['public_metrics']['following_count']
                            tweet['tweet_count'] = user['public_metrics']['tweet_count']
                            tweet['listed_count'] = user['public_metrics']['listed_count']

                            if 'description' in user.keys():
                                tweet['user_profile_description']= user ['description']

                            if "location" in user.keys():
                                tweet['user_location'] = user['location']

                        if 'in_reply_to_user_id' in tweet.keys():

                            if tweet['in_reply_to_user_id'] == user['id']:

                                a = user['username'].lower()

                                tweet['in_reply_to_username'] = a

                                if a in list_individuals:

                                    tweet["in_reply_to_username_within_list"] = a

                if "context_annotations" in tweet:
                    if "domain" in tweet["context_annotations"][0]:
                        tweet['theme']=tweet["context_annotations"][0]["domain"]["name"]
                        if "description" in tweet["context_annotations"][0]["domain"]:
                            tweet['theme_description']=tweet["context_annotations"][0]["domain"]['description']
                    else:
                        tweet['theme']=''
                        tweet['theme_description']=''

                if "entities" in tweet:

                    if "mentions" in tweet["entities"]:

                        l=len(tweet["entities"]['mentions'])

                        tweet['mentions_username'] = []
                        tweet['mentions_username_within_list'] =[]

                        for i in range(0,l):

                            a = tweet["entities"]['mentions'][i]['username']
                            a = a.lower()
                            tweet['mentions_username'].append(a)

                            if a in list_individuals:
                                tweet['mentions_username_within_list'].append(a)
                    else:
                        tweet['mentions_username'] = []
                        tweet['mentions_username_within_list'] = []

                    if "urls" in tweet["entities"]:

                        lu=len(tweet["entities"]['urls'])

                        tweet['expanded_urls']=[]
                        tweet['domain_name']=[]

                        for i in range(0,lu):

                            link = tweet["entities"]['urls'][i]['expanded_url']
                            #print (i,tweet["entities"]['urls'][i].keys())

                            # if tweet['id'] == "1455491668728328192":
                            #     print(json_response['data'])

                            if len(link) < 30:

                                if 'unwound_url' in tweet["entities"]['urls'][i].keys():
                                    b = tweet["entities"]['urls'][i]['unwound_url']
                                    c = get_domain_name(tweet["entities"]['urls'][i]['unwound_url'])

                                # elif 'unwound_url' not in tweet["entities"]['urls'][i].keys():
                                #     #print('unwound not there!')
                                #     #print(tweet['id'])
                                #     for result in multithreaded_resolve([link]):
                                #         b = result.stack[-1].url
                                #         c = get_domain_name(result.stack[-1].url)

                                # tweet['expanded_urls'].append(b)
                                # tweet['domain_name'].append(c)
                                    tweet['expanded_urls'].append(b)
                                    tweet['domain_name'].append(c)

                                else:
                                    d = tweet["entities"]['urls'][i]['expanded_url']
                                    e = get_domain_name(tweet["entities"]['urls'][i]['expanded_url'])

                                    tweet['expanded_urls'].append(d)
                                    tweet['domain_name'].append(e)


                            else:
                                d = tweet["entities"]['urls'][i]['expanded_url']
                                e = get_domain_name(tweet["entities"]['urls'][i]['expanded_url'])

                                tweet['expanded_urls'].append(d)
                                tweet['domain_name'].append(e)
                    else:
                        tweet['expanded_urls'] = []
                        tweet['domain_name'] = []

                    if "hashtags" in tweet["entities"]:
                        l=len(tweet["entities"]["hashtags"])
                        tweet["hashtags"] = []

                        for i in range(0,l):
                            a = tweet["entities"]["hashtags"][i]["tag"]
                            tweet["hashtags"].append(a)
                    else:
                        tweet["hashtags"] = []
                else:
                    tweet['mentions_username'] = []
                    tweet['mentions_username_within_list'] =[]
                    tweet['hashtags'] = []
                    tweet['expanded_urls'] = []
                    tweet['domain_name'] = []

                if "referenced_tweets" in tweet.keys():

                    tweet["type_of_tweet"] = tweet["referenced_tweets"][0]["type"]
                    tweet["referenced_tweet_id"] = tweet["referenced_tweets"][0]["id"]

                    #if (tweet["referenced_tweets"][0]["type"] == "retweeted" or tweet["referenced_tweets"][0]["type"] == "quoted" or tweet["referenced_tweets"][0]["type"] == "replied_to"):
                    if (tweet["referenced_tweets"][0]["type"] == "retweeted" or tweet["referenced_tweets"][0]["type"] == "quoted"):
                        if "tweets" in json_response["includes"]:

                            for tw in json_response["includes"]["tweets"]:

                                if tweet["referenced_tweets"][0]["id"] == tw["id"] :

                                    tweet['retweet_count'] = tw["public_metrics"]["retweet_count"]
                                    tweet['reply_count'] = tw["public_metrics"]["reply_count"]
                                    tweet['like_count'] = tw["public_metrics"]["like_count"]
                                    if 'quote_count' in tweet["public_metrics"].keys():
                                        tweet['quote_count'] = tw["public_metrics"]["quote_count"]

                                    tweet['possibly_sensitive'] = tw['possibly_sensitive']
                                    tweet['text'] = tw['text']

                                    if tweet['referenced_tweets'][0]['type'] == 'retweeted':

                                        if 'entities' in tweet :

                                            if 'mentions' in tweet['entities'].keys():

                                                if tweet['entities']['mentions'][0]['id'] == tw['author_id'] :

                                                    a = tweet['entities']['mentions'][0]['username']
                                                    b = a.lower()

                                                    tweet['retweeted_username'] = b

                                                    if b in list_individuals:

                                                        tweet['retweeted_username_within_list'] = b

                                    if tweet['referenced_tweets'][0]['type'] == 'quoted':

                                        tweet['quoted_user_id'] = tw['author_id']

                                        if 'entities' in tweet.keys():

                                            if 'urls' in tweet['entities']:

                                                l = len(tweet['entities']['urls'])

                                                for i in range(0,l):

                                                    if 'expanded_url' in tweet['entities']['urls'][i].keys():

                                                        url = tweet['entities']['urls'][i]['expanded_url']

                                                        if tweet['referenced_tweets'][0]['id'] in url:

                                                            #sprint(tweet['entities']['urls'][0]['expanded_url'])
                                                            if 'https://twitter.com/' in url:

                                                                a = url.split('https://twitter.com/')[1]
                                                                b = a.split('/status')[0].lower()

                                                                tweet['quoted_username'] = b

                                                                if b in list_individuals:

                                                                    tweet['quoted_username_within_list'] = b

                                    if 'entities' in  tw.keys():

                                        if "urls" in tw["entities"]:

                                            lu=len(tw["entities"]['urls'])

                                            tweet['expanded_urls']=[]
                                            tweet['domain_name']=[]

                                            for i in range(0,lu):

                                                link = tw["entities"]['urls'][i]['expanded_url']

                                                if len(link) < 30:

                                                    if 'unwound_url' in tw["entities"]['urls'][i].keys():
                                                        b = tw["entities"]['urls'][i]['unwound_url']
                                                        c = get_domain_name(tw["entities"]['urls'][i]['unwound_url'])

                                                    # elif 'unwound_url' not in tw["entities"]['urls'][i].keys():
                                                    #     for result in multithreaded_resolve([link]):
                                                    #         b = result.stack[-1].url
                                                    #         c = get_domain_name(result.stack[-1].url)

                                                    # tweet['expanded_urls'].append(b)
                                                    # tweet['domain_name'].append(c)


                                                        tweet['expanded_urls'].append(b)
                                                        tweet['domain_name'].append(c)

                                                    else:
                                                        d = tw["entities"]['urls'][i]['expanded_url']
                                                        e = get_domain_name(tw["entities"]['urls'][i]['expanded_url'])

                                                        tweet['expanded_urls'].append(d)
                                                        tweet['domain_name'].append(e)

                                                else:
                                                    d = tw["entities"]['urls'][i]['expanded_url']
                                                    e = get_domain_name(tw["entities"]['urls'][i]['expanded_url'])

                                                    tweet['expanded_urls'].append(d)
                                                    tweet['domain_name'].append(e)

                                        else:
                                            tweet['expanded_urls'] = []
                                            tweet['domain_name'] = []

                                        if "hashtags" in tw["entities"]:
                                            l=len(tw["entities"]["hashtags"])
                                            tweet["hashtags"] = []

                                            for i in range(0,l):
                                                a = tw["entities"]["hashtags"][i]["tag"]
                                                tweet["hashtags"].append(a)
                                        else:
                                            tweet["hashtags"] = []

                                        if "mentions" in tw["entities"]:

                                            l=len(tw["entities"]['mentions'])
                                            #tweet['mentions_username'] = []
                                            #tweet['mentions_username_within_list'] =[]

                                            for i in range(0,l):
                                                a = tw["entities"]['mentions'][i]['username']
                                                a = a.lower()
                                                tweet['mentions_username'].append(a)

                                                if a in list_individuals:
                                                    tweet['mentions_username_within_list'].append(a)
                                        # else:
                                        #     tweet['mentions_username'] = []
                                        #     tweet['mentions_username_within_list'] = []

                    # elif (tweet["referenced_tweets"][0]["type"] == "quoted" or tweet["referenced_tweets"][0]["type"] == "replied_to"):
                    #     tweet['retweet_count'] = tweet["public_metrics"]["retweet_count"]
                    #     tweet['reply_count'] = tweet["public_metrics"]["reply_count"]
                    #     tweet['like_count'] = tweet["public_metrics"]["like_count"]
                    elif tweet["referenced_tweets"][0]["type"] == "replied_to" :
                        tweet['retweet_count'] = tweet["public_metrics"]["retweet_count"]
                        tweet['reply_count'] = tweet["public_metrics"]["reply_count"]
                        tweet['like_count'] = tweet["public_metrics"]["like_count"]
                        if 'quote_count' in tweet["public_metrics"].keys():
                            tweet['quote_count'] = tweet["public_metrics"]["quote_count"]


                else:

                    tweet['retweet_count'] = tweet["public_metrics"]["retweet_count"]
                    tweet['reply_count'] = tweet["public_metrics"]["reply_count"]
                    tweet['like_count'] = tweet["public_metrics"]["like_count"]
                    if 'quote_count' in tweet["public_metrics"].keys():
                        tweet['quote_count'] = tweet["public_metrics"]["quote_count"]

                tweet["query"] = query
                tweet["username"] = tweet["username"].lower()


                if len(tweet["mentions_username"]) > 1:
                    tweet["mentions_username"] = list(set(tweet["mentions_username"]))

                if len(tweet["mentions_username_within_list"]) > 1:
                    tweet["mentions_username_within_list"] = list(set(tweet["mentions_username_within_list"]))

                timestr = time.strftime("%Y-%m-%d")
                tweet["collection_date"] = timestr
                tweet["collection_method"] = 'Twitter API V2'

                writer.writerow(tweet)

        else:
            pass

def get_next_token(list_individuals, query, token, count, filename, start_time, end_time, bearer_token):

    json_response = connect_to_endpoint_historical_search(bearer_token, query, start_time, end_time, token)

    result_count = json_response['meta']['result_count']

    if 'next_token' in json_response['meta']:
        sleep(3)
        next_token = json_response['meta']['next_token']
        if result_count is not None and result_count > 0:

            count += result_count
            print(count)
        #try:
        write_results(json_response, filename, query, list_individuals)
        return next_token, count
    else:
        write_results(json_response, filename, query, list_individuals)
        return None, count

def collect_twitter_data(list_individuals, query, start_time, end_time, bearer_token, filename):

    print(query)

    flag = True
    count = 0
    file_exists = os.path.isfile(filename)

    with open(filename, "a+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["query",
                                "type_of_tweet",
                                "referenced_tweet_id",
                                "conversation_id",
                                 "id",
                                 "author_id",
                                 "username",
                                 "name",
                                 "created_at",
                                 "text",
                                 "possibly_sensitive",
                                 "retweet_count",
                                 "reply_count",
                                 "like_count",
                                 "quote_count",
                                 "hashtags",
                                 "in_reply_to_user_id",
                                 "in_reply_to_username",
                                 "in_reply_to_username_within_list",
                                 "quoted_user_id",
                                 'quoted_username',
                                 'quoted_username_within_list',
                                 "retweeted_username",
                                 "retweeted_username_within_list",
                                 "mentions_username",
                                 "mentions_username_within_list",
                                 "lang",
                                 "expanded_urls",
                                 "domain_name",
                                 "theme",
                                 "theme_description",
                                 "user_created_at",
                                 "user_profile_description",
                                 "user_location",
                                 #"user_expanded_url",
                                 "followers_count",
                                 "following_count",
                                 "tweet_count",
                                 "listed_count",
                                 "collection_date",
                                 "collection_method"], extrasaction='ignore')
        if not file_exists:
            writer.writeheader()

    next_token = None

    while flag:
        next_token, count = get_next_token(list_individuals, query, next_token, count, filename, start_time, end_time, bearer_token)
        if count >= 2000000:
            break
        if next_token is None:
            flag = False


    print("Total Tweet IDs saved: {}".format(count))

""" General functions to save data and import it """

def TicTocGenerator():
    ti = 0
    tf = time.time()
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti

TicToc = TicTocGenerator()

def toc(tempBool=True):
    tempTimeInterval = next(TicToc)
    if tempBool:
        print( "Elapsed time: %f seconds.\n" %tempTimeInterval )

def tic():
    toc(False)

def import_data(file_name):

    data_path = os.path.join(".", "data", file_name)
    df = pd.read_csv(data_path, low_memory=False)
    return df

def save_figure(figure_name):

    figure_path = os.path.join('.', 'figure', figure_name)
    plt.savefig(figure_path, bbox_inches='tight')
    print("The '{}' figure is saved.".format(figure_name))

def save_data(df, file_name, append):

    file_path = os.path.join('.', 'data', file_name)

    if append == 1:
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    print(" '{}' is saved.".format(file_name))


""" Get users metrics from Twitter API """

def create_url(handle):

    user_fields = "user.fields=created_at,description,id,location,name,pinned_tweet_id,protected,public_metrics,url,username,verified"

    url = "https://api.twitter.com/2/users/by/username/{}?{}".format(handle, user_fields)

    return url

def create_headers(bearer_token):

    bearer_token = bearer_token
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    return headers

def connect_to_endpoint_user_metrics(url, headers):

    response = requests.request("GET", url, headers = headers)

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def write_results_user_metrics(json_response, filename, user):

    with open(filename, "a+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["username",
                                "follower_count",
                                "following_count",
                                "tweet_count",
                                "protected",
                                "url",
                                "name",
                                "id",
                                "location",
                                "created_at",
                                "description",
                                "collection_date",
                                "collection_method"], extrasaction='ignore')

        if "data"  in json_response:

            tweet = json_response["data"]
            tweet['follower_count'] = tweet['public_metrics']["followers_count"]
            tweet['following_count'] = tweet['public_metrics']["following_count"]
            tweet['tweet_count'] = tweet['public_metrics']["tweet_count"]

            timestr = time.strftime("%Y-%m-%d")
            tweet["collection_date"] = timestr
            tweet["collection_method"] = "Twitter API V2"
            tweet["username"] = tweet["username"].lower()
            writer.writerow(tweet)

        else:
            pass
            tweet = {}
            tweet['username'] = user
            tweet['description'] = 'did not find the account, deleted or suspended'
            writer.writerow(tweet)
            print('did not find the account')

def get_user_metrics(bearer_token, list, filename):

    file_exists = os.path.isfile(filename)

    with open(filename, "a") as tweet_file:
        writer = csv.DictWriter(tweet_file,
                                ["username",
                                "follower_count",
                                "following_count",
                                "tweet_count",
                                "protected",
                                "url",
                                "name",
                                "id",
                                "location",
                                "created_at",
                                "description",
                                "collection_date",
                                "collection_method"], extrasaction='ignore')
        if not file_exists:

            writer.writeheader()

    ln=len(list)
    for user in list:
        print(user)
        url = create_url(user)
        headers = create_headers(bearer_token)
        json_response = connect_to_endpoint_user_metrics(url, headers)
        write_results_user_metrics(json_response, filename, user)
        sleep(3)


"""Get following users of a user """

def connect_to_endpoint_following_users(bearer_token, author_id, next_token=None):
    #rate limit 75 calls per 15min window.
    #order of likes: most recent
    max_results = 1000

    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    params = {"user.fields":"username,name,description,location,created_at,entities,public_metrics"}

    if (next_token is not None):
        url = "https://api.twitter.com/2/users/{}/following?max_results={}&pagination_token={}".format(author_id, max_results, next_token)
    else:
        url = "https://api.twitter.com/2/users/{}/following?max_results={}".format(author_id, max_results)

    with requests.request("GET", url, params=params, headers=headers) as response:

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        return response.json()

def write_results_following_users(json_response, filename, author_id, author_name, author_following_count, list_individuals):

    with open(filename, "a+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["author_id",
                                "source_username",
                                "source_following_count",
                                "following_username",
                                "following_within_list",
                                "id",
                                "name",
                                "location",
                                "following_count",
                                "followers_count",
                                "tweet_count",
                                "created_at",
                                "collection_date",
                                "collection_method"], extrasaction='ignore')

        if 'data' in json_response:

            for tweet in json_response['data']:

                if 'public_metrics' in tweet.keys():

                    tweet['followers_count'] = tweet['public_metrics']["followers_count"]
                    tweet['following_count'] = tweet['public_metrics']["following_count"]
                    tweet['tweet_count'] = tweet['public_metrics']["tweet_count"]

                tweet['following_username'] = tweet['username'].lower()

                a = tweet['username'].lower()
                if a in list_individuals :
                    tweet['following_within_list'] = a

                timestr = time.strftime("%Y-%m-%d")
                tweet["collection_date"] = timestr
                tweet["collection_method"] = "Twitter API V2"
                tweet["author_id"] = author_id
                tweet['source_username'] = author_name
                tweet['source_following_count'] = author_following_count

                writer.writerow(tweet)

        else:
            pass

def get_next_token_following(list_individuals, author_id, author_name, author_following_count, token, count, filename, bearer_token):

    json_response = connect_to_endpoint_following_users(bearer_token, author_id, token)

    if 'meta' in json_response:
        result_count = json_response['meta']['result_count']

        if 'next_token' in json_response['meta']:

            sleep(62)
            next_token = json_response['meta']['next_token']

            #print(next_token)
            if result_count is not None and result_count > 0:

                count += result_count
                print(count)
            #try:
            write_results_following_users(json_response, filename, author_id, author_name, author_following_count, list_individuals)
            return next_token, count
        else:
            write_results_following_users(json_response, filename, author_id, author_name, author_following_count, list_individuals)
            return None, count

    elif 'errors' in json_response:
        print(json_response['errors'][0]['title'])
        print(author_id, author_name, 'check this individual')
        pass

def collect_following_data(list_individuals, author_id, author_name, author_following_count, bearer_token, filename):
    print(author_id)

    flag = True
    count = 0
    file_exists = os.path.isfile(filename)

    with open(filename, "a+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["author_id",
                                "source_username",
                                "source_following_count",
                                "following_username",
                                "following_within_list",
                                "id",
                                "name",
                                "location",
                                "following_count",
                                "followers_count",
                                "tweet_count",
                                "created_at",
                                "collection_date",
                                "collection_method"], extrasaction='ignore')
        if not file_exists:
            writer.writeheader()

    next_token = None

    while flag:
        next_token, count = get_next_token_following(list_individuals, author_id, author_name, author_following_count, next_token, count, filename, bearer_token)
        if count >= 100000:
            break
        if next_token is None:
            flag = False


    print("Total following users saved: {}".format(count))

"""Get liking users of a tweet """

def connect_to_endpoint_liking_users(bearer_token, tweet_id, next_token=None):
    #rate limit 75 calls per 15min window.
    #order of likes: most recent
    max_results = 100

    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    params = {"tweet.fields" : "context_annotations,created_at,public_metrics,entities,geo,id,possibly_sensitive,lang,referenced_tweets",
              "user.fields":"username,name,description,location,created_at,entities,public_metrics"}

    if (next_token is not None):
        url = "https://api.twitter.com/2/tweets/{}/liking_users?max_results={}&pagination_token={}".format(tweet_id, max_results, next_token)
    else:
        url = "https://api.twitter.com/2/tweets/{}/liking_users?max_results={}".format(tweet_id, max_results)

    with requests.request("GET", url, params=params, headers=headers) as response:

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        return response.json()

def connect_to_endpoint_liked_tweets(bearer_token, user_id, next_token=None):
    #rate limit 75 calls per 15min window.
    #order of likes: most recent
    max_results = 100

    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    params = {"tweet.fields" : "created_at,author_id",
              "user.fields":"created_at,id,name,username,public_metrics",
              "expansions": "author_id"}

    if (next_token is not None):
        url = "https://api.twitter.com/2/users/{}/liked_tweets?max_results={}&pagination_token={}".format(user_id, max_results, next_token)
    else:
        url = "https://api.twitter.com/2/users/{}/liked_tweets?max_results={}".format(user_id, max_results)

    with requests.request("GET", url, params=params, headers=headers) as response:

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

def write_results_liked_tweets(json_response, filename, author_id, author_name, list_individuals):

    with open(filename, "a+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["source_username_id",
                                "source_username",
                                "tweet_created_at",
                                "id",
                                "text",
                                "liked_tweet_author_id",
                                "liked_tweet_author_name",
                                "liked_tweet_author_username",
                                "liked_tweet_author_username_within_list",
                                "liked_tweet_author_created_at",
                                "liked_tweet_author_following_count",
                                "liked_tweet_author_followers_count",
                                "liked_tweet_author_tweet_count",
                                "collection_date",
                                "collection_method"], extrasaction='ignore')

        if 'data' and 'includes' in json_response:

            for tweet in json_response['data']:

                if 'public_metrics' in tweet.keys():

                    tweet['followers_count'] = tweet['public_metrics']["followers_count"]
                    tweet['following_count'] = tweet['public_metrics']["following_count"]
                    tweet['tweet_count'] = tweet['public_metrics']["tweet_count"]

                tweet['tweet_created_at'] = tweet['created_at']
                tweet["liked_tweet_author_id"] = tweet['author_id']

                if 'users' in json_response['includes']:
                    for user in json_response['includes']['users']:

                        if tweet["liked_tweet_author_id"] == user['id']:
                            tweet['liked_tweet_author_username'] = user['username'].lower()
                            tweet["liked_tweet_author_name"] = user['name'].lower()
                            tweet["liked_tweet_author_created_at"] = user['created_at']

                            if 'public_metrics' in user.keys():

                                tweet['liked_tweet_author_followers_count'] = user['public_metrics']["followers_count"]
                                tweet['liked_tweet_author_following_count'] = user['public_metrics']["following_count"]
                                tweet['liked_tweet_author_tweet_count'] = user['public_metrics']["tweet_count"]


                a = tweet['liked_tweet_author_username'].lower()

                if a in list_individuals :
                    tweet['liked_tweet_author_username_within_list'] = a

                timestr = time.strftime("%Y-%m-%d")

                tweet["collection_date"] = timestr
                tweet["collection_method"] = "Twitter API V2"
                tweet["source_username_id"] = author_id
                tweet['source_username'] = author_name

                writer.writerow(tweet)

        else:
            pass

def get_next_token_liked_tweets(list_individuals, author_id, author_name, token, count, filename, bearer_token):

    json_response = connect_to_endpoint_liked_tweets(bearer_token, author_id, token)
    #print(json_response)
    #print(json_response.keys())
    if 'meta' in json_response:
        result_count = json_response['meta']['result_count']

        if 'next_token' in json_response['meta']:

            #sleep(62)
            next_token = json_response['meta']['next_token']

            #print(next_token)
            if result_count is not None and result_count > 0:

                count += result_count
                print(count)
            #try:
            write_results_liked_tweets(json_response, filename, author_id, author_name, list_individuals)
            return next_token, count
        else:
            write_results_liked_tweets(json_response, filename, author_id, author_name, list_individuals)
            return None, count

    elif 'errors' in json_response:
        print(json_response['errors'][0]['title'])
        print(author_id, author_name, 'check this individual')
        pass

def collect_liked_tweets_data(list_individuals, author_id, author_name, bearer_token, filename):
    print(author_id)

    flag = True
    count = 0
    file_exists = os.path.isfile(filename)

    with open(filename, "a+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["source_username_id",
                                "source_username",
                                "tweet_created_at",
                                "id",
                                "text",
                                "liked_tweet_author_id",
                                "liked_tweet_author_name",
                                "liked_tweet_author_username",
                                "liked_tweet_author_username_within_list",
                                "liked_tweet_author_created_at",
                                "following_count",
                                "followers_count",
                                "tweet_count",
                                "collection_date",
                                "collection_method"], extrasaction='ignore')
        if not file_exists:
            writer.writeheader()

    next_token = None

    while flag:
        next_token, count = get_next_token_liked_tweets(list_individuals, author_id, author_name, next_token, count, filename, bearer_token)
        if count > 190:
            break
        if next_token is None:
            flag = False


    print("Total liked tweets saved: {}".format(count))
