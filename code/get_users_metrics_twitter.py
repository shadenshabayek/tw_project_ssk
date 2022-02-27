import numpy as np
import os
import time


from datetime import date
from dotenv import load_dotenv
from time import sleep

from utils import (get_user_metrics,
                    tic,
                    toc,
                    import_data)



def get_users_list(updated_list):

    df = import_data('match_twitter_theo_2022_02_23.csv')

    df = df.rename(columns={'nom_prenom_std3': 'name', 'total': 'username'})
    df['username'] = df['username'].str.lower()
    df = df.drop_duplicates(subset=['name'], keep='first')
    df['username'] = df['username'].replace({'https://twitter com/jjgiannesini': 'jjgiannesini'}, regex=True)
    print('There are', len(df['username'].dropna().unique()), 'usernames')

    if updated_list == 0 :

        list = df['username'].dropna().unique()

    elif updated_list == 1 :

        timestr = time.strftime("%Y_%m_%d")
        df_collected = import_data('dataset_1_user_metrics_' + timestr  + '.csv')
        df_collected['username'] = df_collected['username'].str.lower()

        list1 = df_collected['username'].to_list()
        print(len(list1))

        list2 = df['username'].dropna().unique()

        list = [x for x in list2 if x not in list1]

    return list

if __name__=="__main__":

    list = get_users_list(updated_list = 1)
    timestr = time.strftime("%Y_%m_%d")

    load_dotenv()
    tic()
    get_user_metrics(bearer_token = os.getenv('TWITTER_TOKEN'),
                list = list,
                filename = os.path.join('.', 'data', 'dataset_1_user_metrics_' + timestr  + '.csv'))
    toc()
