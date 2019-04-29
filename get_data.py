import base_functions
import tweepy
import json
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


def twr(user_list, number_elements=10, trim=0, previous=False, build=True):

    for user in user_list:

        try:
            with open("jsons/tweets_replies_" + user + ".json", "r") as data_load:
                data = json.load(data_load)

            for element in data:
                element[1] = datetime.datetime.strptime(element[1], "%Y-%m-%d %H:%M:%S")

            if previous is True:
                print("Successfully loaded tweets for " + user + ", downloading " + str(number_elements) +
                      " tweets prior to tweet ID " + str(data[len(data) - 1][9]) + ": " +
                      data[len(data) - 1][0])
                base_functions.twr_base(api, user, number_elements, data, previous=True)
            else:
                print("Previous tweets found for " + user + ", downloading last " + str(number_elements) +
                      " tweets since tweet ID " + str(data[0][9]) + ": " + data[0][0])
                base_functions.twr_base(api, user, number_elements, data, trim, previous=False)

        except IOError:
            print("No previous data found for " + user + ", downloading last " + str(number_elements) + " tweets")
            data = []
            base_functions.twr_base(api, user, number_elements, data, trim, previous=False)

    if build is True:
        return twr_build(user_list)
    else:
        return None, None


def tor(user_list, number_elements=100, mean_obs=100, trim=0,
        type_data="tweets", previous=False, build=True):

    for user in user_list:

        try:

            if type_data is "replies" or type_data is "tweets":
                with open("jsons/" + type_data + "_" + user + ".json", "r") as data_load:
                    data = json.load(data_load)
            else:
                print("Only \"tweets\" and \"replies\" are accepted type_data")

            for element in data:
                element[2] = datetime.datetime.strptime(element[2], "%Y-%m-%d %H:%M:%S")

            if previous is True:
                print("Successfully loaded " + type_data + " for " + user + ", downloading " + str(number_elements) +
                      " elements prior to tweet ID " + str(data[len(data) - 1][6]) + ": " +
                      data[len(data) - 1][1])
                base_functions.tor_base(api, user, number_elements, data, type_data=type_data, previous=True)
            else:
                print("Previous " + type_data + " found for " + user + ", downloading last " + str(number_elements) +
                      " elements since tweet ID " + str(data[0][6]) + ": " + data[0][1])
                base_functions.tor_base(api, user, number_elements, data, trim, type_data=type_data, previous=False)

        except IOError:
            print("No previous " + type_data + " found for " + user + ", downloading last " + str(number_elements) +
                  " elements")
            data = []

            if type_data is "replies" or type_data is "tweets":
                base_functions.tor_base(api, user, number_elements, data, type_data=type_data, previous=False)
            else:
                print("Only \"tweets\" and \"replies\" are accepted type_data")

    if build is True:
        return tor_build(user_list=user_list, mean_obs=mean_obs, type_data=type_data)
    else:
        return None, None, None


def twr_build(user_list):
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


def tor_build(user_list, mean_obs=100, type_data="tweets"):

    named_data = {}
    long_data = []

    if type_data is "tweets" or type_data is "replies":

        for user in user_list:
            with open("jsons/" + type_data + "_" + user + ".json", "r") as dl:
                data = json.load(dl)

            for element in data:
                element[2] = datetime.datetime.strptime(element[2], "%Y-%m-%d %H:%M:%S")
                long_data.append([user, element[1], element[2], element[3], element[4], element[5]])

            named_data.update({user: data})

        df_data = pd.DataFrame(long_data)
        df_data.columns = ["User", "Tweet", "Date", "Likes", "Retweets", "Sentiment"]

        mean_elements = {}
        for user in named_data.keys():
            elements = named_data[user]
            mean_elements.update({user: mean([x[5] for x in elements[0:mean_obs] if x[5] is not None])})

        return named_data, mean_elements, df_data

    else:
        print("Only \"tweets\" or \"replies\" are accepted arguments for type_data")


def make_plots(user_list, data, type_data="tweets", start_date=None,
               end_date=None, window=7, spacing=7, operation="average", ratio=False):

    resample_funcs = {"average": lambda x: x.set_index("Date").resample("1D").mean(),
                      "sum": lambda x: x.set_index("Date").resample("1D").sum(),
                      "count": lambda x: x.set_index("Date").resample("1D").count()}
    rolling_funcs = {"average": lambda x: x.rolling(min_periods=1, window=window).mean(),
                     "sum": lambda x: x.rolling(min_periods=1, window=window).sum(),
                     "count": lambda x: x.rolling(min_periods=1, window=window).sum()}

    proc_df = data[["User", "Date", "Likes", "Retweets", "Sentiment"]]

    if type_data is "tweets":

        resample_df = proc_df.groupby("User").apply(resample_funcs[operation])

        likes = resample_df.groupby(level=0)["Likes"].apply(rolling_funcs[operation]).reset_index(name="Likes")
        retweets = resample_df.groupby(level=0)["Retweets"].apply(rolling_funcs[operation]).reset_index(name="Retweets")

        merged_df = pd.merge(likes, retweets, on=["Date", "User"],
                             how="left").groupby("User").apply(lambda x: x.interpolate(method="linear"))
        long = pd.melt(merged_df, id_vars=["User", "Date"], value_vars=["Likes", "Retweets"], value_name="Values")

    else:

        resample_df = proc_df.groupby("User").apply(resample_funcs[operation])

        sent = resample_df.groupby(level=0)["Sentiment"].apply(rolling_funcs[operation]).reset_index(name="Sentiment")
        replies = resample_df.groupby(level=0)["Sentiment"].apply(rolling_funcs[operation]).reset_index(name="Replies")

        merged_df = pd.merge(sent, replies, on=["Date", "User"],
                             how="left").groupby("User").apply(lambda x: x.interpolate(method="linear"))
        long = pd.melt(merged_df, id_vars=["User", "Date"], value_vars=["Sentiment", "Replies"], value_name="Values")

    operation_title = operation.capitalize()

    if start_date is None:
        start_date = min(long["Date"])
    if end_date is None:
        end_date = max(long["Date"])

    long_filter = long.loc[(long["Date"] >= start_date) &
                           (long["Date"] <= end_date)].loc[long["User"].isin(user_list)].sort_values(by=["variable",
                                                                                                         "Date"])
    title_ratio = ""

    if ratio is True:
        mean_users = (long_filter[~(long_filter["User"] == user_list[0])].groupby(["Date", "variable"]).mean().
                      reset_index().sort_values(by=["variable", "Date"]))
        long_filter = long_filter[long_filter["User"] == user_list[0]].reset_index(drop=True)
        long_filter_mean = pd.merge(long_filter, mean_users, on=["Date", "variable"],
                                    how="left")
        long_filter["Values"] = long_filter_mean["Values_x"].divide(long_filter_mean["Values_y"])
        title_ratio = ", ratio of " + user_list[0] + " to average of remaining users"

    long_filter["Date"] = long_filter["Date"].map(lambda x: x.strftime("%d-%m-%y"))

    sns.set(style="darkgrid", rc={"lines.linewidth": 2})
    g = sns.FacetGrid(long_filter, col="variable", hue="User", sharey=False, height=5)
    x_axis_labels = long_filter.Date.unique()
    g = g.map(plt.plot, "Date", "Values").set(xticks=x_axis_labels[0:len(x_axis_labels):spacing],
                                              xticklabels=x_axis_labels[0:len(x_axis_labels):spacing])
    g.add_legend()
    g.set_xticklabels(rotation=90)
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle(operation_title + ", last " + str(window) + " days" + title_ratio)
