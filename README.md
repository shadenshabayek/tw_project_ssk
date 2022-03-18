# Script for the LinkLab Project

## Dataset 0: get twitter usernames 

## Dataset 1: get users metrics

Run the following script, to get Twitter users metrics (followers counts, following, description, etc.) based on the list from Dataset 0: 

```
python3 ./code/get_users_metrics_twitter.py 
```

## Dataset 2: collect tweets 

Run the following script, to get the Tweets of users based on the list from Dataset 0 (this includes referenced tweet id, retweeted/quoted/replied_to/mentionned users within list from Dataset 0) : 

```
python3 ./code/collect_twitter_data_historical.py
```

## Dataset 3 : collect following users (friends)

Run the following script, to get the Following users or friends of users based on the list from Dataset 0 (this includes Following users within list from Dataset 0) :

```
python3 ./code/collect_following_users.py
```

## Dataset 4 : collect liked tweets 
