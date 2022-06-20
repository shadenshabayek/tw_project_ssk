import numpy as np
import os
import time


from datetime import date
from dotenv import load_dotenv
from time import sleep

from utils import (get_user_metrics,
                    tic,
                    toc,
                    import_data,
                    save_data)



def get_users_list(updated_list):

    df = import_data('match_twitter_theo_2022_02_23.csv')

    df = df.rename(columns={'nom_prenom_std3': 'name', 'total': 'username'})
    df['username'] = df['username'].str.lower()
    df = df.drop_duplicates(subset=['name'], keep='first')
    df['username'] = df['username'].replace({'https://twitter com/jjgiannesini': 'jjgiannesini'}, regex=True)
    print('There are', len(df['username'].dropna().unique()), 'usernames')

    list = df['username'].dropna().unique()

    return list

def get_users_list_updated_2022_05_31():

    df = import_data('match_twitter2.csv')

    df = df.rename(columns={'nom_prenom_std3': 'name', 'total': 'username'})
    df['username'] = df['username'].str.lower()
    df = df.drop_duplicates(subset=['username'], keep='first')
    df['username'] = df['username'].replace({'https://twitter com/francklefvre': 'francklefvre'}, regex=True)
    df['username'] = df['username'].replace({'https://twitter com/emercier4': 'emercier4'}, regex=True)

    print('There are', len(df['username'].dropna().unique()), 'usernames')

    list = df['username'].dropna().unique()

    return list

def get_users_from_previous_collection():

    df = import_data('dataset_1_user_metrics_2022_06_12.csv')
    list = df['username'].to_list()
    print(len(list))

    return list
def get_idle_accounts():

    df = import_data('dataset_1_user_metrics_new_list_2022_06_12.csv')
    description = ['did not find the account, deleted or suspended']
    df = df[df['description'].isin(description)]
    timestr = time.strftime("%Y_%m_%d")
    save_data(df, 'missing_accounts_' + timestr + '.csv', 0)
    print(df['username'].tolist())
    print(len(df))

    return list

def main():
    #list = get_users_from_previous_collection()
    list = get_users_list_updated_2022_05_31()
    timestr = time.strftime("%Y_%m_%d")
    #timestr = '2022_06_12'

    load_dotenv()
    get_user_metrics(bearer_token = os.getenv('TWITTER_TOKEN'),
                list = list,
                filename = os.path.join('.', 'data', 'dataset_1_user_metrics_new_list_' + timestr  + '.csv'))

if __name__=="__main__":

    main()
    #get_idle_accounts()
