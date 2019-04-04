import tweepy
import pickle
import datetime
from statistics import mean
from classifier import SentimentClassifier

clf = SentimentClassifier()


def sent_latest(api, user, num_tweets, data):
    if len(data) == 0:
        tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, tweet_mode="extended").items(num_tweets)
    else:
        last_id = data[0][1]
        tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                     tweet_mode="extended").items(num_tweets)
    for user_tweet in tweet_cursor:
        if not user_tweet.retweeted and ("RT @" not in user_tweet.full_text) and \
                ((datetime.datetime.utcnow() - user_tweet.created_at).days < 10):
            replies = []
            for reply_tweet in tweepy.Cursor(api.search, q="to:" + user, tweet_mode="extended",
                                             since_id=user_tweet.id).items(1000):
                if hasattr(reply_tweet, "in_reply_to_status_id_str"):
                    if (reply_tweet.in_reply_to_status_id_str == user_tweet.id_str and
                            reply_tweet.author.screen_name != user):
                        sentiment = clf.predict(reply_tweet.full_text)
                        replies.append([reply_tweet.author.screen_name, reply_tweet.full_text,
                                        reply_tweet.favorite_count, reply_tweet.retweet_count, sentiment])
            if len(replies) != 0:
                data.append([user_tweet.full_text, user_tweet.id, user_tweet.created_at,
                             user_tweet.favorite_count, user_tweet.retweet_count, len(replies), replies,
                             mean([replies[replies.index(x)][4] for x in replies])])
            else:
                data.append([user_tweet.full_text, user_tweet.id, user_tweet.created_at,
                             user_tweet.favorite_count, user_tweet.retweet_count, len(replies), replies, None])
    with open("Pickles/" + user + ".p", "wb") as data_dump:
        pickle.dump(data, data_dump)
    return data


def sent_previous(api, user, num_tweets, data):
    first_id = data[len(data)-1][1]
    tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, max_id=first_id-1,
                                 tweet_mode="extended").items(num_tweets)
    for user_tweet in tweet_cursor:
        if not user_tweet.retweeted and ("RT @" not in user_tweet.full_text) and \
                ((datetime.datetime.utcnow() - user_tweet.created_at).days < 10):
            replies = []
            for reply_tweet in tweepy.Cursor(api.search, q="to:" + user, tweet_mode="extended",
                                             since_id=user_tweet.id).items(1000):
                if hasattr(reply_tweet, "in_reply_to_status_id_str"):
                    if (reply_tweet.in_reply_to_status_id_str == user_tweet.id_str and
                            reply_tweet.author.screen_name != user):
                        sentiment = clf.predict(reply_tweet.full_text)
                        replies.append([reply_tweet.author.screen_name, reply_tweet.full_text,
                                        reply_tweet.favorite_count, reply_tweet.retweet_count, sentiment])
            if len(replies) != 0:
                data.append([user_tweet.full_text, user_tweet.id, user_tweet.created_at,
                             user_tweet.favorite_count, user_tweet.retweet_count, len(replies), replies,
                             mean([replies[replies.index(x)][4] for x in replies])])
            else:
                data.append([user_tweet.full_text, user_tweet.id, user_tweet.created_at,
                             user_tweet.favorite_count, user_tweet.retweet_count, len(replies), replies, None])
    with open("Pickles/" + user + ".p", "wb") as data_dump:
        pickle.dump(data, data_dump)
    return data
def replies_last(api, user, num_tweets, replies_data):
    if len(replies_data) == 0:
        reply_cursor = tweepy.Cursor(api.search, q="to:" + user, tweet_mode="extended").items(num_tweets)
    else:
        last_id = replies_data[0][2]
        reply_cursor = tweepy.Cursor(api.search, q="to:" + user, since_id=last_id,
                                     tweet_mode="extended").items(num_tweets)
    for reply in reply_cursor:
        sentiment = clf.predict(reply.full_text)
        replies_data.append([reply.author.screen_name, reply.full_text, reply.id, reply.created_at,
                            reply.favorite_count, reply.retweet_count, sentiment])
    with open("Pickles/replies_" + user + ".p", "wb") as data_dump:
        pickle.dump(replies_data, data_dump)
    return replies_data


def replies_previous(api, user, num_tweets, replies_data):
    first_id = replies_data[len(replies_data) - 1][2]
    reply_cursor = tweepy.Cursor(api.search, q="to:" + user, max_id=first_id, tweet_mode="extended").items(num_tweets)
    for reply in reply_cursor:
        sentiment = clf.predict(reply.full_text)
        replies_data.append([reply.author.screen_name, reply.full_text, reply.id, reply.created_at,
                            reply.favorite_count, reply.retweet_count, sentiment])
    with open("Pickles/replies_" + user + ".p", "wb") as data_dump:
        pickle.dump(replies_data, data_dump)
    return replies_data
