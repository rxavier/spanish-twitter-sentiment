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


def search_hits(user_list, extra_list, location, language, number_elements=100,
                mean_obs=100, previous=False, build=True):

    for user, extra in zip(user_list, extra_list):

        try:

            with open("jsons/search_" + user + ".json", "r") as data_load:
                data = json.load(data_load)

            for element in data:
                element[2] = datetime.datetime.strptime(element[2], "%Y-%m-%d %H:%M:%S")

            if previous is True:
                print("Successfully loaded data for " + user + ", downloading " + str(number_elements) +
                      " elements prior to tweet ID " + str(data[len(data) - 1][6]) + ": " +
                      data[len(data) - 1][1])
                base_functions.search_base(api, location=location, language=language, user=user, extra=extra,
                                           number_elements=number_elements, data=data, previous=True)
            else:
                print("Previous data found for " + user + ", downloading last " + str(number_elements) +
                      " elements since tweet ID " + str(data[0][6]) + ": " + data[0][1])
                base_functions.search_base(api, location=location, language=language, user=user, extra=extra,
                                           number_elements=number_elements, data=data, previous=False)

        except IOError:
            print("No previous data found for " + user + ", downloading last " + str(number_elements) +
                  " elements")
            data = []
            base_functions.search_base(api, location=location, language=language, user=user, extra=extra,
                                       number_elements=number_elements, data=data, previous=False)

    if build is True:
        return search_build(user_list=user_list, mean_obs=mean_obs)
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


def search_build(user_list, mean_obs=100):

    named_data = {}
    long_data = []

    for user in user_list:
        with open("jsons/search_" + user + ".json", "r") as dl:
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


def make_plots(user_list, data, type_data="tweets", start_date=None,
               end_date=None, window=7, spacing=7, min_window=1, operation="average", user_ratio=None):

    if start_date is None:
        start_date = min(data["Date"])
    if end_date is None:
        end_date = max(data["Date"])

    resample_funcs = {"average": (lambda x: x.set_index("Date").resample("1D").mean().
                                  reindex(pd.date_range(datetime.datetime.strptime(start_date, "%Y-%m-%d") -
                                                        datetime.timedelta(days=window), end_date, freq="D"))),
                      "sum": (lambda x: x.set_index("Date").resample("1D").sum().
                              reindex(pd.date_range(datetime.datetime.strptime(start_date, "%Y-%m-%d") -
                                                    datetime.timedelta(days=window), end_date, freq="D"))),
                      "count": (lambda x: x.set_index("Date").resample("1D").count().
                                reindex(pd.date_range(datetime.datetime.strptime(start_date, "%Y-%m-%d") -
                                                      datetime.timedelta(days=window), end_date, freq="D")))}
    rolling_funcs = {"average": lambda x: x.rolling(min_periods=min_window, window=window).mean(),
                     "sum": lambda x: x.rolling(min_periods=min_window, window=window).sum(),
                     "count": lambda x: x.rolling(min_periods=min_window, window=window).sum()}

    proc_df = data[["User", "Date", "Likes", "Retweets", "Sentiment"]]

    if type_data is "tweets":

        resample_df = proc_df.groupby("User").apply(resample_funcs[operation])

        likes = (resample_df.groupby(level=0)["Likes"].apply(rolling_funcs[operation]).
                 reset_index().rename(columns={"level_1": "Date"}))
        retweets = (resample_df.groupby(level=0)["Retweets"].apply(rolling_funcs[operation]).
                    reset_index().rename(columns={"level_1": "Date"}))

        merged_df = pd.merge(likes, retweets, on=["Date", "User"],
                             how="left").groupby("User").apply(lambda x: x.interpolate(method="linear"))
        long = pd.melt(merged_df, id_vars=["User", "Date"], value_vars=["Likes", "Retweets"], value_name="Values")

    else:

        resample_df = proc_df.groupby("User").apply(resample_funcs["average"])
        sent = (resample_df.groupby(level=0)["Sentiment"].apply(rolling_funcs["average"]).
                reset_index().rename(columns={"level_1": "Date"}))

        resample_df = proc_df.groupby("User").apply(resample_funcs["count"])
        replies = (resample_df.groupby(level=0)["Sentiment"].apply(rolling_funcs["count"]).
                   reset_index().rename(columns={"level_1": "Date", "Sentiment": "Replies"}))

        merged_df = pd.merge(sent, replies, on=["Date", "User"],
                             how="left").groupby("User").apply(lambda x: x.interpolate(method="linear"))
        long = pd.melt(merged_df, id_vars=["User", "Date"], value_vars=["Sentiment", "Replies"], value_name="Values")

    operation_title = operation.capitalize()

    long_filter = long.loc[(long["Date"] >= start_date) &
                           (long["Date"] <= end_date)].loc[long["User"].isin(user_list)]
    title_ratio = ""

    if user_ratio is not None:
        mean_users = (long_filter[~(long_filter["User"] == user_ratio)].groupby(["Date", "variable"]).mean().
                      reset_index())
        long_filter = long_filter[long_filter["User"] == user_ratio].reset_index(drop=True)
        long_filter_mean = pd.merge(long_filter, mean_users, on=["Date", "variable"],
                                    how="left")
        long_filter["Values"] = long_filter_mean["Values_x"].divide(long_filter_mean["Values_y"])
        title_ratio = ", ratio of " + user_ratio + " to average of remaining users"

    long_filter["Date"] = long_filter["Date"].map(lambda x: x.strftime("%d-%m-%y"))

    sns.set(style="darkgrid", rc={"lines.linewidth": 2})
    g = sns.FacetGrid(long_filter, col="variable", hue="User", sharey=False, height=5)
    x_axis_labels = long_filter.Date.unique()
    g = g.map(plt.plot, "Date", "Values").set(xticks=x_axis_labels[0:len(x_axis_labels):spacing],
                                              xticklabels=x_axis_labels[0:len(x_axis_labels):spacing])
    g.add_legend()
    g.set_xticklabels(rotation=90)
    plt.subplots_adjust(top=0.9)
    if type_data is "tweets":
        g.fig.suptitle(operation_title + ", last " + str(window) + " days" + title_ratio)
    else:
        g.fig.suptitle("Average sentiment and reply count, last " + str(window) + " days" + title_ratio)
    return long_filter
