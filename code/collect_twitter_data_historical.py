import os
import time

from datetime import date
from dotenv import load_dotenv
from time import sleep

from utils import (collect_twitter_data,
                    tic,
                    toc,
                    import_data)


def get_list_users(collection_interupted):

    df = import_data('dataset_1_user_metrics_2022_04_01.csv')
    df = df.sort_values(by = 'follower_count', ascending = False)
    description = ['did not find the account, deleted or suspended']
    df = df[~df['description'].isin(description)]
    print(len(df))

    if collection_interupted == 0:

        list_users = df['username'].tolist()
        print('total nb of users', len(list_users))

    elif collection_interupted == 1 :

        timestr = time.strftime("%Y_%m_%d")
        #timestr = '2022_02_25'
        df_collected = import_data('dataset_2_tweets_' + timestr  + '.csv')

        list1 = df_collected.username.unique().tolist()
        print('Number of users for which the tweets were collected', len(list1))

        list2 = df['username'].dropna().unique()
        list_users = [x for x in list2 if x not in list1]

    return list_users


if __name__=="__main__":

    load_dotenv()

    timestr = time.strftime("%Y_%m_%d")
    list_initial = get_list_users(collection_interupted = 0)

    list_users = list_initial
    list_users_tw =['from:' + user for user in list_users]
    print(len(list_users))
    tic()

    for query in list_users_tw :

        collect_twitter_data(
            list_individuals = list_initial,
            query = query,
            start_time = '2022-01-01T23:00:00Z',
            end_time = '2022-03-01T23:00:00Z',
            bearer_token= os.getenv('TWITTER_TOKEN'),
            filename = os.path.join('.', 'data', 'dataset_2_tweets_' + timestr + '.csv'),
            )
        sleep(3)
    toc()
