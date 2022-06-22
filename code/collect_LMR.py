import os
import time

from datetime import date
from dotenv import load_dotenv
from time import sleep

from utils import (collect_twitter_data,
                    tic,
                    toc,
                    import_data,
                    get_user_metrics)

def get_list_users(filename):

    df = import_data(filename)
    df = df[df['total'].notna()]
    df = df.drop_duplicates(subset=['total'])
    df = df.rename(columns={'total': 'username'})

    df['username'] = df['username'].replace({'https://twitter com/francklefvre': 'francklefvre'}, regex=True)
    df['username'] = df['username'].replace({'https://twitter com/emercier4': 'emercier4'}, regex=True)

    list_reg = df[df['election2'].isin(['regionale 2015'])]['username']
    print('reg', len(list_reg))

    list_leg = df[df['election2'].isin(['legislative 2012'])]['username']
    print('leg', len(list_leg))

    list_mun = df[df['election2'].isin(['municipale 2014'])]['username']
    print('mun', len(list_mun))

    return list_reg, list_leg, list_mun

def clean_list(filename):

    df = import_data(filename)
    df = df.sort_values(by = 'follower_count', ascending = False)
    description = ['did not find the account, deleted or suspended']
    df = df[~df['description'].isin(description)]
    df['protected'] = df['protected'].astype(str)
    df = df[~df['protected'].isin(['True'])]
    print('number of users, after removing inexistant/suspended/protected accounts', len(df))

    if collection_interupted == 0:

        list_users = df['username'].tolist()
        print('total nb of users', len(list_users))

    elif collection_interupted == 1 :

        #timestr = time.strftime("%Y_%m_%d")
        timestr = '2022_06_15'
        df_collected = import_data('dataset_2_tweets_new_list_' + timestr  + '.csv')

        list1 = df_collected.username.unique().tolist()
        print('Number of users for which the tweets were collected', len(list1))

        list2 = df['username'].dropna().unique()
        list_users = [x for x in list2 if x not in list1]

    return list_users

def collect_tweets(start, end):

    load_dotenv()

    #timestr = time.strftime("%Y_%m_%d")
    timestr = '2022_06_22'
    filename = 'selection_LMR.py'
    collection_interupted = 0
    list_initial = get_list_users(collection_interupted = collection_interupted,
                                  filename = filename)

    list_users = list_initial
    list_users_tw =['from:' + user for user in list_users]
    print(len(list_users))
    tic()
    for query in list_users_tw :

        collect_twitter_data(
            list_individuals = list_initial,
            query = query,
            start_time = start,
            end_time = end,
            bearer_token= os.getenv('TWITTER_TOKEN'),
            filename = os.path.join('.', 'data', 'hist', level, 'dataset_2_tweets_LMR_' + timestr + '.csv'),
            )
        sleep(3)
    toc()

def collect_users_metrics(filename, level):

    list_reg, list_leg, list_mun = get_list_users(filename)
    timestr = time.strftime("%Y_%m_%d")
    #timestr = '2022_06_12'

    load_dotenv()
    if level == 'reg':
        list_users = list_reg
        tic()
        get_user_metrics(bearer_token = os.getenv('TWITTER_TOKEN'),
                    list = list_users,
                    filename = os.path.join('.',
                                            'data',
                                            'hist',
                                            level,
                                            'dataset_1_user_metrics_{}_'.format(level) + timestr  + '.csv'))
        toc()

    elif level == 'leg':
        list_users = list_leg
        tic()
        get_user_metrics(bearer_token = os.getenv('TWITTER_TOKEN'),
                    list = list_users,
                    filename = os.path.join('.',
                                            'data',
                                            'hist',
                                            level,
                                            'dataset_1_user_metrics_{}_'.format(level) + timestr  + '.csv'))
        toc()

    elif level == 'mun':
        list_users = list_mun
        print(len(list_mun))
        tic()
        get_user_metrics(bearer_token = os.getenv('TWITTER_TOKEN'),
                    list = list_users,
                    filename = os.path.join('.',
                                            'data',
                                            'hist',
                                            level,
                                            'dataset_1_user_metrics_{}_'.format(level) + timestr  + '.csv'))
        toc()

def main():

    #collect_users_metrics(filename = 'selection_LMR.csv', level = 'mun')
    collect_users_metrics(filename = 'selection_LMR.csv', level = 'leg')
    collect_users_metrics(filename = 'selection_LMR.csv', level = 'reg')

if __name__=="__main__":

    main()
