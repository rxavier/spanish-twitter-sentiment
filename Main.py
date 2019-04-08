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


def user_loop(user_list, number_tweets, trim=0, previous=False):
    for user in user_list:
        try:
            with open("Pickles/tweets_replies_" + user + ".p", "rb") as data_load:
                user_data = pickle.load(data_load)
            if previous is True:
                print("Successfully loaded tweets for " + user + ", downloading " + str(number_tweets) +
                      " tweets prior to tweet ID " + str(user_data[len(user_data) - 1][1]) + ": " +
                      user_data[len(user_data) - 1][0])
                Sent.user_data(api, user, number_tweets, user_data, trim, previous=True)
            else:
                print("Previous tweets found for " + user + ", downloading last " + str(number_tweets) +
                      " tweets since tweet ID " + str(user_data[0][1]) + ": " + user_data[0][0])
            Sent.user_data(api, user, number_tweets, user_data, trim, previous=False)
        except IOError:
            if previous is True:
                print("Download some data first with tweets_replies_last_loop function")
            else:
                print("No previous data found for " + user + ", downloading last " + str(number_tweets) + " tweets")
                user_data = []
                Sent.user_data(api, user, number_tweets, user_data, trim, previous=False)


def tweets_replies_loop(user_list, number_elements, trim=0, type_data="replies", previous=False):
    if type_data is "replies":
        for user in user_list:
            try:
                with open("Pickles/replies_" + user + ".p", "rb") as data_load:
                    replies_data = pickle.load(data_load)
                if previous is True:
                    print("Successfully loaded replies for " + user + ", downloading " + str(number_elements) +
                          " replies prior to tweet ID " + str(replies_data[len(replies_data) - 1][2]) + ": " +
                          replies_data[len(replies_data) - 1][1])
                    Sent.tweets_replies(api, user, number_elements, replies_data, type_data="replies", previous=True)
                else:
                    print("Previous replies found for " + user + ", downloading last " + str(number_elements) +
                          " replies since tweet ID " + str(replies_data[0][2]) + ": " + replies_data[0][1])
                    Sent.tweets_replies(api, user, number_elements, replies_data, type_data="replies", previous=False)
            except IOError:
                if previous is True:
                    print("Download some data first with replies_last_loop function")
                else:
                    print("No previous replies found for " + user + ", downloading last " + str(number_elements) +
                          " replies")
                    replies_data = []
                    Sent.tweets_replies(api, user, number_elements, replies_data, type_data="replies", previous=False)
    elif type_data is "tweets":
        for user in user_list:
            try:
                with open("Pickles/tweets_" + user + ".p", "rb") as data_load:
                    tweets_data = pickle.load(data_load)
                if previous is True:
                    print("Successfully loaded tweets for " + user + ", downloading " + str(number_elements) +
                          " tweets prior to tweet ID " + str(tweets_data[len(tweets_data) - 1][1]) + ": " +
                          tweets_data[len(tweets_data) - 1][0])
                    Sent.tweets_replies(api, user, number_elements, tweets_data, trim, type_data="tweets",
                                        previous=True)
                else:
                    print("Previous tweets found for " + user + ", downloading last " + str(number_elements) +
                          " tweets since tweet ID " + str(tweets_data[0][1]) + ": " + tweets_data[0][0])
                    Sent.tweets_replies(api, user, number_elements, tweets_data, trim, type_data="tweets",
                                        previous=False)
            except IOError:
                if previous is True:
                    print("Download some data first with tweets_replies_last_loop function")
                else:
                    print("No previous data found for " + user + ", downloading last " + str(number_elements) +
                          " tweets")
                    tweets_data = []
                    Sent.tweets_replies(api, user, number_elements, tweets_data, trim, type_data="tweets",
                                        previous=False)
    else:
        print("Only \"tweets\" or \"replies\" are accepted arguments for type_data")
        sys.exit()


def build_user(user_list):
    full_tweets_replies_data = {}
    long_tweets_replies = []
    for user in user_list:
        with open("Pickles/tweets_replies_" + user + ".p", "rb") as dl:
            full_tweets_replies_data.update({user: pickle.load(dl)})
        for tweets in full_tweets_replies_data[user]:
            long_tweets_replies.append([user, tweets[0], tweets[7], tweets[3], tweets[4],
                                        tweets[5], tweets[2], tweets[1]])
        user_df = pd.DataFrame(long_tweets_replies)
    return full_tweets_replies_data, user_df


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
        df_tweets.columns = ["User", "Tweet", "ID", "Date", "Likes", "Retweets", "Sentiment"]
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
