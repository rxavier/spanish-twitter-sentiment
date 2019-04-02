import Sent
import tweepy
import json
import pickle

with open("Keys.json", "r") as f:
    keys = json.load(f)

with open("Candidates.json", "r") as f:
    candidates = json.load(f)

auth = tweepy.OAuthHandler(keys["consumer_token"], keys["consumer_token_secret"])
auth.set_access_token(keys["access_token"], keys["access_token_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

num = 10


def get_latest(user_dict):
    for user in user_dict.values():
        try:
            with open("Pickles/" + user + ".p", "rb") as data_load:
                data = pickle.load(data_load)
            print("Previous data found for " + user + ", downloading last " + str(num) + " tweets since tweet ID " +
                  str(data[0][1]) + ": " + data[0][0])
            Sent.sent_latest(api, user, num, data)
        except IOError:
            print("No previous data found for " + user + ", downloading last " + str(num) + " tweets")
            data = []
            Sent.sent_latest(api, user, num, data)


def build_data(user_dict):
    full_data = {}
    for user in user_dict.values():
        with open("Pickles/" + user + ".p", "rb") as dl:
            full_data.update({user: pickle.load(dl)})


def get_previous(user_dict):
    for user in user_dict.values():
        try:
            with open("Pickles/" + user + ".p", "rb") as data_load:
                data = pickle.load(data_load)
            print("Successfully loaded data for " + user + ", downloading " + str(num) + " tweets prior to tweet ID " +
                  str(data[len(data)-1][1]) + ": " + data[len(data)-1][0])
            Sent.sent_previous(api, user, num, data)
        except IOError:
            print("Download some data first with get_latest function")
