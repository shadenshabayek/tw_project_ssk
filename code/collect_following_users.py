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


def get_list_users_id():

    #df = import_data('dataset_1_user_metrics_2022_03_11.csv')
    data_path = './data/dataset_1_user_metrics_2022_03_18.csv'
    df = pd.read_csv(data_path, dtype='str') #important sinon conversion float64 to int64 of ID changes last digit
    description = ['did not find the account, deleted or suspended']
    df = df[~df['description'].isin(description)]

    df['follower_count'] = df['follower_count'].astype('int64')
    df['id'] = df['id'].astype('int64')
    df['following_count'] = df['following_count'].astype('int64')

    df = df.sort_values(by = 'follower_count', ascending = False)
    df = df[~df['protected'].isin(['True'])]

    list_users = df['username'].tolist()
    list_users_id = df['id'].tolist()
    list_following = df['following_count'].tolist()
    print('total nb of users', len(list_users))

    return list_users, list_users_id, list_following

if __name__=="__main__":

  load_dotenv()
  #timestr = time.strftime("%Y_%m_%d")
  timestr = '2022_03_23'
  list_users, list_users_id, list_following = get_list_users_id()

  print(list_following[2036:2100])
  print('total calls', round(sum(list_following[2036:2100])/1000))
  print(list_users[2036:2100])
  print(list_users_id[2036:2100])

  tic()
  for i in range(2036,2100):

      collect_following_data(list_individuals = list_users ,
                             author_id = list_users_id[i],
                             author_name = list_users[i],
                             author_following_count = list_following[i],
                             bearer_token = os.getenv('TWITTER_TOKEN'),
                             filename = os.path.join('.', 'data', 'dataset_3_following_' + timestr + '.csv'))

      sleep(62)
  toc()
