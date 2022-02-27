import ast
import os
import numpy as np
import pandas as pd
import selenium
import re
import time
import unidecode


pd.options.display.max_colwidth = 300
pd.options.mode.chained_assignment = None  # default='warn'


from datetime import date
from dotenv import load_dotenv
from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from utils import (get_user_metrics, import_data, save_data)

def get_mentions_usernames_Twitter (collection_interupted, filename, title):

    df = import_data(filename)

    df = df.dropna(subset=['mentions_username'])

    for index, row in df.iterrows():
        df.at[index, 'mentions_username']=ast.literal_eval(row['mentions_username'])

    df = df.explode('mentions_username')

    df = df[['username',
            'mentions_username',
            'type_of_tweet',
            'id',
            'text',
            'followers_count']]

    df = df.dropna(subset=['mentions_username'])

    df['mentions_username'] = df['mentions_username'].str.lower()
    df['username'] = df['username'].str.lower()

    df1 = df.groupby(['mentions_username'], as_index = False).size().sort_values(by = 'size', ascending = False)

    if collection_interupted == 1:

        df_collected = import_data(title + '.csv')
        print(title)
        df_collected['username'] = df_collected['username'].str.lower()
        list_collected = df_collected['username'].tolist()

        list_mentions = df1['mentions_username'].tolist()
        print(len(list_mentions))
        list = [x for x in list_mentions if x not in list_collected]
        print(len(list))
    else :

        list = df1['mentions_username'].tolist()

    return list

def collect_users(collection_interupted, filename, title):

    list = get_mentions_usernames_Twitter(collection_interupted, filename, title)
    file_path = os.path.join('.', 'data', title  + '.csv')

    load_dotenv()

    get_user_metrics(bearer_token = os.getenv('TWITTER_TOKEN'),
                list = list,
                filename = file_path)

def keep_politicians(filename):

    df = import_data(filename)
    df.drop_duplicates(subset=['username'])
    #print(df.info())

    df['username'] = df['username'].str.lower()
    df['description'] = df['description'].str.lower()
    df['description'] = df['description'].fillna('pas de description')

    # list_sec = ['secrétaire']
    # df_test = df[df.description.apply(lambda tweet: any(words in tweet for words in list_sec))]
    # print(df_test)

    mylist = ['maire ',
            'députée ',
            'député ',
            'sénateur ',
            'sénatrice ',
            'secrétaire d’état', #fsalatbaroux
            'secrétaire d’etat',
            'ministre' ]
            #conseiller ?

    list_presidents_politicians = ['emmanuelmacron',
                                    'fhollande',
                                    'nicolassarkozy',
                                    'agnesbuzyn',
                                    'gerardcollomb',
                                    'pascaleboistard',
                                    'sibethndiaye',
                                    'pietraszewski_l']

    #président de... so many  ex: journaliste au pôle social de @mediapart / ex du pôle politique / président d'honneur de @assoajis
    df1 = df[df.description.apply(lambda tweet: any(words in tweet for words in mylist))]
    #print(df[df['username'] == 'gabrielattal'])
    list_conseiller = ['conseiller régional ']

    df2 = df[df.description.apply(lambda tweet: all(words in tweet for words in list_conseiller))]

    list1 = df1['username'].tolist()
    list_CR = df2['username'].tolist()
    list1 = list1 + list_presidents_politicians + list_CR

    list2 = df['username'].tolist()

    list = [x for x in list2 if x not in list1]

    print('Number of users before filtering with keywords', len(df))
    print('Number of users After filtering with keywords', len(df[df['username'].isin(list1)]))

    df_final = df[df['username'].isin(list1)]
    df_final = df_final.sort_values(by = 'follower_count', ascending = False)

    return df_final

def collect_users_all_sources(lcp, senat, collection_interupted):

    if lcp == 1:

        collect_users(collection_interupted = collection_interupted,
                        filename = 'twitter_data_LCP.csv',
                        title = 'users_metrics_mentions_by_lcp_all_time')
    elif senat == 1:

        collect_users(collection_interupted = collection_interupted,
                        filename = 'twitter_data_senat.csv',
                        title = 'users_metrics_mentions_by_senat_all_time')

def remove_emojis(text):

    #text = u'Jennifer De Temmerman 🌍🕊🐝🏳️‍🌈🇪🇺🇫🇷'
    #text = 'Jennifer De Temmerman 🌍🕊🐝🏳️‍🌈🇪🇺🇫🇷'
    #print(text) # with emoji

    text_with_emoji = text

    emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)

    emoji_free_text = emoji_pattern.sub(r'', text)

    #print(emoji_free_text) # no emoji

    return emoji_free_text

def remove_accents(text):

    accent_free_text = unidecode.unidecode(text)
    #print(accent_free_text)
    return accent_free_text

def clean_names(df):

    dict = {"prof. ": "",
           #" ph": "",
           #"ch. ": "christine ",
           "_": " ",
           "\@": " ",
           " fi 93.9": " ",
           ". senateur de vaucluse": " ",
           "senateur honoraire": " ",
           ",senatrice de la cote d'or": " ",
           "-": " ",
           "\'": " ",
           "j j ": "jean jacques ",
           "senat ": " ",
           " senat ": " ",
           "senateur ": " ",
           " senat": " ",
           " deputee": " ",
           " depute": " ",
           "deputee obono": "daniele obono",
           "marleneschiappa": "marlene schiappa",
           "maudolivier": "maud olivier",
           "o. audibert-troin": "olivier audibert-troin",
           "ch. pires beaune": "christine pires beaune",
           "mathiasin": "max mathiasin",
           "delaverpilliere": "charles de la verpilliere"}

    if 'username' and 'name' in df.columns.tolist():

        df['username'] = df['username'].str.lower()
        df['name'] = df['name'].apply(remove_emojis)
        df['name'] = df['name'].apply(remove_accents)
        df['name'] = df['name'].str.strip()

        #df['name'] = df['name'].replace("prof. ", "", regex=True)
        df['name'] = df['name'].str.lower()
        df['name'] = df['name'].replace(dict, regex=True)
        df['name'] = df['name'].str.split('- ').str[0]
        df['name'] = df['name'].str.split(', ').str[0]
        df['name'] = df['name'].str.split('#').str[0]

        df['name'] = df['name'].str.strip()

        for index, row in df.iterrows():
            if row['name'][-2:] == ' n' :
                df.at[index, 'name']= row['name'][:-2]

            if row['name'][-3:] == ' ph':
                df.at[index, 'name']= row['name'][:-3]
    return df

def keep_politicians_all_sources():

    df1 = keep_politicians(filename = 'users_metrics_mentions_by_lcp_all_time.csv')
    print('Number of Twitter handles, lcp:', len(df1))

    df2 = keep_politicians(filename = 'users_metrics_mentions_by_senat_all_time.csv')
    print('Number of Twitter handles, senat:', len(df2))

    df = pd.concat([df1, df2])
    df = df.drop_duplicates(subset = ['username'])
    df = df.sort_values(by = 'follower_count', ascending = False)

    list_adj = ['adjoint']

    df_exclude = df[df.description.apply(lambda tweet: any(words in tweet for words in list_adj))]
    #print(df_exclude.info())
    #print(df_exclude.head(20))

    list_adj_exclude = df_exclude['username'].tolist()

    list_false = ['justintrudeau',
    'garnodierpierre',
    'e_philippepm',
    'lxgrima',
    'franckmorel1207',
    'renauddeschamps',
    'cousin_gregoire',
    'tribulipietz',
    'martialbourquin',
    'sports_gouv',
    'egalite_gouv',
    'najwaelhaite', #adj.
    'matignon',
    'minakuaubin',
    'diavictimes',
    'deputequimarche',
    'vousnousils',
    'anticor_org',
    'clementleonr',
    'ghassansalame']

    exclude = list_adj_exclude + list_false

    df = df[~df['username'].isin(exclude)]
    #print(df[['username', 'follower_count', 'description']].tail(50))
    print('Number of Twitter handles:', len(df))

    list = df['username'].tolist()

    df = clean_names(df)

    df_final = df[df['username'].isin(list)]

    timestr = time.strftime("%Y_%m_%d")
    name_df = 'twitter_handles_politicians_lcp_senat_' + timestr + '.csv'
    save_data(df_final, name_df, 0)

    return list

def collect_remaining_users():

    first_name = ['emmanuel', 'gerald', 'fakename', 'sgyugde']
    last_name = ['macron', 'darmanin', 'fakelastname', 'ugjgs']

    zipped_lists = zip(first_name, last_name)

    prefixe = 'https://www.google.com/search?q='

    list = [prefixe + x + '+' + y + '+twitter' for (x, y) in zipped_lists]
    print(list)

    list_handles = []

    #url = 'https://www.google.com/search?q=emmanuel+macron+twitter'
    for url in list:

        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.get(url)

        try:
            element = browser.find_element_by_xpath("//h3[@class='haz7je']")
            #twitter_handles = re.findall(r'@\S+', element.text)[0]
            twitter_handles = re.findall('\((.*?)\)', element.text)[0]
            print(element.text)
            print(twitter_handles)
        except:
            print('I did not find the user!')
            twitter_handles=''

        browser.quit()

        list_handles.append(twitter_handles[1:])

    print(list_handles)

if __name__=="__main__":

    # collect_users_all_sources(lcp = 0,
    #                         senat = 1,
    #                         collection_interupted = 0 )

    keep_politicians_all_sources()
    #collect_remaining_users()
