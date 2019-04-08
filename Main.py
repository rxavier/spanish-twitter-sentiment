import Sent
import tweepy
import json
import pickle
import sys
import pandas as pd
from statistics import mean

with open("Keys.json", "r") as f:
    keys = json.load(f)

auth = tweepy.OAuthHandler(keys["consumer_token"], keys["consumer_token_secret"])
auth.set_access_token(keys["access_token"], keys["access_token_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def tweets_replies_loop(user_list, number_tweets, trim, previous=False):
    for user in user_list:
        try:
            with open("Pickles/tweets_replies_" + user + ".p", "rb") as data_load:
                tweets_replies_data = pickle.load(data_load)
            if previous is True:
                print("Successfully loaded tweets for " + user + ", downloading " + str(number_tweets) +
                      " tweets prior to tweet ID " + str(tweets_replies_data[len(tweets_replies_data) - 1][1]) + ": " +
                      tweets_replies_data[len(tweets_replies_data) - 1][0])
                Sent.tweets_replies(api, user, number_tweets, tweets_replies_data, trim, previous=True)
            else:
                print("Previous tweets found for " + user + ", downloading last " + str(number_tweets) +
                      " tweets since tweet ID " + str(tweets_replies_data[0][1]) + ": " + tweets_replies_data[0][0])
            Sent.tweets_replies(api, user, number_tweets, tweets_replies_data, trim, previous=False)
        except IOError:
            if previous is True:
                print("Download some data first with tweets_replies_last_loop function")
            else:
                print("No previous data found for " + user + ", downloading last " + str(number_tweets) + " tweets")
                tweets_replies_data = []
                Sent.tweets_replies(api, user, number_tweets, tweets_replies_data, trim, previous=False)


def tweets_loop(user_list, number_tweets, trim, previous=False):
    for user in user_list:
        try:
            with open("Pickles/tweets_" + user + ".p", "rb") as data_load:
                tweets_data = pickle.load(data_load)
            if previous is True:
                print("Successfully loaded tweets for " + user + ", downloading " + str(number_tweets) +
                      " tweets prior to tweet ID " + str(tweets_data[len(tweets_data) - 1][1]) + ": " +
                      tweets_data[len(tweets_data) - 1][0])
                Sent.tweets(api, user, number_tweets, tweets_data, trim, previous=True)
            else:
                print("Previous tweets found for " + user + ", downloading last " + str(number_tweets) +
                      " tweets since tweet ID " + str(tweets_data[0][1]) + ": " + tweets_data[0][0])
                Sent.tweets(api, user, number_tweets, tweets_data, trim, previous=False)
        except IOError:
            if previous is True:
                print("Download some data first with tweets_replies_last_loop function")
            else:
                print("No previous data found for " + user + ", downloading last " + str(number_tweets) + " tweets")
                tweets_data = []
                Sent.tweets(api, user, number_tweets, tweets_data, trim, previous=False)


def replies_loop(user_list, number_replies, previous=False):
    for user in user_list:
        try:
            with open("Pickles/replies_" + user + ".p", "rb") as data_load:
                replies_data = pickle.load(data_load)
            if previous is True:
                print("Successfully loaded replies for " + user + ", downloading " + str(number_replies) +
                      " replies prior to tweet ID " + str(replies_data[len(replies_data) - 1][2]) + ": " +
                      replies_data[len(replies_data) - 1][1])
                Sent.replies(api, user, number_replies, replies_data, previous=True)
            else:
                print("Previous replies found for " + user + ", downloading last " + str(number_replies) +
                      " replies since tweet ID " + str(replies_data[0][2]) + ": " + replies_data[0][1])
                Sent.replies(api, user, number_replies, replies_data, previous=False)
        except IOError:
            if previous is True:
                print("Download some data first with replies_last_loop function")
            else:
                print("No previous replies found for " + user + ", downloading last " + str(number_replies) +
                      " replies")
                replies_data = []
                Sent.replies(api, user, number_replies, replies_data)


def build_user(user_list):
    full_tweets_replies_data = {}
    long_tweets_replies = []
    for user in user_list:
        with open("Pickles/tweets_replies_" + user + ".p", "rb") as dl:
            full_tweets_replies_data.update({user: pickle.load(dl)})
        for tweets in full_tweets_replies_data[user]:
            long_tweets_replies.append([user, tweets[0], tweets[7], tweets[3], tweets[4],
                                        tweets[5], tweets[2], tweets[1]])
        df = pd.DataFrame(long_tweets_replies)
    return full_tweets_replies_data, df


def build_tweets_replies(user_list, num_obs, type_data="replies"):
    named_data = {}
    long_data = []
    if type_data is "tweets":
        for user in user_list:
            with open("Pickles/tweets_" + user + ".p", "rb") as dl:
                named_data.update({user: pickle.load(dl)})
            for tweets in named_data[user]:
                long_data.append([user, tweets[0], tweets[1], tweets[2], tweets[3], tweets[4], tweets[5]])
        df_tweets = pd.DataFrame(long_data)
        mean_tweets_user = {}
        for user in named_data.keys():
            tweets_user = named_data[user]
            mean_tweets_user.update({user: mean([x[5] for x in tweets_user[0:num_obs]])})
        return named_data, mean_tweets_user, df_tweets
    elif type_data is "replies":
        for user in user_list:
            with open("Pickles/replies_" + user + ".p", "rb") as dl:
                named_data.update({user: pickle.load(dl)})
        mean_replies_user = {}
        for user in named_data.keys():
            replies_list = named_data[user]
            mean_replies_user.update({user: mean([x[6] for x in replies_list[0:num_obs]])})
        return named_data, mean_replies_user, None
    else:
        print("Only \"tweets\" or \"replies\" are accepted arguments for type_data")
        sys.exit()
