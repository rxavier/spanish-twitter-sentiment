import tweepy
import pickle
import datetime
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
                        sentiment = clf.predict(reply_tweet.full_text)
                        replies_list.append([reply_tweet.author.screen_name, reply_tweet.full_text,
                                            reply_tweet.favorite_count, reply_tweet.retweet_count, sentiment])
            if len(replies_list) != 0:
                tweets_replies_data.append([user_tweet.full_text, user_tweet.id, user_tweet.created_at,
                                            user_tweet.favorite_count, user_tweet.retweet_count,
                                            len(replies_list), replies_list,
                                            mean([replies_list[replies_list.index(x)][4] for x in replies_list])])
            else:
                tweets_replies_data.append([user_tweet.full_text, user_tweet.id, user_tweet.created_at,
                                            user_tweet.favorite_count, user_tweet.retweet_count, len(replies_list),
                                            replies_list, None])
    with open("Pickles/tweets_replies_" + user + ".p", "wb") as data_dump:
        pickle.dump(sorted(tweets_replies_data, key=lambda x: x[2], reverse=True), data_dump)
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
                sentiment = clf.predict(reply.full_text)
                data.append([reply.author.screen_name, reply.full_text, reply.id, reply.created_at,
                             reply.favorite_count, reply.retweet_count, sentiment])
        with open("Pickles/replies_" + user + ".p", "wb") as data_dump:
            pickle.dump(sorted(data, key=lambda x: x[2], reverse=True), data_dump)
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
                sentiment = clf.predict(tweet.full_text)
                data.append([tweet.full_text, tweet.id, tweet.created_at,
                            tweet.favorite_count, tweet.retweet_count, sentiment])
        with open("Pickles/tweets_" + user + ".p", "wb") as data_dump:
            pickle.dump(sorted(data, key=lambda x: x[2], reverse=True), data_dump)
        return data
