import Sent
import tweepy
import json
import pickle

with open("Keys.json", "r") as f:
    keys = json.load(f)

auth = tweepy.OAuthHandler(keys["consumer_token"], keys["consumer_token_secret"])
auth.set_access_token(keys["access_token"], keys["access_token_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def tweets_replies_loop(user_list, number_tweets, trim, previous=False):
    for user in user_list:
        try:
            with open("Pickles/tweets_replies_" + user + ".p", "rb") as data_load:
                tweets_data = pickle.load(data_load)
            if previous is True:
                print("Successfully loaded tweets for " + user + ", downloading " + str(number_tweets) +
                      " tweets prior to tweet ID " + str(tweets_data[len(tweets_data) - 1][1]) + ": " +
                      tweets_data[len(tweets_data) - 1][0])
                Sent.tweets_replies(api, user, number_tweets, tweets_data, trim, previous=True)
            else:
                print("Previous tweets found for " + user + ", downloading last " + str(number_tweets) +
                      " tweets since tweet ID " + str(tweets_data[0][1]) + ": " + tweets_data[0][0])
            Sent.tweets_replies(api, user, number_tweets, tweets_data, trim, previous=False)
        except IOError:
            if previous is True:
                print("Download some data first with tweets_replies_last_loop function")
            else:
                print("No previous data found for " + user + ", downloading last " + str(number_tweets) + " tweets")
                tweets_data = []
                Sent.tweets_replies(api, user, number_tweets, tweets_data, trim, previous=False)


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


def build_tweets(user_list):
    full_tweets_data = {}
    for user in user_list:
        with open("Pickles/tweets_replies_" + user + ".p", "rb") as dl:
            full_tweets_data.update({user: sorted(pickle.load(dl), key=lambda x: x[2], reverse=True)})
    return full_tweets_data


def build_replies(user_list):
    full_replies_data = {}
    for user in user_list:
        with open("Pickles/replies_" + user + ".p", "rb") as dl:
            full_replies_data.update({user: sorted(pickle.load(dl), key=lambda x: x[2], reverse=True)})
    return full_replies_data
