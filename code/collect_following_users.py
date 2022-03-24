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

    #df = import_data('dataset_1_user_metrics_2022_03_11.csv')
    data_path = './data/dataset_1_user_metrics_2022_03_18.csv'
    df = pd.read_csv(data_path, dtype='str') #important sinon conversion float64 to int64 of ID changes last digit
    description = ['did not find the account, deleted or suspended']
    df = df[~df['description'].isin(description)]

    df['follower_count'] = df['follower_count'].astype('int64')
    df['id'] = df['id'].astype('int64')
    df['following_count'] = df['following_count'].astype('int64')

    df = df.sort_values(by = 'follower_count', ascending = False)
    print(len(df))

    list_users = df['username'].tolist()

    if collection_interupted == 0:

        list_users_id = df['id'].tolist()
        list_following = df['following_count'].tolist()

        print('total nb of users', len(list_users))

    # elif collection_interupted == 1 :
    #
    #     #timestr = time.strftime("%Y_%m_%d")
    #     timestr = '2022_03_19'
    #     df_collected = import_data('dataset_3_following_' + timestr  + '.csv')
    #
    #     list1 = df_collected.source_username.unique().tolist()
    #     print(len(list1))
    #
    #     list2 = df['username'].tolist()
    #     list_users_updated = [x for x in list2 if x not in list1]
    #
    #     list1_id =df_collected.author_id.unique().tolist()
    #     list_users_id = df['id'].tolist()
    #
    #     list_users__id_updated = [x for x in list2 if x not in list1_id]
    #
    return list_users, list_users_id, list_following

if __name__=="__main__":

  load_dotenv()
  #timestr = time.strftime("%Y_%m_%d")
  timestr = '2022_03_23'
  list_users, list_users_id, list_following = get_list_users_id(collection_interupted = 0 )


  # print(list_following[176:200])
  # print(list_users[176:200])
  # print(list_users_id[176:200])
  #for i in range(177,250):

  print(list_following[180:250])
  print(list_users[180:250])
  print(list_users_id[180:250])

  tic()
  for i in range(181,250):

      collect_following_data(list_individuals = list_users ,
                             author_id = list_users_id[i],
                             author_name = list_users[i],
                             author_following_count = list_following[i],
                             bearer_token = os.getenv('TWITTER_TOKEN'),
                             filename = os.path.join('.', 'data', 'dataset_3_following_' + timestr + '.csv'))

      sleep(90)
  toc()
