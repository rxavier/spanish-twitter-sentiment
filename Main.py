import Sent
import tweepy
import json
import sys
import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statistics import mean

with open("Keys.json", "r") as f:
    keys = json.load(f)

auth = tweepy.OAuthHandler(keys["consumer_token"], keys["consumer_token_secret"])
auth.set_access_token(keys["access_token"], keys["access_token_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def tweets_with_replies_loop(user_list, number_tweets=10, trim=0, previous=False, build=False):
    for user in user_list:
        try:
            with open("jsons/tweets_replies_" + user + ".json", "r") as data_load:
                data = json.load(data_load)
            for tweet in data:
                tweet[1] = datetime.datetime.strptime(tweet[1], "%Y-%m-%d %H:%M:%S")
            if previous is True:
                print("Successfully loaded tweets for " + user + ", downloading " + str(number_tweets) +
                      " tweets prior to tweet ID " + str(data[len(data) - 1][9]) + ": " +
                      data[len(data) - 1][0])
                Sent.tweets_with_replies(api, user, number_tweets, data, trim, previous=True)
            else:
                print("Previous tweets found for " + user + ", downloading last " + str(number_tweets) +
                      " tweets since tweet ID " + str(data[0][9]) + ": " + data[0][0])
                Sent.tweets_with_replies(api, user, number_tweets, data, trim, previous=False)
        except IOError:
            if previous is True:
                print("Download some data first with tweets_replies_last_loop function")
            else:
                print("No previous data found for " + user + ", downloading last " + str(number_tweets) + " tweets")
                data = []
                Sent.tweets_with_replies(api, user, number_tweets, data, trim, previous=False)
    if build is True:
        return build_tweets_with_replies(user_list)
    else:
        return None, None


def tweets_or_replies_loop(user_list, number_elements=100, mean_obs=100, trim=0,
                           type_data="replies", previous=False, build=False):
    if type_data is "replies":
        for user in user_list:
            try:
                with open("jsons/replies_" + user + ".json", "r") as data_load:
                    data = json.load(data_load)
                for reply in data:
                    reply[2] = datetime.datetime.strptime(reply[2], "%Y-%m-%d %H:%M:%S")
                if previous is True:
                    print("Successfully loaded replies for " + user + ", downloading " + str(number_elements) +
                          " replies prior to tweet ID " + str(data[len(data) - 1][6]) + ": " +
                          data[len(data) - 1][1])
                    Sent.tweets_or_replies(api, user, number_elements, data, type_data="replies", previous=True)
                else:
                    print("Previous replies found for " + user + ", downloading last " + str(number_elements) +
                          " replies since tweet ID " + str(data[0][6]) + ": " + data[0][1])
                    Sent.tweets_or_replies(api, user, number_elements, data, type_data="replies", previous=False)
            except IOError:
                if previous is True:
                    print("Download some data first with replies_last_loop function")
                else:
                    print("No previous replies found for " + user + ", downloading last " + str(number_elements) +
                          " replies")
                    data = []
                    Sent.tweets_or_replies(api, user, number_elements, data, type_data="replies", previous=False)
        if build is True:
            return build_tweets_or_replies(user_list=user_list, mean_obs=mean_obs, type_data=type_data)
        else:
            return None, None, None
    elif type_data is "tweets":
        for user in user_list:
            try:
                with open("jsons/tweets_" + user + ".json", "r") as data_load:
                    data = json.load(data_load)
                for tweet in data:
                    tweet[2] = datetime.datetime.strptime(tweet[2], "%Y-%m-%d %H:%M:%S")
                if previous is True:
                    print("Successfully loaded tweets for " + user + ", downloading " + str(number_elements) +
                          " tweets prior to tweet ID " + str(data[len(data) - 1][6]) + ": " +
                          data[len(data) - 1][0])
                    Sent.tweets_or_replies(api, user, number_elements, data, trim, type_data="tweets",
                                           previous=True)
                else:
                    print("Previous tweets found for " + user + ", downloading last " + str(number_elements) +
                          " tweets since tweet ID " + str(data[0][6]) + ": " + data[0][0])
                    Sent.tweets_or_replies(api, user, number_elements, data, trim, type_data="tweets",
                                           previous=False)
            except IOError:
                if previous is True:
                    print("Download some data first with tweets_replies_last_loop function")
                else:
                    print("No previous data found for " + user + ", downloading last " + str(number_elements) +
                          " tweets")
                    data = []
                    Sent.tweets_or_replies(api, user, number_elements, data, trim, type_data="tweets",
                                           previous=False)
        if build is True:
            return build_tweets_or_replies(user_list=user_list, mean_obs=mean_obs, type_data=type_data)
        else:
            return None, None, None
    else:
        print("Only \"tweets\" and \"replies\" are accepted type_data")
        return None, None, None


def build_tweets_with_replies(user_list):
    full_tweets_replies_data = {}
    long_tweets_replies = []

    for user in user_list:
        with open("jsons/tweets_replies_" + user + ".json", "r") as dl:
            data = json.load(dl)

        for tweet in data:
            tweet[1] = datetime.datetime.strptime(tweet[1], "%Y-%m-%d %H:%M:%S")
            long_tweets_replies.append([user, tweet[0], tweet[1], tweet[2], tweet[3],
                                        tweet[4], tweet[5], tweet[6], tweet[7], tweet[8]])

        full_tweets_replies_data.update({user: data})
    user_df = pd.DataFrame(long_tweets_replies)
    return full_tweets_replies_data, user_df


def build_tweets_or_replies(user_list, mean_obs=100, type_data="replies"):
    named_data = {}
    long_data = []

    if type_data is "tweets":
        for user in user_list:
            with open("jsons/tweets_" + user + ".json", "r") as dl:
                data = json.load(dl)

            for tweet in data:
                tweet[2] = datetime.datetime.strptime(tweet[2], "%Y-%m-%d %H:%M:%S")
                long_data.append([tweet[0], tweet[1], tweet[2], tweet[3], tweet[4], tweet[5], tweet[6]])

            named_data.update({user: data})

        df_tweets = pd.DataFrame(long_data)
        df_tweets.columns = ["User", "Tweet", "Date", "Likes", "Retweets", "Sentiment", "ID"]
        df_tweets["Date"] = pd.to_datetime(df_tweets["Date"])

        mean_tweets_user = {}
        for user in named_data.keys():
            tweets_user = named_data[user]
            mean_tweets_user.update({user: mean([x[5] for x in tweets_user[0:mean_obs] if x[5] is not None])})
        return named_data, mean_tweets_user, df_tweets

    elif type_data is "replies":
        for user in user_list:
            with open("jsons/replies_" + user + ".json", "r") as dl:
                data = json.load(dl)

            for reply in data:
                reply[3] = datetime.datetime.strptime(reply[2], "%Y-%m-%d %H:%M:%S")

            named_data.update({user: data})

        mean_replies_user = {}
        for user in named_data.keys():
            replies_list = named_data[user]
            mean_replies_user.update({user: mean([x[5] for x in replies_list[0:mean_obs] if x[5] is not None])})
        return named_data, mean_replies_user, None

    else:
        print("Only \"tweets\" or \"replies\" are accepted arguments for type_data")
        sys.exit()


def make_plots(data, user_list, start_date=None, end_date=None, window=7, spacing=7, operation="average"):
    proc_df = data[["User", "Date", "Likes", "Retweets"]]
    if operation == "average":
        resample_df = proc_df.groupby("User").apply(lambda x: x.set_index("Date").resample("1D").mean())
        likes = resample_df.groupby(level=0)["Likes"].apply(
            lambda x: x.shift().rolling(min_periods=1, window=window).mean()).reset_index(name="Likes")
        retweets = resample_df.groupby(level=0)["Retweets"].apply(
            lambda x: x.shift().rolling(min_periods=1, window=window).mean()).reset_index(name="Retweets")
        title = "Average"
    elif operation == "sum":
        resample_df = proc_df.groupby("User").apply(lambda x: x.set_index("Date").resample("1D").sum())
        likes = resample_df.groupby(level=0)["Likes"].apply(
            lambda x: x.shift().rolling(min_periods=1, window=window).sum()).reset_index(name="Likes")
        retweets = resample_df.groupby(level=0)["Retweets"].apply(
            lambda x: x.shift().rolling(min_periods=1, window=window).sum()).reset_index(name="Retweets")
        title = "Sum"
    else:
        print("Only \"sum\" and \"mean\" are accepted operations")
        sys.exit()
    merged_df = pd.merge(likes, retweets, on=["Date", "User"],
                         how="left").groupby("User").apply(lambda x: x.interpolate(method="linear"))
    long = pd.melt(merged_df, id_vars=["User", "Date"],
                   value_vars=["Likes", "Retweets"], value_name="Values")
    if start_date is None:
        start_date = min(long["Date"])
    if end_date is None:
        end_date = max(long["Date"])
    long_filter = long.loc[(long["Date"] >= start_date) &
                           (long["Date"] <= end_date)].loc[long["User"].isin(user_list)].sort_values(by="Date")

    sns.set(style="darkgrid", rc={"lines.linewidth": 2})
    g = sns.FacetGrid(long_filter, col="variable", hue="User", sharey=False, height=5)
    long_filter["Date"] = long_filter["Date"].map(lambda x: x.strftime("%d-%m-%y"))
    x_axis_labels = long_filter.Date.unique()
    g = g.map(plt.plot, "Date", "Values").set(xticks=x_axis_labels[0:len(x_axis_labels):spacing],
                                              xticklabels=x_axis_labels[0:len(x_axis_labels):spacing])
    g.add_legend()
    g.set_xticklabels(rotation=90)
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle(title + " of likes and retweets, last " + str(window) + " days")
