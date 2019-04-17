import tweepy
import datetime
import re
import json
from statistics import mean
from classifier import SentimentClassifier

clf = SentimentClassifier()


def user_data(api, user, num_tweets, tweets_replies_data, trim, previous=False):
    if previous is True:
        first_id = tweets_replies_data[len(tweets_replies_data) - 1][1]
        tweet_reply_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, max_id=first_id - 1,
                                           tweet_mode="extended").items(num_tweets)
    else:
        if len(tweets_replies_data) == 0:
            tweet_reply_cursor = tweepy.Cursor(api.user_timeline, screen_name=user,
                                               tweet_mode="extended").items(num_tweets)
        elif trim > 0:
            tweets_replies_data = tweets_replies_data[trim:]
            last_id = tweets_replies_data[0][1]
            print("Trimming " + str(trim) + " tweets. Last tweet considered is " + tweets_replies_data[0][0])
            tweet_reply_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                               tweet_mode="extended").items(num_tweets)
        else:
            last_id = tweets_replies_data[0][1]
            tweet_reply_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                               tweet_mode="extended").items(num_tweets)
    for user_tweet in tweet_reply_cursor:
        if not user_tweet.retweeted and ("RT @" not in user_tweet.full_text) and \
                ((datetime.datetime.utcnow() - user_tweet.created_at).days < 9) and \
                not user_tweet.full_text.startswith("@"):
            replies_list = []
            for reply_tweet in tweepy.Cursor(api.search, q="to:" + user, tweet_mode="extended",
                                             since_id=user_tweet.id).items(1000):
                if hasattr(reply_tweet, "in_reply_to_status_id_str"):
                    if (reply_tweet.in_reply_to_status_id_str == user_tweet.id_str and
                            reply_tweet.author.screen_name != user):
                        tweet_reply_to_evaluate = re.sub("@[A-z0-9_]+|http\\S+", "", reply_tweet.full_text).strip()
                        if len(tweet_reply_to_evaluate) < 4:
                            sentiment = None
                        else:
                            sentiment = clf.predict(tweet_reply_to_evaluate)
                        replies_list.append([reply_tweet.author.screen_name, reply_tweet.full_text,
                                            reply_tweet.favorite_count, reply_tweet.retweet_count, sentiment])
            sentiment_count = [replies_list[x][4] for x in range(0, len(replies_list))]
            if (len(replies_list) != 0) and (len(sentiment_count) > sentiment_count.count(None)):
                tweets_replies_data.append([user_tweet.full_text, user_tweet.id, user_tweet.created_at,
                                            user_tweet.favorite_count, user_tweet.retweet_count,
                                            len(replies_list), replies_list,
                                            mean([replies_list[replies_list.index(x)][4] for x in replies_list
                                                  if replies_list[replies_list.index(x)][4] is not None])])
            else:
                tweets_replies_data.append([user_tweet.full_text, user_tweet.id, user_tweet.created_at,
                                            user_tweet.favorite_count, user_tweet.retweet_count, len(replies_list),
                                            replies_list, None])
    with open("jsons/tweets_replies_" + user + ".json", "w") as data_dump:
        json.dump(sorted(tweets_replies_data, key=lambda x: x[2], reverse=True), data_dump, default=datetime_to_str)
    return tweets_replies_data


def tweets_replies(api, user, number_elements, data, trim=0, type_data="replies", previous=False):
    if type_data is "replies":
        if previous is True:
            first_id = data[len(data) - 1][2]
            reply_cursor = tweepy.Cursor(api.search, q="to:" + user, max_id=first_id, tweet_mode="extended").items(
                number_elements)
        else:
            if len(data) == 0:
                reply_cursor = tweepy.Cursor(api.search, q="to:" + user, tweet_mode="extended").items(number_elements)
            else:
                last_id = data[0][2]
                reply_cursor = tweepy.Cursor(api.search, q="to:" + user, since_id=last_id,
                                             tweet_mode="extended").items(number_elements)
        for reply in reply_cursor:
            if not reply.retweeted and ("RT @" not in reply.full_text):
                reply_to_evaluate = re.sub("@[A-z0-9_]+|http\\S+", "", reply.full_text).strip()
                if len(reply_to_evaluate) < 4:
                    sentiment = None
                else:
                    sentiment = clf.predict(reply_to_evaluate)
                data.append([reply.author.screen_name, reply.full_text, reply.id, reply.created_at,
                             reply.favorite_count, reply.retweet_count, sentiment])
        with open("jsons/replies_" + user + ".json", "w") as data_dump:
            json.dump(sorted(data, key=lambda x: x[2], reverse=True), data_dump, default=datetime_to_str)
        return data
    elif type_data is "tweets":
        if previous is True:
            first_id = data[len(data) - 1][1]
            tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, max_id=first_id - 1,
                                         tweet_mode="extended").items(number_elements)
        else:
            if len(data) == 0:
                tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, tweet_mode="extended").items(
                    number_elements)
            elif trim > 0:
                data = data[trim:]
                last_id = data[0][1]
                print("Trimming " + str(trim) + " tweets. Last tweet considered is " + data[0][0])
                tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                             tweet_mode="extended").items(number_elements)
            else:
                last_id = data[0][1]
                tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                             tweet_mode="extended").items(number_elements)
        for tweet in tweet_cursor:
            if not tweet.retweeted and ("RT @" not in tweet.full_text) and not tweet.full_text.startswith("@"):
                tweet_to_evaluate = re.sub("@[A-z0-9_]+|http\\S+", "", tweet.full_text).strip()
                if len(tweet_to_evaluate) < 4:
                    sentiment = None
                else:
                    sentiment = clf.predict(tweet_to_evaluate)
                data.append([tweet.full_text, tweet.id, tweet.created_at,
                            tweet.favorite_count, tweet.retweet_count, sentiment])
        with open("jsons/tweets_" + user + ".json", "w") as data_dump:
            json.dump(sorted(data, key=lambda x: x[2], reverse=True), data_dump, default=datetime_to_str)
        return data


def datetime_to_str(data):
    if isinstance(data, datetime.datetime):
        return data.__str__()
