import tweepy
import datetime
import re
import json
from statistics import mean
from classifier import SentimentClassifier

clf = SentimentClassifier()


def twr_base(api, user, number_elements, data, trim=0, previous=False):

    if previous is True:
        first_id = data[len(data) - 1][9]
        tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, max_id=first_id - 1,
                                     tweet_mode="extended").items(number_elements)
    else:

        if len(data) == 0:
            tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user,
                                         tweet_mode="extended").items(number_elements)
        elif trim > 0:
            data = data[trim:]
            last_id = data[0][9]
            print("Trimming " + str(trim) + " tweets. Last tweet considered is " + data[0][0])
            tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                         tweet_mode="extended").items(number_elements)
        else:
            last_id = data[0][9]
            tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                         tweet_mode="extended").items(number_elements)

    for tweet in tweet_cursor:

        if (not tweet.retweeted and ("RT @" not in tweet.full_text) and
                ((datetime.datetime.utcnow() - tweet.created_at).days < 9) and
                not tweet.full_text.startswith("@")):
            tweet_to_evaluate = re.sub("@[A-z0-9_]+|http\\S+", "", tweet.full_text).strip()

            if len(tweet_to_evaluate) < 4:
                tweet_sentiment = None
            else:
                tweet_sentiment = clf.predict(tweet_to_evaluate)

            replies_to = []
            reply_cursor = tweepy.Cursor(api.search, q="to:" + user, tweet_mode="extended",
                                         since_id=tweet.id).items(1000)
            for reply in reply_cursor:

                if hasattr(reply, "in_reply_to_status_id_str"):

                    if (reply.in_reply_to_status_id_str == tweet.id_str and
                            reply.author.screen_name != user):

                        reply_to_evaluate = re.sub("@[A-z0-9_]+|http\\S+", "", reply.full_text).strip()

                        if len(reply_to_evaluate) < 4:
                            reply_sentiment = None
                        else:
                            reply_sentiment = clf.predict(reply_to_evaluate)

                        replies_to.append([reply.author.screen_name, reply.full_text,
                                          reply.favorite_count, reply.retweet_count, reply_sentiment])

            sentiment_count = [replies_to[x][4] for x in range(0, len(replies_to))]

            if (len(replies_to) != 0) and (len(sentiment_count) > sentiment_count.count(None)):
                mean_sentiment = mean([replies_to[replies_to.index(x)][4] for x in replies_to
                                       if replies_to[replies_to.index(x)][4] is not None])
            else:
                mean_sentiment = None

            if tweet_sentiment is not None and mean_sentiment is not None:
                sentiment_difference = mean_sentiment - tweet_sentiment
            else:
                sentiment_difference = None

            data.append([tweet.full_text, tweet.created_at,
                         tweet.favorite_count, tweet.retweet_count, len(replies_to),
                         tweet_sentiment, mean_sentiment, sentiment_difference,
                         replies_to, tweet.id])

    data = sorted(data, key=lambda x: x[1], reverse=True)
    with open("jsons/tweets_replies_" + user + ".json", "w") as data_dump:
        json.dump(data, data_dump, default=datetime_to_str)
    return data


def tor_base(api, user, number_elements, data, trim=0, type_data="tweets", previous=False):

    if type_data is "replies":

        if previous is True:
            first_id = data[len(data) - 1][6]
            element_cursor = tweepy.Cursor(api.search, q="to:" + user, max_id=first_id, tweet_mode="extended").items(
                number_elements)
        else:

            if len(data) == 0:
                element_cursor = tweepy.Cursor(api.search, q="to:" + user, tweet_mode="extended").items(number_elements)
            else:
                last_id = data[0][6]
                element_cursor = tweepy.Cursor(api.search, q="to:" + user, since_id=last_id,
                                               tweet_mode="extended").items(number_elements)

        for element in element_cursor:

            if not element.retweeted and ("RT @" not in element.full_text):
                reply_to_evaluate = re.sub("@[A-z0-9_]+|http\\S+", "", element.full_text).strip()

                if len(reply_to_evaluate) < 4:
                    sentiment = None
                else:
                    sentiment = clf.predict(reply_to_evaluate)

                data.append([element.author.screen_name, element.full_text, element.created_at,
                             element.favorite_count, element.retweet_count, sentiment, element.id])

    else:

        if previous is True:
            first_id = data[len(data) - 1][6]
            element_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, max_id=first_id - 1,
                                           tweet_mode="extended").items(number_elements)
        else:

            if len(data) == 0:
                element_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, tweet_mode="extended").items(
                    number_elements)
            elif trim > 0:
                data = data[trim:]
                last_id = data[0][6]
                print("Trimming " + str(trim) + " tweets. Last tweet considered is " + data[0][1])
                element_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                               tweet_mode="extended").items(number_elements)
            else:
                last_id = data[0][6]
                element_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                               tweet_mode="extended").items(number_elements)

        for element in element_cursor:

            if not element.retweeted and ("RT @" not in element.full_text) and not element.full_text.startswith("@"):
                element_to_evaluate = re.sub("@[A-z0-9_]+|http\\S+", "", element.full_text).strip()

                if len(element_to_evaluate) < 4:
                    sentiment = None
                else:
                    sentiment = clf.predict(element_to_evaluate)

                data.append([element.author.screen_name, element.full_text, element.created_at,
                            element.favorite_count, element.retweet_count, sentiment, element.id])

    data = sorted(data, key=lambda x: x[2], reverse=True)
    with open("jsons/" + type_data + "_" + user + ".json", "w") as data_dump:
        json.dump(data, data_dump, default=datetime_to_str)
    return data


def datetime_to_str(data):
    if isinstance(data, datetime.datetime):
        return data.__str__()
