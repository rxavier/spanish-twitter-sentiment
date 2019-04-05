import tweepy
import pickle
import datetime
from statistics import mean
from classifier import SentimentClassifier

clf = SentimentClassifier()


def tweets_replies(api, user, num_tweets, tweets_data, trim, previous=False):
    if previous is True:
        first_id = tweets_data[len(tweets_data) - 1][1]
        tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, max_id=first_id - 1,
                                     tweet_mode="extended").items(num_tweets)
    else:
        if len(tweets_data) == 0:
            tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, tweet_mode="extended").items(num_tweets)
        elif trim > 0:
            tweets_data = tweets_data[trim:]
            last_id = tweets_data[0][1]
            print("Trimming " + str(trim) + " tweets. Last tweet considered is " + tweets_data[0][0])
            tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                         tweet_mode="extended").items(num_tweets)
        else:
            last_id = tweets_data[0][1]
            tweet_cursor = tweepy.Cursor(api.user_timeline, screen_name=user, since_id=last_id,
                                         tweet_mode="extended").items(num_tweets)
    for user_tweet in tweet_cursor:
        if not user_tweet.retweeted and ("RT @" not in user_tweet.full_text) and \
                ((datetime.datetime.utcnow() - user_tweet.created_at).days < 9):
            replies_list = []
            for reply_tweet in tweepy.Cursor(api.search, q="to:" + user, tweet_mode="extended",
                                             since_id=user_tweet.id).items(1000):
                if hasattr(reply_tweet, "in_reply_to_status_id_str"):
                    if (reply_tweet.in_reply_to_status_id_str == user_tweet.id_str and
                            reply_tweet.author.screen_name != user):
                        sentiment = clf.predict(reply_tweet.full_text)
                        replies_list.append([reply_tweet.author.screen_name, reply_tweet.full_text,
                                            reply_tweet.favorite_count, reply_tweet.retweet_count, sentiment])
            if len(replies_list) != 0:
                tweets_data.append([user_tweet.full_text, user_tweet.id, user_tweet.created_at,
                                    user_tweet.favorite_count, user_tweet.retweet_count, len(replies_list),
                                    replies_list, mean([replies_list[replies_list.index(x)][4] for x in replies_list])])
            else:
                tweets_data.append([user_tweet.full_text, user_tweet.id, user_tweet.created_at,
                                    user_tweet.favorite_count, user_tweet.retweet_count, len(replies_list),
                                    replies_list, None])
    with open("Pickles/tweets_replies_" + user + ".p", "wb") as data_dump:
        pickle.dump(tweets_data, data_dump)
    return tweets_data


def replies(api, user, num_tweets, replies_data, previous=False):
    if previous is True:
        first_id = replies_data[len(replies_data) - 1][2]
        reply_cursor = tweepy.Cursor(api.search, q="to:" + user, max_id=first_id, tweet_mode="extended").items(
            num_tweets)
    else:
        if len(replies_data) == 0:
            reply_cursor = tweepy.Cursor(api.search, q="to:" + user, tweet_mode="extended").items(num_tweets)
        else:
            last_id = replies_data[0][2]
            reply_cursor = tweepy.Cursor(api.search, q="to:" + user, since_id=last_id,
                                         tweet_mode="extended").items(num_tweets)
    for reply in reply_cursor:
        if not reply.retweeted and ("RT @" not in reply.full_text):
            sentiment = clf.predict(reply.full_text)
            replies_data.append([reply.author.screen_name, reply.full_text, reply.id, reply.created_at,
                                reply.favorite_count, reply.retweet_count, sentiment])
    with open("Pickles/replies_" + user + ".p", "wb") as data_dump:
        pickle.dump(replies_data, data_dump)
    return replies_data
