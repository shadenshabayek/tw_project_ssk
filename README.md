
## Get Users Metrics

Run the following script, to get Twitter users metrics (followers counts, following, description, etc.) based on a list of Twitter usernames: 

```
python3 ./code/get_users_metrics_twitter.py 
```

## Collect Tweets 

Run the following script, to get the Tweets of users based on a list of Twitter usernames (this includes referenced tweet id, retweeted/quoted/replied_to/mentioned users within a specific list of Twitter usernames) : 

```
python3 ./code/collect_twitter_data_historical.py
```

## Collect Following Users (friends)

Run the following script, to get the Following users (or friends) of users based on on a list of Twitter accounts ID (this includes Following users within a specific list of Twitter usernames) :

```
python3 ./code/collect_following_users.py
```

## Collect Liked Tweets 

Run the following script, to get the last 200 tweets of a given user based on on a list of Twitter accounts ID  :

```
python3 ./code/collect_liked_tweets.py
```

