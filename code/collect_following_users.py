import os
import time
import pandas as pd
pd.set_option('display.float_format', lambda x: '%.0f' % x)

from datetime import date
from dotenv import load_dotenv
from time import sleep

from utils import (collect_following_data,
                    tic,
                    toc,
                    import_data)


def get_list_users_id(collection_interupted):

    df = import_data('dataset_1_user_metrics_2022_03_11.csv')
    df = df.sort_values(by = 'follower_count', ascending = False)
    #print(df.head(10))
    description = ['did not find the account, deleted or suspended']
    df = df[~df['description'].isin(description)]
    df['id'] = df['id'].astype('int64')
    df['following_count'] = df['following_count'].astype('int64')
    print(len(df))

    if collection_interupted == 0:

        list_users = df['username'].tolist()
        list_users_id = df['id'].tolist()
        list_following = df['following_count'].tolist()

    #list_users = list_users[0:2]
    #list_users = ['lcp', 'senat']
        print('total nb of users', len(list_users))

    # elif collection_interupted == 1 :
    #
    #     timestr = time.strftime("%Y_%m_%d")
    #     #timestr = '2022_02_25'
    #     df_collected = import_data('dataset_2_tweets_' + timestr  + '.csv')
    #
    #     list1 = df_collected.username.unique().tolist()
    #     print(len(list1))
    #
    #     list2 = df['username'].dropna().unique()
    #
    #     list_users = [x for x in list2 if x not in list1]

    return list_users, list_users_id, list_following

if __name__=="__main__":

  load_dotenv()
  timestr = time.strftime("%Y_%m_%d")
  list_users, list_users_id, list_following = get_list_users_id(collection_interupted = 0 )

  tic()
  for i in range(0, 3):

      collect_following_data(list_individuals = list_users ,
                             author_id = list_users_id[i],
                             author_name = list_users[i],
                             author_following_count = list_following[i],
                             bearer_token = os.getenv('TWITTER_TOKEN'),
                             filename = os.path.join('.', 'data', 'dataset_3_test_' + timestr + '.csv'))

      sleep(2)
  toc()
