import pandas as pd
import selenium
import re

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

```sample code ```

def collect_remaining_users():

    first_name = ['emmanuel', 'gerald', 'fakename', 'sgyugde']
    last_name = ['macron', 'darmanin', 'fakelastname', 'ugjgs']

    zipped_lists = zip(first_name, last_name)

    prefixe = 'https://www.google.com/search?q='

    list = [prefixe + x + '+' + y + '+twitter' for (x, y) in zipped_lists]
    print(list)

    list_handles = []

    for url in list:

        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.get(url)

        try:
            element = browser.find_element_by_xpath("//h3[@class='haz7je']")
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

    collect_remaining_users()
