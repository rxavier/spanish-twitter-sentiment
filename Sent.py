import tweepy
import sys
import pickle
from statistics import mean
from classifier import SentimentClassifier

clf = SentimentClassifier()


def sent_latest(api, user, num_tweets, data):
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    if len(data) == 0:
        tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, tweet_mode="extended",
                                     timeout=999999).items(num_tweets)
    else:
        last_id = data[0][1]
        tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                     tweet_mode="extended", timeout=999999).items(num_tweets)
    for user_tweet in tweet_cursor:
        if not user_tweet.retweeted and ("RT @" not in user_tweet.full_text):
            replies = []
            for reply_tweet in tweepy.Cursor(api.search, q="to:" + user, result_type='recent', tweet_mode="extended",
                                             since_id=user_tweet.id, timeout=999999).items(1000):
                if hasattr(reply_tweet, "in_reply_to_status_id_str"):
                    if reply_tweet.in_reply_to_status_id_str == user_tweet.id_str:
                        sentiment = clf.predict(reply_tweet.full_text)
                        replies.append([reply_tweet.author.screen_name, reply_tweet.full_text,
                                        reply_tweet.favorite_count, reply_tweet.retweet_count, sentiment])
            if len(replies) != 0:
                data.append([user_tweet.full_text.translate(non_bmp_map), user_tweet.id, user_tweet.created_at,
                             user_tweet.favorite_count, user_tweet.retweet_count, len(replies), replies,
                             mean([replies[replies.index(x)][4] for x in replies])])
            else:
                data.append([user_tweet.full_text.translate(non_bmp_map), user_tweet.id, user_tweet.created_at,
                             user_tweet.favorite_count, user_tweet.retweet_count, len(replies), replies, None])
    with open("Pickles/" + user + ".p", "wb") as data_dump:
        pickle.dump(data, data_dump)
    return data


def sent_previous(api, user, num_tweets, data):
    first_id = data[len(data)-1][1]
    tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, max_id=first_id-1,
                                 tweet_mode="extended", timeout=999999).items(num_tweets)
    for user_tweet in tweet_cursor:
        if not user_tweet.retweeted and ("RT @" not in user_tweet.full_text):
            replies = []
            for reply_tweet in tweepy.Cursor(api.search, q="to:" + user, result_type='recent', tweet_mode="extended",
                                             since_id=user_tweet.id, timeout=999999).items(1000):
                if hasattr(reply_tweet, "in_reply_to_status_id_str"):
                    if reply_tweet.in_reply_to_status_id_str == user_tweet.id_str:
                        sentiment = clf.predict(reply_tweet.full_text)
                        replies.append([reply_tweet.author.screen_name, reply_tweet.full_text,
                                        reply_tweet.favorite_count, reply_tweet.retweet_count, sentiment])
            if len(replies) != 0:
                data.append([user_tweet.full_text.translate(non_bmp_map), user_tweet.id, user_tweet.created_at,
                             user_tweet.favorite_count, user_tweet.retweet_count, len(replies), replies,
                             mean([replies[replies.index(x)][4] for x in replies])])
            else:
                data.append([user_tweet.full_text.translate(non_bmp_map), user_tweet.id, user_tweet.created_at,
                             user_tweet.favorite_count, user_tweet.retweet_count, len(replies), replies, None])
    with open("Pickles/" + user + ".p", "wb") as data_dump:
        pickle.dump(data, data_dump)
    return data
