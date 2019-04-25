# Spanish Twitter Sentiment

This project uses [Tweepy](https://www.tweepy.org/) and Elliot Hofman's
[senti-py](https://github.com/aylliote/senti-py) sentiment classifier for
Spanish to evaluate average sentiment for a tweet's replies.

## Description of functions

* `twr(user_list, number_elements=10, trim=0,
previous=False, build=True)`: loads data if available and retrieves tweets for a
list of users and their associated replies. Evaluates sentiment for each
reply and for the tweet, and calculates net sentiment (mean reply sentiment
minus tweet sentiment). Saves a JSON file for each user.
    * `user_list`: list of Twitter user handles
    * `number_elements`: number of tweets to retrieve
    * `trim`: number of elements to remove from previously loaded data (useful
    if you believe that the data you already have needs updating)
    * `previous`: if set to `True` will retrieve elements prior to the earliest
    tweet ID in the data
    * `build`: if set to `True` will output a dictionary with a key for each
    user containing a list of every tweet and the associated data, and a
    Pandas dataframe

* `tor(user_list, number_elements=100, mean_obs=100, trim=0,
                            type_data="tweets", previous=False, build=True)`:
   loads data if available and retrieves tweets or replies for a list of users.
   Evaluates sentiment for each element. Saves a JSON file for each user.
    * `user_list`: list of Twitter user handles
    * `number_elements`: number of elements to retrieve
    * `mean_obs`: determines how many observations to use for calculating mean
    sentiment
    * `trim`: number of elements to remove from previously loaded data (useful
    if you believe that the data you already have needs updating)
    * `type_data`: whether to retrieve tweets for a user or replies to a user
    * `previous`: if set to `True` will retrieve elements prior to the earliest
    tweet ID in the data
   * `build`: if set to `True` will output a dictionary with a key for each user
   containing a list of every tweet or reply and the associated data, the mean
   sentiment for each user (either for their tweets or the replies made to them),
   and a Pandas dataframe

* `build_...`: auxiliary function for the above functions.

* `make_plots(user_list, data, type_data="tweets", start_date=None,
               end_date=None, window=7, spacing=7, operation="average")`:
               plots time series of tweets or replies retrieved by the
               `tweets_or_replies_users` function
    * `user_list`: list of Twitter users to plot
    * `data`: a Pandas dataframe output by the `tor`
               function
    * `type_data`: whether to plot tweets or replies
    * `start_date` and `end_date`: strings that define first and last date to plot
    * `window`: how many days to use for the rolling window
    * `spacing`: how many days to use for the x axis spacing (for readability)
    * `operation`: `sum`, `average` or `count`. Tweets can be used with sum and
    average, replies can be used with average and count.
     
## Limitations and solutions
Because the free Twitter search API tier is limited (only gets tweets more recent than 7 or so days, which is the only way to get replies to a particular user or tweet), each time a Tweepy function is used the results are saved to JSONs, which are used the next time the function is run. This is not ideal, but the best I could think of to circumvent this issue.